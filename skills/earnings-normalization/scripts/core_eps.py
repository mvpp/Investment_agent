#!/usr/bin/env python3
"""GAAP -> Core earnings bridge with audit controls, tax effects, recurrence evidence and core FCF.

Usage:
  python3 core_eps.py input.json            # markdown bridge + warnings
  python3 core_eps.py input.json --json     # machine-readable result

Exit code 2 = input errors: no core number is computed until they are fixed.

Input schema (see ../examples/core_eps_input.json):
{
  "company": "Meta Platforms", "ticker": "META", "period": "Q3-26", "unit": "USD M",
  "sector": "general",          # optional: bank | insurance | reit | commodity | retail | pharma | general
  "gaap": {
    "revenue":..., "operating_income":..., "pretax_income":..., "tax_expense":...,
    "earnings_to_common":...,   # DILUTED EPS NUMERATOR: net income attributable to common after
                                # preferred dividends, NCI and two-class/if-converted effects (EPS note)
    "diluted_shares":...,       # diluted weighted-average shares, same scale as money (e.g. millions)
    "reported_diluted_eps":..., # as filed; must tie to earnings_to_common / diluted_shares within $0.02
    "core_diluted_shares":...,  # optional: recomputed denominator (required when profit/loss status flips)
    "core_shares_method": "..." # required with core_diluted_shares
  },
  "revenue_adjustments": [{"event_id":..., "item":..., "amount": -500, "class":"R0", "source":...}],
  "adjustments": [
    {"event_id":"2026Q3-legal-AG", "item":..., "class":"R1", "category":"litigation",
     "level":"operating"|"non_operating", "pretax": 9890, "normal_pretax": 875,
     "tax_basis":"not_deductible", "tax_rate": 0.0,          # or "tax_effect" / "gross_tax_effect" (below)
     "alt_normal_pretax": 2500, "alt_label": "5-yr average", # optional second run-rate → sensitivity table
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
For R1/R3 the adjustment is the NET amount (pretax − normal_pretax) and tax applies to that
net amount. tax_rate is applied to the net; tax_effect is taken as the tax on the net. When the
filing discloses the tax on the GROSS charge, give it as `gross_tax_effect` (tax benefit the
filing reports for the whole charge, positive): the script applies its rate (gross_tax_effect ÷
pretax) to the net adjustment.
`alt_normal_pretax` (R1/R3): a second defensible run-rate (e.g. the forward run-rate vs the
5-yr average — adjustment-catalog §10). The bridge uses normal_pretax; the output adds core EPS
under each alternative and under all alternatives together.

Classes:
  R0  true one-off              -> remove fully
  R1  lumpy-recurring           -> replace with normal_pretax (multi-year run-rate)
  R2  recurring, labelled one-off -> NOT adjusted (listed for transparency).
      Add "investment": true for discretionary investment segments (e.g. Reality
      Labs, Other Bets) to also get a core-ex-investment EPS for SOTP work.
  R3  cyclical / macro-driven   -> replace with normal_pretax (mid-cycle level)
  TAX discrete tax item         -> remove after_tax amount; "tax_basis": "filing_specific" (default,
      amount disclosed) or "normalized_estimate" (you sized it — warned); for a recurring but volatile tax
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
  - A switch between GAAP profit and Core loss, or loss and profit, requires a recomputed diluted share count.
  - Sector overlays flag adjustments that are ordinary business in that sector.
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from evidence import number, positive, units, verify

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
    if sum(key in a for key in ("tax_rate", "tax_effect", "gross_tax_effect")) != 1:
        errors.append(f"'{name}': provide exactly one tax rate or effect.")
        return 0.0
    if "tax_effect" in a:
        tax = number(a["tax_effect"], "tax_effect")
    elif "gross_tax_effect" in a:
        if not a.get("pretax"):
            errors.append(f"'{name}': gross_tax_effect needs the gross pretax charge.")
            return 0.0
        tax = base * number(a["gross_tax_effect"], "gross_tax_effect") / float(a["pretax"])
    elif "tax_rate" in a:
        tax = base * number(a["tax_rate"], "tax_rate")
    else:
        errors.append(f"'{name}': give tax_rate, tax_effect or gross_tax_effect explicitly.")
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


def run(cfg, directory=".", require_evidence=False):
    try:
        units(cfg)
        if "quarters" in cfg:
            return ttm(cfg, directory, require_evidence)
        if "TTM" in str(cfg.get("period", "")).upper():
            raise ValueError("TTM requires four quarterly bridges in quarters")
        audit = verify(cfg, directory, require_evidence)
        result = quarter(cfg)
        if audit and not result["errors"]:
            result["evidence"] = audit
        return result
    except (ValueError, KeyError, TypeError, AttributeError, IndexError, OSError, ArithmeticError) as exc:
        return {"errors": [f"Invalid input: {exc}"], "warnings": []}


def ttm(cfg, directory, require_evidence):
    quarters = cfg["quarters"]
    if len(quarters) != 4:
        raise ValueError("TTM requires four consecutive quarters, oldest first")
    shares = positive(cfg["valuation_shares"], "valuation_shares")
    if "gaap" in cfg or "adjustments" in cfg or "revenue_adjustments" in cfg or "cash" in cfg:
        raise ValueError("put bridge inputs inside each quarter")
    if not cfg.get("unit") or not cfg.get("ticker"):
        raise ValueError("TTM requires one unit and ticker across quarters")
    results = []
    previous = None
    for q in quarters:
        start, end = (date.fromisoformat(q[k]) for k in ("period_start", "period_end"))
        if not 77 <= (end - start).days + 1 <= 105 or (previous and start != previous + timedelta(days=1)):
            raise ValueError("TTM quarters must be consecutive, non-overlapping fiscal quarters")
        previous = end
        inputs = {k: cfg[k] for k in ("company", "ticker", "unit", "shares_unit", "sector", "as_of", "has_nci") if k in cfg}
        for key in ("ticker", "unit", "shares_unit", "as_of"):
            if key in q and key in inputs and inputs[key] != q[key]:
                raise ValueError(f"TTM quarters must share {key}")
        if "quarters" in q:
            raise ValueError("nested TTM input")
        result = run({**inputs, "period": str(end), **q}, directory, require_evidence)
        if result["errors"]:
            raise ValueError(f"{end}: " + " / ".join(result["errors"]))
        results.append(result)
    elapsed_days = (previous - date.fromisoformat(quarters[0]["period_start"])).days + 1
    if not 364 <= elapsed_days <= 371:
        raise ValueError("four quarters must span a full fiscal year (52 or 53 weeks, or a calendar year)")
    agg = {}
    for basis in ("gaap", "core"):
        agg[basis] = {k: sum(r[basis][k] for r in results)
                      for k in ("eps", "earnings_to_common", "revenue", "operating_income")}
        if basis == "gaap":
            agg[basis]["eps"] = agg[basis]["reported_eps"] = sum(r[basis]["reported_eps"] for r in results)
        revenue = agg[basis]["revenue"]
        agg[basis]["op_margin"] = agg[basis]["operating_income"] / revenue if revenue else None
    if all("cash" in r for r in results):
        cash = {k: sum(r["cash"][k] for r in results)
                for k in ("reported_fcf", "core_cfo", "core_fcf", "core_fcf_after_sbc")}
        ni = agg["core"]["earnings_to_common"]
        cash["conversion"] = cash["core_fcf_after_sbc"] / ni if ni else None
        cash["fcf_after_sbc_per_share"] = sum(r["cash"]["fcf_after_sbc_per_share"] for r in results)
        agg["cash"] = cash
    if require_evidence or "as_of" in cfg or "evidence" in cfg:
        # Quarter facts retain their own fiscal dates. The outer fact is the valuation denominator.
        outer = {k: v for k, v in cfg.items() if k != "quarters"}
        if outer["period_start"] != quarters[0]["period_start"] or outer["period_end"] != quarters[-1]["period_end"]:
            raise ValueError("TTM evidence period must span the four quarters")
        agg["evidence"] = verify(outer, directory, True)
    return {**agg, "quarters": results, "valuation_shares": shares,
            "warnings": [w for r in results for w in r["warnings"]], "errors": []}


def quarter(cfg):
    g = cfg["gaap"]
    errors, warnings, lines = [], [], []
    required = ("revenue", "operating_income", "pretax_income", "tax_expense", "earnings_to_common", "diluted_shares", "reported_diluted_eps")
    for k in required:
        if k not in g:
            errors.append(f"gaap.{k} is required" + (" (the diluted EPS numerator from the EPS note, not consolidated net income)" if k == "earnings_to_common" else ""))
    if errors:
        return {"errors": errors, "warnings": warnings}

    for k in required:
        number(g[k], "gaap." + k)
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
    alts = []  # (name, label, after-tax change to core earnings if the alternative run-rate is used)
    nci_effect = 0.0
    seen_ids = set()
    operating_events = set()
    allocations = {}
    if type(cfg.get("has_nci", False)) is not bool:
        raise ValueError("has_nci must be boolean")
    if "as_of" in cfg and "has_nci" not in cfg:
        raise ValueError("dated earnings inputs require an explicit has_nci assessment")

    for a in cfg.get("adjustments", []):
        cls = a.get("class", "").upper()
        name = a.get("item", "?")
        src = a.get("source", "")
        eid = a.get("event_id")
        if cls not in EARNINGS_CHANGING | {"R2", "EST", "TAX"}:
            errors.append(f"'{name}': unknown adjustment class '{cls}'")
            continue
        level = a.get("level", "operating")
        if level not in ("operating", "non_operating"):
            errors.append(f"'{name}': invalid adjustment level")
        applies = cls in EARNINGS_CHANGING or cls == "TAX" or a.get("investment") or a.get("apply")
        if applies and cfg.get("has_nci") and "nci_fraction" not in a:
            errors.append(f"'{name}': provide the NCI fraction of this event's after-tax effect")
        nci = number(a.get("nci_fraction", 0), "nci_fraction")
        if not 0 <= nci <= 1:
            errors.append(f"'{name}': nci_fraction must be between 0 and 1")
        if not isinstance(eid, str) or not eid.strip():
            errors.append(f"'{name}': event_id is required (one id per economic event, reused wherever it appears).")
        elif eid in seen_ids:
            errors.append(f"'{name}': duplicate event_id '{eid}' — the same event is being booked twice.")
        else:
            seen_ids.add(eid)
        if not isinstance(src, str) or not src.strip():
            errors.append(f"'{name}': source is required (filing + note/page).")
        if any(w in name.lower() for w in SBC_WORDS) and cls in EARNINGS_CHANGING and not a.get("ipo_catch_up"):
            errors.append(f"'{name}': SBC is a recurring cost of doing business and cannot be removed (only a one-time IPO/acquisition catch-up may, with ipo_catch_up: true).")
        cat = a.get("category")
        if cat in rules and cls in ("R0", "R1"):
            warnings.append(f"'{name}' ({sector}): {rules[cat]}.")

        if cls == "TAX":
            amt = number(a["after_tax"], "after_tax")
            tb = a.get("tax_basis", "filing_specific")
            if tb not in ("filing_specific", "normalized_estimate"):
                errors.append(f"'{name}': TAX items take tax_basis filing_specific (amount disclosed) or normalized_estimate (sized by you).")
            elif tb == "normalized_estimate":
                warnings.append(f"'{name}': discrete tax item sized by estimate, not disclosed — mark it (E) in the memo and show EPS without it if material.")
            if "normal_after_tax" in a:  # recurring-but-volatile tax item (e.g. excess SBC tax benefits): remove only the excess
                check_recurrence(a, "TAX (normalized)", name, errors, warnings)
                amt = amt - a["normal_after_tax"]
            tax_items += amt
            nci_effect += amt * nci
            allocations[eid] = amt * nci
            lines.append((eid, name, cls + (" (vs normal)" if "normal_after_tax" in a else ""), None, None, None, amt * (1 - nci), src))
            if amt > 0:
                increase += 1
            elif amt < 0:
                decrease += 1
            continue

        pre = number(a["pretax"], "pretax") if applies else a.get("pretax", 0.0)
        if cls == "R2":
            if a.get("investment"):
                invest_after += (pre - tax_for(a, pre, name, errors, warnings)) * (1 - nci)
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
        allocations[eid] = (adj - tax) * nci
        nci_effect += allocations[eid]
        after = (adj - tax) * (1 - nci)
        if "alt_normal_pretax" in a and cls in ("R1", "R3"):
            d = a.get("normal_pretax", 0.0) - a["alt_normal_pretax"]  # alt adjustment − base adjustment
            rate = tax / adj if adj else float(a.get("tax_rate", 0.0))
            alts.append((name, a.get("alt_label", "alternative run-rate"), d * (1 - rate) * (1 - nci)))
        if level == "operating":
            if adj and eid:
                operating_events.add(eid)
            op_adj += adj
        else:
            nonop_adj += adj
        tax_on_adj += tax
        if adj > 0:
            increase += 1
        elif adj < 0:
            decrease += 1
        lines.append((eid, name, cls, pre, adj, tax, after, src))

    core_ni = e2c + (op_adj + nonop_adj - tax_on_adj) + tax_items - nci_effect
    revenue_ids = set()
    for row in cfg.get("revenue_adjustments", []):
        eid = row.get("event_id")
        if not isinstance(eid, str) or not eid.strip() or eid in revenue_ids:
            errors.append("Revenue adjustment needs a unique event_id")
        revenue_ids.add(eid)
        if row.get("class", "R0") not in EARNINGS_CHANGING:
            errors.append(f"{eid}: invalid revenue adjustment class")
        if not isinstance(row.get("source"), str) or not row["source"].strip():
            errors.append(f"{eid}: revenue adjustment needs a source")
        number(row["amount"], "revenue amount")
        if eid not in operating_events and not (isinstance(row.get("no_earnings_effect_reason"), str) and row["no_earnings_effect_reason"].strip()):
            errors.append(f"{eid}: link an operating adjustment or document zero earnings impact")
        if eid in operating_events and row.get("no_earnings_effect_reason"):
            errors.append(f"{eid}: zero-impact explanation conflicts with EBIT adjustment")
        if eid in seen_ids and eid not in operating_events and any(line[0] == eid and line[6] for line in lines):
            errors.append(f"{eid}: zero-impact explanation conflicts with earnings adjustment")
    core_shares = shares
    if "core_diluted_shares" in g:
        if not isinstance(g.get("core_shares_method"), str) or not g["core_shares_method"].strip():
            errors.append("gaap.core_shares_method is required with core_diluted_shares (how the recomputed denominator was built).")
        core_shares = positive(g["core_diluted_shares"], "core_diluted_shares")
    elif e2c >= 0 > core_ni and "basic_shares" in g:
        core_shares = positive(g["basic_shares"], "gaap.basic_shares")
    elif e2c >= 0 > core_ni:
        errors.append("GAAP profit turns into core loss: provide core_diluted_shares excluding anti-dilutive securities and core_shares_method.")
    elif e2c <= 0 < core_ni:
        errors.append("GAAP loss turns into core profit: the GAAP diluted count excludes anti-dilutive securities. "
                      "Provide core_diluted_shares (treasury method on options/RSUs, if-converted on converts) and core_shares_method.")

    if e2c < 0 < core_ni and core_shares < shares:
        errors.append("Core profit share count cannot be below the GAAP loss share count")
    if e2c >= 0 > core_ni and core_shares > shares:
        errors.append("Core loss share count cannot exceed the GAAP diluted count")
    if e2c >= 0 > core_ni and "basic_shares" in g and core_shares != positive(g["basic_shares"], "gaap.basic_shares"):
        errors.append("Use the basic weighted-average share count for a core loss")
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

    def supplemental_eps(earnings, label):
        if (earnings < 0) == (core_ni < 0):
            return earnings / core_shares
        if earnings < 0 and "basic_shares" in g:
            return earnings / positive(g["basic_shares"], "gaap.basic_shares")
        if (earnings < 0) == (e2c < 0):
            return earnings / shares
        warnings.append(f"{label}: EPS unavailable because the alternative changes dilution status and lacks a suitable denominator.")
        return None

    res = {
        "company": cfg.get("company"), "period": cfg.get("period"), "unit": cfg.get("unit", ""), "sector": sector,
        "gaap": {"revenue": g["revenue"], "operating_income": g["operating_income"], "earnings_to_common": e2c, "eps": gaap_eps,
                 "reported_eps": g["reported_diluted_eps"], "etr": gaap_etr, "op_margin": g["operating_income"] / g["revenue"] if g["revenue"] else None, "shares": shares},
        "core": {"revenue": core_rev, "operating_income": core_op, "earnings_to_common": core_ni, "eps": core_eps, "etr": core_etr,
                 "op_margin": core_op / core_rev if core_rev else None, "shares": core_shares},
        "nci_adjustment": nci_effect, "nci_by_event": allocations,
        "core_ex_investment_eps": supplemental_eps(core_ni + invest_after, "Ex-investment") if invest_after else None,
        "lines": lines, "errors": [], "warnings": warnings, "revenue_adjustments": cfg.get("revenue_adjustments", []),
        "alternatives": [{"item": n, "label": lb, "core_eps": supplemental_eps(core_ni + d, n)} for n, lb, d in alts]
                        + ([{"item": "all alternatives together", "label": "", "core_eps": supplemental_eps(core_ni + sum(d for *_, d in alts), "All alternatives")}] if len(alts) > 1 else []),
    }
    for x in res["alternatives"]:
        if x["core_eps"] is not None and abs(x["core_eps"] - core_eps) > 0.05 * abs(core_eps):
            warnings.append(f"Run-rate choice for '{x['item']}' moves core EPS by more than 5% ({core_eps:.2f} → {x['core_eps']:.2f}) — show both in the memo as a judgment call.")

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
            if c["capex"] > 2 * c["maintenance_capex"] and oe - (core_fcf - sbc) > 0.5 * abs(oe):
                warnings.append(f"Growth capex is {pct(cash['growth_capex'] / c['capex'])} of capex, so owner earnings ({oe / core_shares:,.2f}/sh) far exceed FCF after SBC "
                                f"({(core_fcf - sbc) / core_shares:,.2f}/sh). Owner earnings assume the growth capex earns at least its cost of capital — show both and say why that holds.")
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
    if "quarters" in r:
        out = ["## TTM earnings", "", "| Quarter | GAAP EPS (reported) | Core EPS | Core earnings to common | Core shares |",
               "|---|---|---|---|---|"]
        for q in r["quarters"]:
            out.append(f"| {q['period']} | {q['gaap']['reported_eps']:.2f} | {q['core']['eps']:.4f} | {q['core']['earnings_to_common']:,.2f} | {q['core']['shares']:,.2f} |")
        out += [f"| TTM | {r['gaap']['reported_eps']:.2f} | {r['core']['eps']:.2f} | {r['core']['earnings_to_common']:,.2f} | |",
                f"Valuation shares: {r['valuation_shares']:,.2f}"]
        out += [f"Core revenue: {r['core']['revenue']:,.2f} · Core operating margin: {pct(r['core']['op_margin'])}"]
        if "cash" in r:
            out.append(f"Core FCF after SBC: {r['cash']['core_fcf_after_sbc']:,.2f} · Cash conversion: {pct(r['cash']['conversion'])}")
        return "\n".join(out + [f"- {w}" for w in r["warnings"]])
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
    if r["nci_adjustment"]:
        out.append(f"| Adjustment allocated to NCI (after tax) | | {num(r['nci_adjustment'])} |")
    if r.get("core_ex_investment_eps") is not None:
        out.append(f"| Core EPS ex investment segments (SOTP input only — not a headline number) | | {num(r['core_ex_investment_eps'], 2)} |")
    if r["revenue_adjustments"]:
        out += ["", "Revenue adjustments: " + "; ".join(f"{x['item']} {num(x['amount'])} [{x.get('source', '')}]" for x in r["revenue_adjustments"])]
    if r.get("alternatives"):
        out += ["", "| Run-rate sensitivity | Core EPS |", "|---|---|", f"| Bridge as above | {num(cc['eps'], 2)} |"]
        out += [f"| {x['item']}{' — ' + x['label'] if x['label'] else ''} | {num(x['core_eps'], 2)} |" for x in r["alternatives"]]
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
    source = Path(sys.argv[1])
    try:
        cfg = json.loads(source.read_text())
        r = run(cfg, source.parent, "--require-evidence" in sys.argv)
    except (OSError, ValueError) as exc:
        r = {"errors": [str(exc)], "warnings": []}
    if "--json" in sys.argv:
        for bridge in r.get("quarters", [r]):
            bridge["lines"] = [dict(zip(["event_id", "item", "class", "pretax", "adjustment", "tax_effect", "after_tax", "source"], l)) for l in bridge.get("lines", [])]
        print(json.dumps(r, indent=1, default=float))
    else:
        print(render(r))
    sys.exit(2 if r.get("errors") else 0)


if __name__ == "__main__":
    main()
