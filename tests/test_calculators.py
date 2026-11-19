import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1] / "skills"
EARN = ROOT / "earnings-normalization"
VAL = ROOT / "sector-valuation"
CORE = EARN / "scripts/core_eps.py"
VALUATION = VAL / "scripts/valuation.py"
MEMO = ROOT / "investment-memo/scripts/memo_check.py"


def read(path):
    return json.loads(path.read_text())


def run(*args):
    return subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True)


def quarter(income=100, shares=100):
    return {"gaap": {"revenue": 600, "operating_income": 200, "pretax_income": 180, "tax_expense": 40,
                     "earnings_to_common": income, "diluted_shares": shares, "reported_diluted_eps": income / shares}}


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write(self, data, name="input.json"):
        path = self.dir / name
        path.write_text(json.dumps(data))
        return path

    def calc(self, cmd, data, ok=True, *flags):
        args = [VALUATION, cmd] if cmd else [CORE]
        proc = run(*args, self.write(data), "--json", *flags)
        if ok:
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            return json.loads(proc.stdout)
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("Traceback", proc.stderr)
        if cmd:
            self.assertFalse(proc.stdout.strip())
        else:
            self.assertNotIn("core", json.loads(proc.stdout))
        return proc.stdout + proc.stderr

    def meta(self):
        shutil.copytree(EARN / "examples/meta-q3-2025", self.dir / "meta-q3-2025")
        return read(EARN / "examples/core_eps_input.json")

    def test_meta_golden(self):
        cfg = self.meta()
        actual = self.calc(None, cfg, True, "--require-evidence")
        self.assertEqual(round(actual["gaap"]["eps"], 2), 1.05)
        self.assertEqual(round(actual["core"]["eps"], 2), 6.96)
        self.assertAlmostEqual(actual["core"]["earnings_to_common"], 17910.62)
        self.assertEqual(actual["cash"]["reported_fcf"], 10625)
        self.assertEqual(actual["evidence"]["documents"]["release"]["accession"], "0001628280-25-047114")
        cfg["adjustments"] = cfg["adjustments"][:1]
        self.assertEqual(round(self.calc(None, cfg)["core"]["eps"], 2), 7.25)

    def test_evidence_as_of_and_input_drift(self):
        cfg = self.meta()
        self.assertIn("postdates", self.calc(None, {**cfg, "as_of": "2025-10-28"}, False))
        cfg["gaap"]["operating_income"] += 1
        self.assertIn("differs", self.calc(None, cfg, False))
        self.assertIn("evidence", self.calc(None, quarter(), False, "--require-evidence"))

    def test_evidence_period_unit_column_and_snapshot(self):
        cfg = self.meta()
        path = self.dir / cfg["evidence"]
        original = read(path)
        for key, change, message in [("column", 3, "fiscal period"), ("unit", "USD_B", "USD_M"),
                                     ("source_location", "Other income", "row label")]:
            with self.subTest(key=key):
                manifest = read(path)
                manifest["facts"]["/gaap/revenue"][key] = change
                path.write_text(json.dumps(manifest))
                self.assertIn(message, self.calc(None, cfg, False))
                path.write_text(json.dumps(original))
        (path.parent / "exhibit-99-1-extract.txt").write_text("altered")
        self.assertIn("checksum", self.calc(None, cfg, False))

    def test_ttm_changing_shares(self):
        starts = ["2025-01-01", "2025-04-01", "2025-07-01", "2025-10-01"]
        ends = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]
        quarters = [dict(quarter(shares=shares), period_start=start, period_end=end,
                         cash={"cfo": 150, "capex": 40, "finance_lease_principal": 10, "sbc": 20})
                    for start, end, shares in zip(starts, ends, [100, 100, 200, 200])]
        cfg = {"period": "TTM", "ticker": "DEMO", "unit": "USD M", "valuation_shares": 230, "quarters": quarters}
        out = self.calc(None, cfg)
        self.assertEqual(out["core"]["eps"], 3)
        self.assertEqual(out["core"]["earnings_to_common"], 400)
        self.assertEqual(out["valuation_shares"], 230)
        self.assertAlmostEqual(out["gaap"]["etr"], 160 / 720)
        self.assertAlmostEqual(out["core"]["etr"], 160 / 720)
        self.assertAlmostEqual(out["cash"]["fcf_after_sbc_per_share"], 80 / 100 * 2 + 80 / 200 * 2)
        self.assertAlmostEqual(out["cash"]["fcf_after_sbc_per_valuation_share"], 320 / 230)
        md = run(CORE, self.write(cfg)).stdout
        self.assertIn("Core ETR: 22.2%", md)
        self.assertIn("FCF after SBC / share: 2.40", md)
        quarters[0] = quarters[1]
        self.assertIn("consecutive", self.calc(None, cfg, False))
        self.calc(None, dict(quarter(), period="TTM"), False)

    def test_evidence_dollar_parentheses_and_cli(self):
        import hashlib
        cfg = self.meta()
        manifest_path = self.dir / cfg["evidence"]
        extract_path = manifest_path.parent / "exhibit-99-1-extract.txt"
        raw_text = extract_path.read_text()
        for fmt in ["($18,829)", "$(18,829)", "-$18,829"]:
            with self.subTest(fmt=fmt):
                modified = raw_text.replace("(18,829)", fmt)
                extract_path.write_text(modified)
                manifest = read(manifest_path)
                manifest["documents"]["release"]["sha256"] = hashlib.sha256(modified.encode()).hexdigest()
                manifest_path.write_text(json.dumps(manifest))
                actual = self.calc(None, cfg, True, "--require-evidence")
                self.assertEqual(actual["cash"]["reported_fcf"], 10625)
        extract_path.write_text(raw_text)
        ev_script = EARN / "scripts/evidence.py"
        insp = run(ev_script, "--inspect", extract_path, "--json")
        self.assertEqual(insp.returncode, 0, insp.stderr)
        insp_data = json.loads(insp.stdout)
        self.assertEqual(insp_data["snapshot"], "exhibit-99-1-extract.txt")
        scaf = run(ev_script, "--scaffold", EARN / "examples/core_eps_input.json", "--extract", extract_path)
        self.assertEqual(scaf.returncode, 0, scaf.stderr)
        scaf_data = json.loads(scaf.stdout)
        self.assertEqual(scaf_data["facts"]["/gaap/revenue"]["line"], 10)
        self.assertEqual(scaf_data["facts"]["/cash/capex"]["factor"], -1)
        self.assertEqual(scaf_data["facts"]["/adjustments/2/pretax"]["event_id"], "2025Q3-RL-loss")

    def test_agents_skills_symlink(self):
        agents_skills = ROOT.parent / ".agents/skills"
        for name in ("earnings-normalization", "sector-valuation", "investment-memo", "us-industry-deepdive"):
            self.assertTrue((agents_skills / name / "SKILL.md").is_file(), f"missing {name}/SKILL.md via .agents/skills")

    def test_revenue_and_nci(self):
        cfg = quarter()
        rev = {"event_id": "sale", "item": "sale", "amount": -60, "source": "contract note"}
        cfg["revenue_adjustments"] = [rev]
        self.assertIn("link an operating adjustment", self.calc(None, cfg, False))
        rev["no_earnings_effect_reason"] = "Equal pass-through expense is reversed in the same note."
        self.assertEqual(self.calc(None, cfg)["core"]["operating_income"], 200)
        del rev["no_earnings_effect_reason"]
        cfg["has_nci"] = True
        event = {"event_id": "sale", "item": "sale", "class": "R0", "level": "operating", "pretax": -40,
                 "tax_rate": .2, "tax_basis": "filing_specific", "source": "contract note",
                 "recurrence": {"quarters_reviewed": 8, "similar_events": 0, "assessment": "isolated"}}
        cfg["adjustments"] = [event]
        self.assertIn("NCI", self.calc(None, cfg, False))
        event["nci_fraction"] = .25
        out = self.calc(None, cfg)
        self.assertEqual(out["nci_adjustment"], -8)
        self.assertEqual(out["core"]["earnings_to_common"], 76)
        self.assertAlmostEqual(out["core"]["op_margin"], 160 / 540)
        event["class"] = "typo"
        self.assertIn("unknown", self.calc(None, cfg, False))

    def test_sign_crossings_and_bad_shares(self):
        for start, adjustment, shares in [(100, -150, 80), (-100, 150, 110)]:
            cfg = quarter(start)
            cfg["adjustments"] = [{"event_id": "tax", "item": "tax", "source": "note", "class": "TAX", "after_tax": adjustment}]
            self.assertIn("core_diluted_shares", self.calc(None, cfg, False))
            cfg["gaap"].update(core_diluted_shares=0, core_shares_method="EPS note")
            self.assertIn("positive", self.calc(None, cfg, False))
            cfg["gaap"]["core_diluted_shares"] = shares
            self.assertAlmostEqual(self.calc(None, cfg)["core"]["eps"], (start + adjustment) / shares)

    def test_probability_and_terminal_inputs(self):
        for probs in [[.3, .3, .3], [-.2, 1.2], [], [float("nan")], [True]]:
            self.calc("scenarios", {"price": 100, "scenarios": [{"prob": p, "value": 100} for p in probs]}, False)
        cfg = read(VAL / "examples/dcf.json")
        for changes in [{"wacc": .03}, {"terminal_roic": 0}, {"unit": None}, {"shares_unit": None}, {"terminal_roic": .02}, {"diluted_shares": 0},
                        {"unit": "USD B", "shares_unit": "M"}, {"capital_actions": [{"shares": -3000}]}]:
            self.calc("dcf", {**cfg, **changes}, False)

    def test_terminal_reinvestment(self):
        cfg = read(VAL / "examples/dcf_capex.json")
        r = self.calc("dcf", cfg)
        rec = r["terminal_reinvestment_reconciliation"]
        self.assertAlmostEqual(rec["schedule_reinvestment"], rec["capex"] - rec["da"] + rec["delta_nwc"])
        self.assertAlmostEqual(rec["schedule_tv"], (rec["nopat"] - rec["schedule_reinvestment"]) / (r["wacc"] - r["g"]))
        self.assertTrue(any("reinvestment gap" in w for w in r["warnings"]))
        cfg["terminal_roic"] = cfg["terminal_growth"] * rec["nopat"] / rec["schedule_reinvestment"]
        tied = self.calc("dcf", cfg)
        self.assertAlmostEqual(tied["tv"], tied["terminal_reinvestment_reconciliation"]["schedule_tv"])
        self.assertFalse(any("reinvestment gap" in w for w in tied["warnings"]))

    def test_horizon_target(self):
        model = read(VAL / "examples/dcf.json")
        model.update(years=3, growth=.1, ebit_margin=.25, mid_year=False)
        self.write(model, "model.json")
        scenario = {"name": "base", "prob": 1, "dcf": "model.json",
                    "horizon_bridge": {"net_cash": 50, "other_claims": 5, "diluted_shares": 3000}}
        cfg = {"unit": "USD M", "price": 100, "years": 2, "cost_of_equity": .1, "scenarios": [scenario]}
        out = self.calc("scenarios", cfg)
        dcf = self.calc("dcf", model)
        expected = ((dcf["rows"][2]["fcff"] + dcf["tv"]) / (1 + model["wacc"]) + 45) / 3000
        self.assertAlmostEqual(out["fundamentals_based_target"], expected)
        self.assertAlmostEqual(out["required_return_rolled_target"], dcf["per_share"] * 1.1**2)
        self.assertEqual(out["expected_value"], out["fundamentals_based_target"])
        del scenario["horizon_bridge"]
        rolled = self.calc("scenarios", cfg)
        self.assertIsNone(rolled["fundamentals_based_target"])
        self.assertEqual(rolled["expected_value"], rolled["required_return_rolled_target"])
        scenario["horizon_bridge"] = {"net_cash": 0}
        self.calc("scenarios", cfg, False)

    def test_dated_scenario_checks_linked_model(self):
        scenario = {"unit": "USD M", "ticker": "DEMO", "period_start": "2025-01-01",
                    "period_end": "2025-03-31", "as_of": "2025-05-01", "evidence": "scenario-evidence.json",
                    "price": 50, "years": 1, "cost_of_equity": .10,
                    "scenarios": [{"name": "base", "prob": 1, "dcf": "dcf.json",
                                   "horizon_bridge": {"net_cash": 0, "diluted_shares": 20}}]}
        def manifest(cfg, items):
            facts = {key: {"value": val, "unit": unit, "evidence_type": "estimate", "confidence": "low",
                           "method": "Synthetic test assumption", "estimate_date": cfg["as_of"]}
                     for key, val, unit in items}
            return {**{k: cfg[k] for k in ("ticker", "period_start", "period_end")}, "facts": facts}

        self.write(manifest(scenario, [("/price", 50, "USD/share"), ("/years", 1, "years"),
                   ("/cost_of_equity", .1, "ratio"), ("/scenarios/0/prob", 1, "ratio"),
                   ("/scenarios/0/horizon_bridge/net_cash", 0, "USD_M"),
                   ("/scenarios/0/horizon_bridge/diluted_shares", 20, "shares_M")]), scenario["evidence"])
        model = {k: scenario[k] for k in ("ticker", "unit", "period_start", "period_end", "as_of")}
        model.update(shares_unit="M", years=2, revenue0=100, growth=.05, ebit_margin=.25, wacc=.1,
                     terminal_growth=.02, diluted_shares=20, evidence="model-evidence.json")
        self.write(manifest(model, [("/years", 2, "years"), ("/revenue0", 100, "USD_M"),
                   ("/growth", .05, "ratio"), ("/ebit_margin", .25, "ratio"), ("/wacc", .1, "ratio"),
                   ("/terminal_growth", .02, "ratio"), ("/diluted_shares", 20, "shares_M")]), model["evidence"])
        self.write(model, "dcf.json")
        result = self.calc("scenarios", scenario, True, "--require-evidence")
        self.assertEqual(result["rows"][0]["dcf_evidence"]["as_of"], scenario["as_of"])
        self.write({**model, "as_of": "2025-05-02"}, "dcf.json")
        self.assertIn("later as_of", self.calc("scenarios", scenario, False))
        del model["evidence"]
        self.write(model, "dcf.json")
        self.assertIn("manifest required", self.calc("scenarios", scenario, False))

    def test_loss_uses_basic_shares_and_parent_tax(self):
        cfg = quarter()
        cfg.update(has_nci=True, adjustments=[{"event_id": "tax", "item": "tax", "source": "tax note",
                   "class": "TAX", "after_tax": -200, "nci_fraction": .2}])
        cfg["gaap"]["basic_shares"] = 80
        r = self.calc(None, cfg)
        self.assertEqual(r["core"]["eps"], -.75)
        self.assertEqual(r["core"]["shares"], 80)
        self.assertEqual(r["nci_adjustment"], -40)
        self.assertAlmostEqual(r["core"]["etr"], 240 / 180)

    def test_memo_swaps(self):
        calc = self.write({"expected_value": 120, "fair_value_today": 100, "action_price": 80})
        memo = self.dir / "memo.md"
        body = ("Rating Buy · 截至 2025-10-29\n{}\n\n## Thesis and consensus\n## Key forces\n## Competitive position\n"
                "## Core EPS\n## Valuation\n## Risks\n## Kill conditions\n- Growth below 2% by 2026\n"
                "- Margin below 3% by 2026\n## Monitoring\n## Sources\n")
        for header, ok in [("Target (3 yr): $120 · Fair value today $100 · Action price ≤ $80", True),
                           ("目标价 $120 · 公允价值 $100 · 买入价 $80", True),
                           ("Target $80 · Fair value today $100 · Action price $120", False),
                           ("Target $100 · Fair value today $120 · Action price $80", False)]:
            memo.write_text(body.format(header))
            result = run(MEMO, memo, "--calc", calc)
            self.assertEqual(result.returncode, 0 if ok else 1, result.stdout)
            if not ok:
                self.assertIn("Header target", result.stdout)

    def test_down_year_capital_release(self):
        base = {"unit": "USD M", "shares_unit": "M", "revenue0": 1000, "years": 3, "growth": [.1, -.2, .05],
                "ebit_margin": .2, "tax_rate": .2, "wacc": .1, "terminal_growth": .02, "diluted_shares": 100}
        s2c = self.calc("dcf", {**base, "sales_to_capital": 2})
        self.assertAlmostEqual(s2c["rows"][0]["reinvestment"], 50)
        self.assertEqual(s2c["rows"][1]["reinvestment"], 0)  # no capital released by default
        released = self.calc("dcf", {**base, "sales_to_capital": 2, "sales_to_capital_down": 4})
        self.assertAlmostEqual(released["rows"][1]["reinvestment"], -220 / 4)
        self.assertTrue(any("sales_to_capital_down" in w for w in released["warnings"]))
        capex = {**base, "capex_pct": .05, "ebitda_margin": .25, "asset_life": 5}
        for nwc, extra, expected in [(.1, {}, 0), (-.1, {}, 22), (.1, {"nwc_pct_down": .05}, -11)]:
            r = self.calc("dcf", {**capex, "nwc_pct": nwc, **extra})
            row = r["rows"][1]
            self.assertAlmostEqual(row["reinvestment"] - (row["capex"] - row["da"]), expected)

    def payout_cfg(self, price, mid_year=True, **bridge):
        model = {"unit": "USD M", "shares_unit": "M", "revenue0": 1000, "years": 5, "growth": .05, "ebit_margin": .2, "mid_year": mid_year,
                 "tax_rate": .2, "sales_to_capital": 2, "wacc": .1, "terminal_growth": .02, "net_cash": 100, "diluted_shares": 100}
        self.write(model, "model.json")
        return {"unit": "USD M", "price": price, "years": 3, "cost_of_equity": .1, "hurdle": .15,
                "scenarios": [{"name": "Base", "prob": 1, "dcf": "model.json", "horizon_bridge": bridge}]}

    def test_payout_bridge(self):
        # Buybacks at intrinsic value are neutral against cash that earns the cost of capital.
        kept = self.calc("scenarios", self.payout_cfg(20, False, buyback_share=0, cash_yield=.1))
        neutral = self.calc("scenarios", self.payout_cfg(20, False, buyback_share=1, cash_yield=.1, repurchase_price="intrinsic"))
        self.assertAlmostEqual(neutral["expected_value"], kept["expected_value"])
        none = self.calc("scenarios", self.payout_cfg(20, buyback_share=0))
        row = none["rows"][0]
        dcf = self.calc("dcf", read(self.dir / "model.json"))
        self.assertAlmostEqual(row["horizon_net_cash"], 100 + sum(r["fcff"] for r in dcf["rows"][:3]))
        self.assertEqual(row["horizon_diluted_shares"], 100)
        cheap = self.calc("scenarios", self.payout_cfg(10, buyback_share=1))
        dear = self.calc("scenarios", self.payout_cfg(40, buyback_share=1))
        self.assertGreater(cheap["rows"][0]["buyback_value_effect"], 0)
        self.assertLess(dear["rows"][0]["buyback_value_effect"], 0)
        self.assertTrue(any("destroy" in w for w in dear["warnings"]))
        first = cheap["rows"][0]["payout_schedule"][0]
        self.assertAlmostEqual(first["repurchase_price"], 10 * 1.1)
        self.assertAlmostEqual(first["shares_end"], 100 - first["fcff"] / 11)
        self.assertAlmostEqual(first["net_cash_end"], 100)
        self.calc("scenarios", self.payout_cfg(20, buyback_share=.5, net_cash=0), False)
        self.calc("scenarios", self.payout_cfg(20, buyback_share=.8, dividend_share=.3), False)
        legacy = self.calc("scenarios", self.payout_cfg(20, net_cash=0, diluted_shares=100))
        self.assertTrue(any("prefer payout mode" in w for w in legacy["warnings"]))

    def test_margin_of_safety_rule(self):
        cfg = {"price": 100, "years": 3, "cost_of_equity": .1, "scenarios": [{"name": "Base", "prob": 1, "value_today": 100}]}
        for mos, expected in [({"quality": "A", "cyclical": True, "policy_exposure": .3}, .35),
                              ({"quality": "A", "cyclical": True, "policy_exposure": .2}, .25),
                              ({"quality": "C", "cyclical": True, "policy_exposure": .5, "net_debt_ebitda": 4}, .5),
                              ({"quality": "B"}, .25), (.2, .2)]:
            r = self.calc("scenarios", {**cfg, "margin_of_safety": mos})
            self.assertAlmostEqual(r["mos"], expected)
        d = self.calc("scenarios", {**cfg, "margin_of_safety": {"quality": "D"}})
        self.assertIsNone(d["action_price"])
        self.assertEqual(d["rating"], "Avoid")
        self.calc("scenarios", {**cfg, "margin_of_safety": {"quality": "E"}}, False)

    def test_rating_rows_and_weights(self):
        def scen(price, values, probs=(.25, .5, .25), **extra):
            rows = [{"name": n, "prob": p, "value_today": v} for n, p, v in zip(("Bear", "Base", "Bull"), probs, values)]
            return self.calc("scenarios", {"price": price, "years": 3, "cost_of_equity": .1, "hurdle": .15,
                                           "margin_of_safety": .15, "scenarios": rows, **extra})
        cases = [(60, (50, 100, 200), {}, "Buy", 2),
                 (60, (50, 100, 200), {"rating_flags": {"kill_near": True}}, "Avoid (watchlist, near miss)", 3),
                 (60, (50, 100, 200), {"rating_flags": {"kill_near": True, "owned": True}}, "Hold", 3),
                 (95, (80, 100, 125), {}, "Avoid (watchlist)", 4),
                 (130, (80, 100, 140), {"rating_flags": {"owned": True}}, "Trim", 5),
                 (60, (50, 100, 200), {"rating_flags": {"thesis_broken": True, "owned": True}}, "Sell", 1)]
        for price, values, extra, rating, row in cases:
            with self.subTest(rating=rating):
                r = scen(price, values, **extra)
                self.assertEqual((r["rating"], r["rating_row"]), (rating, row))
        self.assertTrue(any("weight_basis" in w for w in scen(95, (80, 100, 125), (.5, .3, .2))["warnings"]))
        skewed = scen(95, (80, 100, 125), (.5, .3, .2), weight_basis="bear-skewed: debt-funded customer capex")
        self.assertFalse(any("weight_basis" in w for w in skewed["warnings"]))

    def test_memo_rating_tie(self):
        calc = self.write({"expected_value": 120, "fair_value_today": 100, "action_price": 80, "rating": "Avoid (watchlist)"})
        memo = self.dir / "memo.md"
        body = ("# Target-rich environment\n{} · 截至 2025-10-29\nTarget (3 yr): $120 · Fair value today $100 · Action price ≤ $80\n\n"
                "## Thesis and consensus\n## Key forces\n## Competitive position\n## Core EPS\n## Valuation\n## Risks\n"
                "## Kill conditions\n- Growth below 2% by 2026\n- Margin below 3% by 2026\n## Monitoring\n## Sources\n")
        for rating, ok in [("**Rating: AVOID (watchlist)**", True), ("评级：回避（观察名单）", True),
                           ("Rating: Buy", False), ("Rating: Avoid", False)]:
            memo.write_text(body.format(rating))
            result = run(MEMO, memo, "--calc", calc)
            self.assertEqual(result.returncode, 0 if ok else 1, result.stdout)

    def test_all_valuation_examples(self):
        for fp in sorted((VAL / "examples").glob("*.json")):
            cmd = fp.stem.split("_")[0]
            for flags in [[], ["--json"]]:
                with self.subTest(file=fp.name, flags=flags):
                    result = run(VALUATION, cmd, fp, *flags)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
