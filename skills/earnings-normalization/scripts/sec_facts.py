#!/usr/bin/env python3
"""Pull standardized financials from SEC XBRL companyfacts.

Prints annual, discrete-quarter and TTM values for the line items that matter
for earnings normalization (P&L, one-off candidates, cash flow, balance sheet).
Discrete quarters missing from the filings (Q4, and cash-flow Q2/Q3 that are
only reported year-to-date) are derived by differencing YTD values.

Usage:
  python3 sec_facts.py META
  python3 sec_facts.py --cik 1326801 --years 5 --quarters 8
  python3 sec_facts.py META --json > meta_facts.json

SEC asks automated clients to identify themselves. Set SEC_USER_AGENT, e.g.
  export SEC_USER_AGENT="Your Name your@email.com"
Ticker lookup (www.sec.gov) rejects anonymous agents; use --cik if it fails.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_UA = "InvestmentMemoSkill/0.1 (personal research)"

# (key, label, kind, [tags in priority order])
# kind: flow = additive duration item, per = non-additive duration item (EPS,
# share counts), inst = balance-sheet instant.
ITEMS = [
    ("revenue", "Revenue", "flow", ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"]),
    ("cogs", "Cost of revenue", "flow", ["CostOfRevenue", "CostOfGoodsAndServicesSold"]),
    ("rnd", "R&D", "flow", ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"]),
    ("sm", "Sales & marketing", "flow", ["SellingAndMarketingExpense"]),
    ("ga", "G&A", "flow", ["GeneralAndAdministrativeExpense"]),
    ("op_income", "Operating income", "flow", ["OperatingIncomeLoss"]),
    ("nonop", "Non-operating inc/(exp)", "flow", ["NonoperatingIncomeExpense", "OtherNonoperatingIncomeExpense"]),
    ("pretax", "Pretax income", "flow", ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic"]),
    ("tax", "Income tax expense (total)", "flow", ["IncomeTaxExpenseBenefit"]),
    ("net_income", "Net income", "flow", ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"]),
    ("eps_dil", "EPS diluted ($)", "per", ["EarningsPerShareDiluted"]),
    ("sh_dil", "Diluted shares (M)", "per", ["WeightedAverageNumberOfDilutedSharesOutstanding"]),
    # one-off candidates
    ("sbc", "Stock-based comp", "flow", ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"]),
    ("restructuring", "Restructuring", "flow", ["RestructuringCharges", "RestructuringCosts", "RestructuringSettlementAndImpairmentProvisions", "RestructuringCostsAndAssetImpairmentCharges"]),
    ("gw_impair", "Goodwill impairment", "flow", ["GoodwillImpairmentLoss"]),
    ("asset_impair", "Asset impairment", "flow", ["AssetImpairmentCharges", "ImpairmentOfLongLivedAssetsHeldForUse", "ImpairmentOfIntangibleAssetsExcludingGoodwill"]),
    ("legal", "Litigation/legal", "flow", ["LitigationSettlementExpense", "LossContingencyLossInPeriod", "LossContingencyAccrualProvision"]),
    ("inv_gain", "Gain/(loss) on investments", "flow", ["GainLossOnInvestments", "EquitySecuritiesFvNiGainLoss", "EquitySecuritiesFvNiUnrealizedGainLoss", "MarketableSecuritiesRealizedGainLoss"]),
    ("asset_sale", "Gain/(loss) on asset sales", "flow", ["GainLossOnDispositionOfAssets", "GainLossOnSaleOfPropertyPlantEquipment", "GainLossOnSaleOfBusiness"]),
    ("debt_extinguish", "Gain/(loss) debt extinguishment", "flow", ["GainsLossesOnExtinguishmentOfDebt"]),
    ("deferred_tax", "Deferred tax exp/(benefit)", "flow", ["DeferredIncomeTaxExpenseBenefit"]),
    ("cash_tax", "Cash taxes paid", "flow", ["IncomeTaxesPaidNet", "IncomeTaxesPaid"]),
    # cash flow
    ("da", "D&A", "flow", ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet", "Depreciation"]),
    ("cfo", "Cash from operations", "flow", ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]),
    ("capex", "Capex", "flow", ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"]),
    ("fin_lease", "Finance lease principal", "flow", ["FinanceLeasePrincipalPayments"]),
    ("acquisitions", "Acquisitions (cash)", "flow", ["PaymentsToAcquireBusinessesNetOfCashAcquired"]),
    ("buybacks", "Buybacks", "flow", ["PaymentsForRepurchaseOfCommonStock"]),
    ("dividends", "Dividends paid", "flow", ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"]),
    # balance sheet
    ("cash", "Cash & equivalents", "inst", ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]),
    ("securities", "Marketable securities", "inst", ["MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "ShortTermInvestments"]),
    ("debt_lt", "Long-term debt", "inst", ["LongTermDebtNoncurrent", "LongTermDebt"]),
    ("debt_st", "Short-term debt", "inst", ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"]),
    ("fin_lease_liab", "Finance lease liabilities", "inst", ["FinanceLeaseLiability", "FinanceLeaseLiabilityNoncurrent"]),
    ("op_lease_liab", "Operating lease liabilities", "inst", ["OperatingLeaseLiability"]),
    ("legal_accrual", "Legal accruals (balance)", "inst", ["LossContingencyAccrualAtCarryingValue", "LossContingencyAccrualCurrent"]),
    ("preferred", "Preferred / temporary equity", "inst", ["PreferredStockValue", "TemporaryEquityCarryingAmountAttributableToParent"]),
    ("contract_liab", "Contract liabilities (customer advances)", "inst", ["ContractWithCustomerLiabilityCurrent", "ContractWithCustomerLiability"]),
    ("contract_assets", "Contract assets (unbilled)", "inst", ["ContractWithCustomerAssetNetCurrent", "ContractWithCustomerAssetNet"]),
    ("receivables", "Accounts receivable", "inst", ["AccountsReceivableNetCurrent"]),
    ("inventory", "Inventory", "inst", ["InventoryNet"]),
    ("equity", "Shareholders' equity", "inst", ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]),
    ("assets", "Total assets", "inst", ["Assets"]),
]
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "40-F"}


def fetch(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def lookup_cik(ticker, ua):
    try:
        data = fetch("https://www.sec.gov/files/company_tickers.json", ua)
    except urllib.error.HTTPError as e:
        sys.exit(f"Ticker lookup failed ({e.code}). Set SEC_USER_AGENT='Name email' or pass --cik.")
    for row in data.values():
        if row["ticker"].upper() == ticker.upper():
            return int(row["cik_str"]), row["title"]
    sys.exit(f"Ticker {ticker} not found in SEC list; pass --cik.")


def d(s):
    return dt.date.fromisoformat(s)


SPLIT_RATIOS = (1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 15, 20, 25, 30, 40, 50, 100)


def detect_splits(gaap):
    """Find stock splits from the same period reported before and after a split (filers restate
    share counts and EPS in later comparatives). Returns [(ratio, boundary_filed_date)]: values
    filed before `boundary` are on the pre-split basis. Reverse splits give ratio < 1."""
    found = {}
    for tag in ("WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"):
        node = gaap.get(tag)
        if not node or "shares" not in node["units"]:
            continue
        groups = {}
        for f in node["units"]["shares"]:
            if f.get("form") in FORMS and f.get("val"):
                groups.setdefault((f.get("start"), f["end"]), []).append((f["filed"], f["val"]))
        for obs in groups.values():
            obs.sort()
            for (f0, v0), (f1, v1) in zip(obs, obs[1:]):
                r = v1 / v0
                for c in SPLIT_RATIOS:
                    for cand in (c, 1 / c):
                        if abs(r / cand - 1) < 0.03:
                            k = round(cand, 4)
                            lo, hi = found.get(k, ("0000", "9999"))
                            found[k] = (max(lo, f0), min(hi, f1))
        if found:
            break
    return sorted(((k, hi) for k, (lo, hi) in found.items() if lo < hi), key=lambda x: x[1])


def split_factor(splits, filed):
    f = 1.0
    for ratio, boundary in splits:
        if filed < boundary:
            f *= ratio
    return f


def _anchor(end):
    """52/53-week filers end periods on a weekday near month end (e.g. 2026-01-03 for a
    'December' year). Shifting back 7 days maps the period to the month it really closes."""
    a = d(end) - dt.timedelta(days=7)
    return a.year, a.month


def fiscal_year(end, fye_month):
    y, m = _anchor(end)
    return y if m <= fye_month else y + 1


def fiscal_label(end, fye_month):
    """'FY26 Q1' style label for a quarter ending on `end` given the fiscal-year-end month."""
    y, m = _anchor(end)
    q = ((m - fye_month - 1) % 12) // 3 + 1
    return f"FY{fiscal_year(end, fye_month) % 100:02d} Q{q}"


def facts_for(gaap, tags, kind, splits=(), is_eps=False):
    """Merge facts across tags without mixing definitions in the same window: the tag
    with the most recent data is primary; other tags only fill periods that end before
    the primary tag's history starts (filers switch tags over the years).
    Returns {(start, end): (val, tag)} for duration items, {end: (val, tag)} for instants."""
    per_tag = []
    for prio, tag in enumerate(tags):
        node = gaap.get(tag)
        if not node:
            continue
        units = node["units"]
        unit = "USD" if "USD" in units else ("USD/shares" if "USD/shares" in units else ("shares" if "shares" in units else next(iter(units))))
        best = {}
        for f in units[unit]:
            if f.get("form") not in FORMS:
                continue
            key = f["end"] if kind == "inst" else (f.get("start"), f["end"])
            if kind != "inst" and not f.get("start"):
                continue
            val = f["val"]
            if kind == "per" and splits:  # put pre-split share counts / EPS on today's basis
                fac = split_factor(splits, f["filed"])
                val = val / fac if is_eps else val * fac
            # keep the most recently filed value (captures restatements)
            if key not in best or f["filed"] > best[key][2]:
                best[key] = (val, tag, f["filed"])
        if best:
            end_of = (lambda k: k) if kind == "inst" else (lambda k: k[1])
            per_tag.append((max(end_of(k) for k in best), -prio, best, end_of))
    out, floor = {}, None
    for _, _, best, end_of in sorted(per_tag, key=lambda x: (x[0], x[1]), reverse=True):
        for k, v in best.items():
            if floor is None or end_of(k) < floor:
                out.setdefault(k, (v[0], v[1]))
        first = min(end_of(k) for k in best)
        floor = first if floor is None else min(floor, first)
    if kind == "per" and not is_eps and len(out) >= 3:
        # filers occasionally tag share counts in thousands; repair values ~1000x below the median
        med = sorted(v[0] for v in out.values())[len(out) // 2]
        for k, (v, tag) in list(out.items()):
            if v and med and 0.5 < v * 1000 / med < 2:
                out[k] = (v * 1000, tag + " (x1000 scale fix)")
    return out


def discrete_quarters(periods, additive):
    """periods: {(start,end): (val, tag)} -> {end: (val, tag, derived)} for ~quarter durations."""
    q = {}
    for (s, e), (v, tag) in periods.items():
        days = (d(e) - d(s)).days
        if 80 <= days <= 100:
            q[e] = (v, tag, False)
    if not additive:
        return q
    # derive from cumulative periods sharing a start date
    by_start = {}
    for (s, e), (v, tag) in periods.items():
        by_start.setdefault(s, []).append((e, v, tag))
    for s, lst in by_start.items():
        lst.sort()
        for i in range(1, len(lst)):
            e_prev, v_prev, _ = lst[i - 1]
            e, v, tag = lst[i]
            if 80 <= (d(e) - d(e_prev)).days <= 100 and e not in q:
                q[e] = (v - v_prev, tag, True)
    return q


def annual(periods):
    a = {}
    for (s, e), (v, tag) in periods.items():
        if 350 <= (d(e) - d(s)).days <= 380:
            a[e] = (v, tag, s)
    return a


def scale(key, v):
    if v is None:
        return None
    if key == "eps_dil":
        return round(v, 2)
    return round(v / 1e6, 1)


def build(cik, ua, n_years, n_q):
    data = fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", ua)
    gaap = data["facts"].get("us-gaap", {})
    splits = detect_splits(gaap)
    rows, year_ends, q_ends = {}, set(), set()
    for key, label, kind, tags in ITEMS:
        p = facts_for(gaap, tags, kind, splits, is_eps=(key == "eps_dil"))
        if kind == "inst":
            rows[key] = {"label": label, "kind": kind, "inst": {e: v for e, v in p.items()}}
            continue
        a = annual(p)
        q = discrete_quarters(p, additive=(kind == "flow"))
        rows[key] = {"label": label, "kind": kind, "annual": a, "quarter": q}
        if key in ("revenue", "net_income"):
            year_ends.update(a)
            q_ends.update(q)
    derive_q4_per_share(rows)
    years = sorted(year_ends)[-n_years:]
    quarters = sorted(q_ends)[-n_q:]
    months = [_anchor(e)[1] for e in year_ends]
    fye = max(set(months), key=months.count) if months else 12
    meta = {"splits": splits, "fye_month": fye}
    return data.get("entityName", ""), rows, years, quarters, meta


def derive_q4_per_share(rows):
    """Q4 diluted shares from the day-weighted identity FY_avg x FY_days = sum(q_avg x q_days)
    (handles 14-week quarters in 53-week years); Q4 EPS = Q4 NI / Q4 shares."""
    sh, eps, ni = rows["sh_dil"], rows["eps_dil"], rows["net_income"]
    for fy_end, (fy_sh, tag, fy_start) in sh["annual"].items():
        if fy_end in sh["quarter"]:
            continue
        qe = sorted(e for e in sh["quarter"] if 0 < (d(fy_end) - d(e)).days < 300)
        if len(qe) == 3:
            bounds = [fy_start] + qe + [fy_end]
            days = [(d(b) - d(a)).days for a, b in zip(bounds, bounds[1:])]
            days[0] += 1  # fiscal start date is the first day of Q1
            q4 = (fy_sh * sum(days) - sum(sh["quarter"][e][0] * n for e, n in zip(qe, days[:3]))) / days[3]
            sh["quarter"][fy_end] = (q4, tag, True)
            if fy_end not in eps["quarter"] and fy_end in ni["quarter"] and q4 > 0:
                eps["quarter"][fy_end] = (ni["quarter"][fy_end][0] / q4, "derived NI/shares", True)


def ttm_eps(rows, quarters):
    if len(quarters) < 4:
        return None
    ni = ttm(rows["net_income"], quarters)
    sh = [rows["sh_dil"]["quarter"].get(e) for e in quarters[-4:]]
    if ni is None or any(v is None for v in sh):
        return None
    return ni / (sum(v[0] for v in sh) / 4)


def etr_line(rows, years, quarters, fye=12):
    """Effective tax rate per period; flags periods that need a read of the tax note
    (outside 5–35%, or >8 points away from the median of its normal-range periods)."""
    obs = []
    for label, src, ends in (("FY", "annual", years), ("Q", "quarter", quarters)):
        for e in ends:
            t, p = rows["tax"][src].get(e), rows["pretax"][src].get(e)
            if t and p and p[0]:
                tag = fiscal_label(e, fye) if label == "Q" else f"FY{fiscal_year(e, fye)}"
                obs.append((tag, t[0] / p[0]))
    if not obs:
        return []
    normal = sorted(r for _, r in obs if 0.05 <= r <= 0.35)
    med = normal[len(normal) // 2] if normal else 0.21  # baseline from normal-range periods only
    return [f"{tag} {r * 100:.1f}%" + (" ⚠ discrete item likely — read the income-tax note" if (r < 0.05 or r > 0.35 or abs(r - med) > 0.08) else "")
            for tag, r in obs]


def ttm(row, quarters):
    if row["kind"] == "per" and len(quarters) >= 4:  # average of the last 4 quarters (share counts)
        vals = [row["quarter"].get(e) for e in quarters[-4:]]
        return None if any(v is None for v in vals) else sum(v[0] for v in vals) / 4
    if row["kind"] != "flow" or len(quarters) < 4:
        return None
    last4 = quarters[-4:]
    if (d(last4[-1]) - d(last4[0])).days > 300:
        return None
    vals = [row["quarter"].get(e) for e in last4]
    if any(v is None for v in vals):
        return None
    return sum(v[0] for v in vals)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker", nargs="?")
    ap.add_argument("--cik", type=int)
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--quarters", type=int, default=8)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()
    ua = os.environ.get("SEC_USER_AGENT", DEFAULT_UA)
    if not args.cik and not args.ticker:
        ap.error("ticker or --cik required")
    cik = args.cik or lookup_cik(args.ticker, ua)[0]
    name, rows, years, quarters, meta = build(cik, ua, args.years, args.quarters)
    fye = meta["fye_month"]
    split_note = "; ".join(f"{(r if r >= 1 else 1 / r):g}-for-1{' reverse' if r < 1 else ''} split (values filed before {b} restated to today's share basis)" for r, b in meta["splits"])

    if args.json:
        out = {"entity": name, "cik": cik, "units": "USD millions (EPS in $, shares in millions)", "fetched": dt.date.today().isoformat(),
               "fiscal_year_end_month": fye, "splits": [{"ratio": r, "restated_from_filing_date": b} for r, b in meta["splits"]],
               "quarter_labels": {e: fiscal_label(e, fye) for e in quarters}, "items": {}}
        for key, r in rows.items():
            if r["kind"] == "inst":
                ends = sorted(r["inst"])[-max(len(quarters), 1):]
                out["items"][key] = {"label": r["label"], "instant": {e: scale(key, r["inst"][e][0]) for e in ends}}
            else:
                out["items"][key] = {
                    "label": r["label"],
                    "annual": {e: scale(key, r["annual"][e][0]) for e in years if e in r["annual"]},
                    "quarter": {e: scale(key, r["quarter"][e][0]) for e in quarters if e in r["quarter"]},
                    "derived_quarters": [e for e in quarters if e in r["quarter"] and r["quarter"][e][2]],
                    "ttm": scale(key, ttm_eps(rows, quarters) if key == "eps_dil" else ttm(r, quarters)),
                }
        out["effective_tax_rates"] = etr_line(rows, years, quarters, fye)
        print(json.dumps(out, indent=1))
        return

    def fmt(x, key=""):
        if x is None:
            return ""
        if key == "eps_dil":
            return f"{x:,.2f}"
        return f"{x:,.1f}" if (abs(x) < 100 or key == "sh_dil") else f"{x:,.0f}"

    print(f"# {name} (CIK {cik}) — SEC XBRL companyfacts, fetched {dt.date.today()}")
    print("Units: USD millions; EPS in $; shares in millions. '*' = quarter derived from YTD/annual differencing.")
    print(f"Fiscal year ends in month {fye}; columns are labelled by fiscal period (period-end date in brackets).")
    if split_note:
        print(f"⚠ Stock split detected: {split_note}. Per-share data and share counts are all on the post-split basis.")
    print()
    hdr = ["Item"] + [f"FY{fiscal_year(e, fye)} ({e[:10]})" for e in years] + [f"{fiscal_label(e, fye)} ({e[:10]})" for e in quarters] + ["TTM", "tag"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "---|" * len(hdr))
    for key, r in rows.items():
        if r["kind"] == "inst":
            continue
        cells, tags = [r["label"]], set()
        for e in years:
            v = r["annual"].get(e)
            cells.append(fmt(scale(key, v[0]), key) if v else "")
            if v:
                tags.add(v[1])
        for e in quarters:
            v = r["quarter"].get(e)
            cells.append((fmt(scale(key, v[0]), key) + ("*" if v[2] else "")) if v else "")
            if v:
                tags.add(v[1])
        cells.append(fmt(scale(key, ttm_eps(rows, quarters) if key == "eps_dil" else ttm(r, quarters)), key))
        cells.append(",".join(sorted(tags))[:60])
        if any(c for c in cells[1:-1]):
            print("| " + " | ".join(cells) + " |")
    print("\nEffective tax rate: " + " · ".join(etr_line(rows, years, quarters, fye)))
    print("(Tax row = TOTAL tax. A low/high ETR flags a discrete item; size it from the tax note, don't remove the whole tax line.)")
    print("\n## Balance sheet (latest 4 instants)")
    latest = quarters[-1] if quarters else (years[-1] if years else "")
    for key, r in rows.items():
        if r["kind"] != "inst" or not r["inst"]:
            continue
        ends = sorted(r["inst"])[-4:]
        if latest and (d(latest) - d(ends[-1])).days > 730:
            continue  # not tagged for 2+ years: noise, not data
        stale = f"  ⚠ stale: last tagged {ends[-1]}, latest quarter {latest} — read the current filing" if latest and ends[-1] < latest else ""
        print(f"- {r['label']}: " + "; ".join(f"{e}: {fmt(scale(key, r['inst'][e][0]))}" for e in ends) + f"  [{r['inst'][ends[-1]][1]}]{stale}")
    print("\nDerived Q4 diluted shares/EPS (*) are approximate: diluted counts are not additive when quarters swing between loss and profit (anti-dilution); prefer the 10-K's Q4 figure when the filing shows it.")
    print("Caveats: tags vary by filer — a blank row means 'not tagged', not 'zero'. Verify any number you rely on against the filing text.")


if __name__ == "__main__":
    main()
