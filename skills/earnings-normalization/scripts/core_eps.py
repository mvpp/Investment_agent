#!/usr/bin/env python3
"""GAAP -> Core earnings bridge with audit controls, tax effects, recurrence evidence and core FCF.

Usage:
  python3 core_eps.py input.json            # markdown bridge + warnings
  python3 core_eps.py input.json --json     # machine-readable result

Exit code 2 = input errors: no core number is computed until they are fixed.

Input schema (see ../examples/core_eps_input.json):
{
  "company": "Meta Platforms", "ticker": "META", "period": "TTM Q3-26", "unit": "USD M",
  "sector": "general",          # optional: bank | insurance | reit | commodity | retail | pharma | general
  "gaap": {
    "revenue":..., "operating_income":..., "pretax_income":..., "tax_expense":...,
    "earnings_to_common":...,   # DILUTED EPS NUMERATOR: net income attributable to common after
                                # preferred dividends, NCI and two-class/if-converted effects (EPS note)
    "diluted_shares":...,       # diluted weighted-average shares, same scale as money (e.g. millions)
    "reported_diluted_eps":..., # as filed; must tie to earnings_to_common / diluted_shares within $0.02
    "core_diluted_shares":...,  # optional: recomputed denominator (required if GAAP loss -> core profit)
    "core_shares_method": "..." # required with core_diluted_shares
  },
  "revenue_adjustments": [{"item":..., "amount": -500, "class":"R0", "source":...}],
  "adjustments": [
    {"event_id":"2026Q3-legal-AG", "item":..., "class":"R1", "category":"litigation",
     "level":"operating"|"non_operating", "pretax": 9890, "normal_pretax": 875,
     "tax_basis":"not_deductible", "tax_rate": 0.0,          # or "tax_effect": <incremental tax expense>
     "recurrence": {"quarters_reviewed": 12, "similar_events": 5, "assessment": "lumpy-recurring"},
     "source":"10-Q Q3-26, Note 8"},
    {"event_id":"2026Q1-tax-CAMT", "item":..., "class":"TAX", "after_tax": -8030, "source":...},
    {"event_id":"FY26-sbc-excess-tax", "item":"Excess tax benefit on RSU vesting", "class":"TAX",
     "after_tax": -6.1, "normal_after_tax": -3.8, "recurrence": {...}, "source":...},
    {"event_id":"RL-loss", "item":"Reality Labs op loss", "class":"R2", "investment": true,
     "pretax": 4400, "tax_basis":"jurisdiction_specific", "tax_rate": 0.17, "source":...}
  ],
  "cash": {"cfo":..., "capex":..., "finance_lease_principal":..., "sbc":...,
           "maintenance_capex": optional,
           "one_off_cash": [{"item":..., "amount": 1400, "source":...}]}
}

Sign convention: `pretax` / `after_tax` / `one_off_cash.amount` = how much the item
REDUCED reported earnings or CFO. Charges and payments are positive; gains and
windfalls are negative. For cash normalizations that LOWER core CFO (e.g. a cash-tax
holiday or an accrued-but-unpaid settlement whose run-rate cash cost must be charged),
the amount is negative. Revenue `amount` is what you add to reported revenue.
`tax_effect` = incremental income-tax EXPENSE caused by the adjustment (adding back a
deductible 100 charge at 21% -> +21; removing a taxable 100 gain -> -21).

Classes:
  R0  true one-off              -> remove fully
  R1  lumpy-recurring           -> replace with normal_pretax (multi-year run-rate)
  R2  recurring, labelled one-off -> NOT adjusted (listed for transparency).
      Add "investment": true for discretionary investment segments (e.g. Reality
      Labs, Other Bets) to also get a core-ex-investment EPS for SOTP work.
  R3  cyclical / macro-driven   -> replace with normal_pretax (mid-cycle level)
  TAX discrete tax item         -> remove after_tax amount; for a recurring but volatile tax
      item (excess SBC tax benefits, R3-like) add "normal_after_tax" (the multi-year normal
      level, same sign convention) plus recurrence evidence — only the excess is removed
  EST accounting-estimate change -> informational unless "apply": true; put the
      period's earnings uplift in `pretax` (negative = flattered earnings); optional.

Controls (errors stop the calculation; warnings need a sentence in the memo):
  - GAAP tie-out: earnings_to_common / diluted_shares vs reported diluted EPS (±$0.02).
  - Every adjustment has a unique event_id (the same charge appears in the income
    statement, cash-flow statement, footnotes and release — book it once).
  - Every earnings-changing item has an explicit tax_basis and tax_rate/tax_effect;
    no default rate. not_deductible / no_tax_effect must carry zero tax.
  - R0/R1/R3 items carry recurrence evidence (quarters reviewed, similar events, assessment).
  - GAAP loss -> core profit requires a recomputed diluted share count.
  - Sector overlays flag adjustments that are ordinary business in that sector.
"""
import json
import sys

SBC_WORDS = ("stock-based", "stock based", "share-based", "share based", "sbc", "equity comp")
TAX_BASES = {"filing_specific", "jurisdiction_specific", "normalized_estimate", "not_deductible", "no_tax_effect"}
EARNINGS_CHANGING = {"R0", "R1", "R3"}
TIE_TOLERANCE = 0.02

# sector -> {category: message}; fires when such a category is removed as a one-off (R0/R1)
SECTOR_RULES = {
    "bank": {"investment_gain_loss": "securities gains/losses are part of a bank's balance-sheet management",
             "credit_provision": "loan-loss provisions are a core operating cost — normalize to through-cycle credit cost (R3), don't remove",
             "hedge": "hedging results are ordinary for banks"},
    "insurance": {"investment_gain_loss": "investment results are core for insurers — use R3 normalization of realized gains, not removal",
                  "reserve_development": "reserve development recurs — normalize (R3), don't remove",
                  "catastrophe_loss": "cat losses are the product — replace with a normalized cat load (R3)"},
    "reit": {"property_depreciation": "use Nareit FFO/AFFO as a separate measure; don't add depreciation back inside Core EPS"},
    "commodity": {"commodity_price": "commodity price swings are core exposure — use a mid-cycle price (R3), not removal",
                  "hedge": "hedge gains/losses track commodity exposure — R3",
                  "inventory_valuation": "LIFO/LCM inventory effects recur with prices — R3"},
    "retail": {"store_closure": "store closures and lease impairments recur in retail — R1 run-rate at most",
               "lease_impairment": "lease impairments recur in retail — R1 run-rate at most"},
    "pharma": {"iprd_licensing": "acquired IPR&D / licensing payments are recurring pipeline investment for drug developers — R1/R2"},
}
SECTOR_NOTES = {
    "reit": "REIT: Core EPS is an audit bridge only — value on FFO/AFFO and NAV (sector-valuation real-assets playbook).",
    "bank": "Bank: pair Core EPS with ROTCE, normalized credit costs and CET1 — P/TBV is the primary valuation.",
    "insurance": "Insurer: pair Core EPS with cat-normalized combined ratio and ROE — P/B is the primary valuation.",
    "pharma": "Drug developer: if GAAP profit is absent or pipeline-driven, Core EPS is not a meaningful valuation base — use rNPV.",
}


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


AMT_DP = 0  # decimals for money amounts; render() sets 1 for small companies


def num(x, dp=None):
    if x is None:
        return ""
    return f"{x:,.{AMT_DP if dp is None else dp}f}"


def tax_for(a, base, name, errors, warnings):
    """Incremental tax expense for an adjustment of `base` pretax. Explicit only — no default rate."""
    basis = a.get("tax_basis")
    if basis not in TAX_BASES:
        errors.append(f"'{name}': tax_basis must be one of {sorted(TAX_BASES)} (no default tax rate).")
        return 0.0
    if "tax_effect" in a:
        tax = float(a["tax_effect"])
    elif "tax_rate" in a:
        tax = base * float(a["tax_rate"])
    else:
        errors.append(f"'{name}': give tax_rate or tax_effect explicitly.")
        return 0.0
    if basis in ("not_deductible", "no_tax_effect") and abs(tax) > 1e-9:
        errors.append(f"'{name}': tax_basis {basis} must carry zero tax.")
    if basis == "normalized_estimate":
        warnings.append(f"'{name}': tax effect is an analyst estimate — say so in the memo.")
    if base:
        implied = tax / base
        if implied < 0 or implied > 0.60:
            warnings.append(f"'{name}': implied tax rate {pct(implied)} is outside 0–60% — check sign and special tax effects.")
    return tax


def check_recurrence(a, cls, name, errors, warnings):
    rec = a.get("recurrence")
    if not isinstance(rec, dict):
        errors.append(f"'{name}': {cls} needs recurrence evidence {{quarters_reviewed, similar_events, assessment}}.")
        return
    q, n, assess = rec.get("quarters_reviewed"), rec.get("similar_events"), rec.get("assessment")
    if not isinstance(q, int) or isinstance(q, bool) or q < 0:
        errors.append(f"'{name}': recurrence.quarters_reviewed must be a non-negative integer.")
    elif q < 8:
        warnings.append(f"'{name}': only {q} prior quarters reviewed for recurrence (8+ recommended where available).")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        errors.append(f"'{name}': recurrence.similar_events must be a non-negative integer.")
    elif cls == "R0" and n >= 2:
        warnings.append(f"'{name}': R0 but {n} similar events found — recurring 'non-recurring' items should be R1 with a run-rate.")
    if not isinstance(assess, str) or not assess.strip():
        errors.append(f"'{name}': recurrence.assessment (one-line reasoning) is required.")
    elif cls == "R0" and "recurr" in assess.lower() and "non-recurr" not in assess.lower():
        warnings.append(f"'{name}': assessed as recurring yet removed as R0 — reclassify or justify.")


def run(cfg):
    g = cfg["gaap"]
    errors, warnings, lines = [], [], []
    for k in ("revenue", "operating_income", "pretax_income", "tax_expense", "earnings_to_common", "diluted_shares", "reported_diluted_eps"):
        if k not in g:
            errors.append(f"gaap.{k} is required" + (" (the diluted EPS numerator from the EPS note, not consolidated net income)" if k == "earnings_to_common" else ""))
    if errors:
        return {"errors": errors, "warnings": warnings}

    e2c, shares = g["earnings_to_common"], g["diluted_shares"]
    if shares <= 0:
        errors.append("gaap.diluted_shares must be positive.")
        return {"errors": errors, "warnings": warnings}
    gaap_eps = e2c / shares
    if abs(gaap_eps - g["reported_diluted_eps"]) > TIE_TOLERANCE:
        errors.append(f"GAAP tie-out fails: earnings_to_common / diluted_shares = {gaap_eps:.4f} vs reported diluted EPS {g['reported_diluted_eps']} "
                      f"(tolerance ±{TIE_TOLERANCE}). Check the numerator (preferred dividends, NCI, two-class), units and period.")

    sector = (cfg.get("sector") or "general").lower()
    rules = SECTOR_RULES.get(sector, {})
    if sector in SECTOR_NOTES:
        warnings.append(SECTOR_NOTES[sector])

    op_adj = nonop_adj = tax_on_adj = tax_items = 0.0
    increase = decrease = 0
    invest_after = 0.0  # after-tax losses of discretionary investment segments (SOTP aid only)
    seen_ids = set()

    for a in cfg.get("adjustments", []):
        cls = a.get("class", "R0").upper()
        name = a.get("item", "?")
        src = a.get("source", "")
        eid = a.get("event_id")
        if not eid:
            errors.append(f"'{name}': event_id is required (one id per economic event, reused wherever it appears).")
        elif eid in seen_ids:
            errors.append(f"'{name}': duplicate event_id '{eid}' — the same event is being booked twice.")
        else:
            seen_ids.add(eid)
        if not src:
            errors.append(f"'{name}': source is required (filing + note/page).")
        if any(w in name.lower() for w in SBC_WORDS) and cls in EARNINGS_CHANGING and not a.get("ipo_catch_up"):
            errors.append(f"'{name}': SBC is a recurring cost of doing business and cannot be removed (only a one-time IPO/acquisition catch-up may, with ipo_catch_up: true).")
        cat = a.get("category")
        if cat in rules and cls in ("R0", "R1"):
            warnings.append(f"'{name}' ({sector}): {rules[cat]}.")

        if cls == "TAX":
            amt = a["after_tax"]
            if "normal_after_tax" in a:  # recurring-but-volatile tax item (e.g. excess SBC tax benefits): remove only the excess
                check_recurrence(a, "TAX (normalized)", name, errors, warnings)
                amt = amt - a["normal_after_tax"]
            tax_items += amt
            lines.append((eid, name, cls + (" (vs normal)" if "normal_after_tax" in a else ""), None, None, None, amt, src))
            if amt > 0:
                increase += 1
            elif amt < 0:
                decrease += 1
            continue

        pre = a.get("pretax", 0.0)
        if cls == "R2":
            if a.get("investment"):
                invest_after += pre - tax_for(a, pre, name, errors, warnings)
            lines.append((eid, name, cls + (" (investment)" if a.get("investment") else ""), pre, 0.0, 0.0, 0.0, src))
            continue
        if cls == "EST" and not a.get("apply"):
            lines.append((eid, name, cls + " (info)", pre, 0.0, 0.0, 0.0, src))
            continue
        if cls in EARNINGS_CHANGING:
            check_recurrence(a, cls, name, errors, warnings)
        if cls in ("R1", "R3"):
            if "normal_pretax" not in a:
                errors.append(f"'{name}': {cls} needs normal_pretax (run-rate / mid-cycle level).")
            elif pre > 0 and a["normal_pretax"] > pre:
                warnings.append(f"'{name}': run-rate {a['normal_pretax']:,} exceeds the reported charge {pre:,} — the adjustment lowers earnings; confirm the run-rate basis.")
            adj = pre - a.get("normal_pretax", 0.0)
        else:  # R0 or applied EST
            adj = pre
        tax = tax_for(a, adj, name, errors, warnings)
        after = adj - tax
        if a.get("level", "operating") == "operating":
            op_adj += adj
        else:
            nonop_adj += adj
        tax_on_adj += tax
        if adj > 0:
            increase += 1
        elif adj < 0:
            decrease += 1
        lines.append((eid, name, cls, pre, adj, tax, after, src))

    core_ni = e2c + (op_adj + nonop_adj - tax_on_adj) + tax_items
    core_shares = shares
    if "core_diluted_shares" in g:
        if not g.get("core_shares_method"):
            errors.append("gaap.core_shares_method is required with core_diluted_shares (how the recomputed denominator was built).")
        core_shares = g["core_diluted_shares"]
    elif e2c < 0 < core_ni:
        errors.append("GAAP loss turns into core profit: the GAAP diluted count excludes anti-dilutive securities. "
                      "Provide core_diluted_shares (treasury method on options/RSUs, if-converted on converts) and core_shares_method.")

    if errors:
        return {"errors": errors, "warnings": warnings}

    rev_adj = sum(r["amount"] for r in cfg.get("revenue_adjustments", []))
    core_rev = g["revenue"] + rev_adj
    core_op = g["operating_income"] + op_adj
    core_pretax = g["pretax_income"] + op_adj + nonop_adj
    core_tax = g["tax_expense"] + tax_on_adj - tax_items
    core_eps = core_ni / core_shares
    core_etr = core_tax / core_pretax if core_pretax else None
    gaap_etr = g["tax_expense"] / g["pretax_income"] if g["pretax_income"] else None
    rel = abs(core_ni - e2c) / abs(e2c) if e2c else None

    if rel is not None and rel > 0.20:
        warnings.append(f"Net adjustments move earnings by {pct(rel)} — the bridge carries the thesis; double-check each large item against the filing text.")
    if increase >= 2 and decrease == 0:
        warnings.append("Every adjustment raises earnings. Look for gains to remove too (investment marks, asset sales, reserve releases, tax benefits, one-off revenue).")
    if core_etr is not None and not (0.08 <= core_etr <= 0.30):
        warnings.append(f"Core effective tax rate {pct(core_etr)} looks abnormal — check discrete tax items and the tax on adjustments.")

    res = {
        "company": cfg.get("company"), "period": cfg.get("period"), "unit": cfg.get("unit", ""), "sector": sector,
        "gaap": {"revenue": g["revenue"], "operating_income": g["operating_income"], "earnings_to_common": e2c, "eps": gaap_eps,
                 "reported_eps": g["reported_diluted_eps"], "etr": gaap_etr, "op_margin": g["operating_income"] / g["revenue"], "shares": shares},
        "core": {"revenue": core_rev, "operating_income": core_op, "earnings_to_common": core_ni, "eps": core_eps, "etr": core_etr,
                 "op_margin": core_op / core_rev, "shares": core_shares},
        "core_ex_investment_eps": (core_ni + invest_after) / core_shares if invest_after else None,
        "lines": lines, "errors": [], "warnings": warnings, "revenue_adjustments": cfg.get("revenue_adjustments", []),
    }

    c = cfg.get("cash")
    if c:
        one_off = sum(x["amount"] for x in c.get("one_off_cash", []))
        flp = c.get("finance_lease_principal", 0.0)
        core_cfo = c["cfo"] + one_off
        fcf = c["cfo"] - c["capex"] - flp
        core_fcf = core_cfo - c["capex"] - flp
        sbc = c.get("sbc", 0.0)
        cash = {"reported_fcf": fcf, "core_cfo": core_cfo, "core_fcf": core_fcf, "core_fcf_after_sbc": core_fcf - sbc,
                "fcf_per_share": core_fcf / core_shares, "fcf_after_sbc_per_share": (core_fcf - sbc) / core_shares,
                "conversion": (core_fcf - sbc) / core_ni if core_ni else None, "one_off_cash": c.get("one_off_cash", [])}
        if "maintenance_capex" in c:
            oe = core_cfo - c["maintenance_capex"] - flp - sbc
            cash["owner_earnings"] = oe
            cash["owner_earnings_per_share"] = oe / core_shares
            cash["growth_capex"] = c["capex"] - c["maintenance_capex"]
        conv = cash["conversion"]
        if conv is not None and conv < 0.5:
            warnings.append(f"FCF-after-SBC / core earnings is {pct(conv)} (<50%) — explain it in the memo (capex cycle, working capital, cash taxes) or treat earnings quality as low.")
        if "finance_lease_principal" not in c:
            warnings.append("No finance-lease principal given — data-center / equipment-heavy filers fund capex through finance leases; check the financing section.")
        res["cash"] = cash
    return res


def render(r):
    global AMT_DP
    if r.get("errors"):
        out = ["## Input errors — core EPS not computed", ""] + [f"- {e}" for e in r["errors"]]
        if r.get("warnings"):
            out += ["", "Warnings so far:"] + [f"- {w}" for w in r["warnings"]]
        return "\n".join(out)
    u = r["unit"]
    AMT_DP = 1 if abs(r["gaap"]["earnings_to_common"]) < 1000 else 0
    out = [f"## Core earnings bridge — {r['company']} {r['period']} ({u})", ""]
    out += ["| Event | Item | Class | Reported (pretax) | Adjustment (pretax) | Tax effect | After-tax to earnings | Source |", "|---|---|---|---|---|---|---|---|"]
    out.append(f"| | **GAAP earnings to common (diluted numerator)** | | | | | **{num(r['gaap']['earnings_to_common'])}** | |")
    for eid, name, cls, pre, adj, tax, after, src in r["lines"]:
        out.append(f"| {eid or ''} | {name} | {cls} | {num(pre)} | {num(adj)} | {num(tax)} | {num(after)} | {src} |")
    out.append(f"| | **Core earnings to common** | | | | | **{num(r['core']['earnings_to_common'])}** | |")
    out += ["", "| Metric | GAAP | Core |", "|---|---|---|"]
    gg, cc = r["gaap"], r["core"]
    out.append(f"| Revenue | {num(gg['revenue'])} | {num(cc['revenue'])} |")
    out.append(f"| Operating income | {num(gg['operating_income'])} | {num(cc['operating_income'])} |")
    out.append(f"| Operating margin | {pct(gg['op_margin'])} | {pct(cc['op_margin'])} |")
    out.append(f"| Effective tax rate | {pct(gg['etr'])} | {pct(cc['etr'])} |")
    out.append(f"| Earnings to common | {num(gg['earnings_to_common'])} | {num(cc['earnings_to_common'])} |")
    out.append(f"| Diluted shares | {num(gg['shares'], 1)} | {num(cc['shares'], 1)} |")
    out.append(f"| Diluted EPS (GAAP tie-out: reported {gg['reported_eps']}) | {num(gg['eps'], 2)} | **{num(cc['eps'], 2)}** |")
    if r.get("core_ex_investment_eps"):
        out.append(f"| Core EPS ex investment segments (SOTP input only — not a headline number) | | {num(r['core_ex_investment_eps'], 2)} |")
    if r["revenue_adjustments"]:
        out += ["", "Revenue adjustments: " + "; ".join(f"{x['item']} {num(x['amount'])} [{x.get('source', '')}]" for x in r["revenue_adjustments"])]
    if "cash" in r:
        c = r["cash"]
        out += ["", "| Cash metric | Value |", "|---|---|"]
        out.append(f"| Reported FCF (CFO − capex − finance-lease principal) | {num(c['reported_fcf'])} |")
        out.append(f"| Core CFO (ex one-off cash items) | {num(c['core_cfo'])} |")
        out.append(f"| Core FCF | {num(c['core_fcf'])} |")
        out.append(f"| Core FCF after SBC | {num(c['core_fcf_after_sbc'])} |")
        out.append(f"| Core FCF after SBC / share | {num(c['fcf_after_sbc_per_share'], 2)} |")
        out.append(f"| FCF-after-SBC / core earnings (conversion) | {pct(c['conversion'])} |")
        if "owner_earnings" in c:
            out.append(f"| Owner earnings (core CFO − maint. capex − leases − SBC) | {num(c['owner_earnings'])} |")
            out.append(f"| Owner earnings / share | {num(c['owner_earnings_per_share'], 2)} |")
            out.append(f"| Growth capex (capex − maintenance) | {num(c['growth_capex'])} |")
        if c["one_off_cash"]:
            out.append("")
            out.append("One-off cash items: " + "; ".join(f"{x['item']} {num(x['amount'])} [{x.get('source', '')}]" for x in c["one_off_cash"]))
    if r["warnings"]:
        out += ["", "### Warnings"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cfg = json.load(open(sys.argv[1]))
    r = run(cfg)
    if "--json" in sys.argv:
        r["lines"] = [dict(zip(["event_id", "item", "class", "pretax", "adjustment", "tax_effect", "after_tax", "source"], l)) for l in r.get("lines", [])]
        print(json.dumps(r, indent=1, default=float))
    else:
        print(render(r))
    sys.exit(2 if r.get("errors") else 0)


if __name__ == "__main__":
    main()
