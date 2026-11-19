#!/usr/bin/env python3
"""Deterministic valuation math so the memo never relies on mental arithmetic.

Subcommands (each takes a JSON file; see ../examples/*.json):
  dcf        FCFF DCF with growth/margin fade (or margins built from an incremental margin on
             new revenue); reinvestment via capex/D&A vintages (models the depreciation wave of a
             capex boom), sales-to-capital (scalar or path) or a reinvestment-rate path;
             value-consistent terminal value (g / RONIC); 5x5 sensitivity.
  reverse    Reverse DCF: solve the revenue growth (whole path scaled, shape kept) or the
             terminal margin the current price implies, holding the rest of the dcf inputs fixed.
  sotp       Sum-of-the-parts: segment metric x multiple (or explicit value), bridge to per share.
  scenarios  Bear/base/bull probability-weighted value, expected IRR, upside/downside skew,
             hurdle-based buy price and margin-of-safety action price.
  rnpv       Risk-adjusted NPV for drug pipelines (phase PoS defaults, ramp, LOE erosion).
  ltv        SaaS / subscription unit economics: LTV, LTV/CAC, CAC payback.

Usage: python3 valuation.py <subcommand> input.json [--json]
All money inputs in one consistent unit (e.g. USD M); shares in the same scale (M).

Bridge inputs shared by dcf and sotp: net_cash (negative = net debt), investments, other_claims,
excess_customer_advances, and capital_actions — post-period events not yet in the balance sheet:
  [{"item": "Forward sale, 46M sh", "shares": 46, "cash": 28700, "claims": 0, "source": "8-K 10-29"}]
  shares/cash added; claims (debt raised, PV of preferred dividends, expected legal penalties) deducted.
split_factor (e.g. 2 for a pending 2-for-1) prints post-split per-share values next to pre-split ones.
"""
import json
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "earnings-normalization" / "scripts"))
from evidence import number, positive, units, verify


def probability(value, label):
    if not 0 <= number(value, label) <= 1:
        raise ValueError(f"{label} must be in [0, 1]")
    return value


def check_valuation_units(c):
    if not c.get("unit") or not c.get("shares_unit"):
        raise ValueError("declare unit and shares_unit before dividing equity value by shares")
    return units(c)


def check_dcf(c):
    check_valuation_units(c)
    if type(c["years"]) is not int or c["years"] < 1:
        raise ValueError("years must be a positive integer")
    positive(c["revenue0"], "revenue0")
    for rate in path(c.get("tax_rate", 0.21), c["years"], "tax_rate"):
        if not 0 <= number(rate, "tax_rate") < 1:
            raise ValueError("DCF tax_rate must be in [0, 1)")
    if any(number(rate, "growth") <= -1 for rate in path(c["growth"], c["years"], "growth")):
        raise ValueError("annual revenue growth must exceed -100%")
    w = positive(c["wacc"], "wacc")
    g = number(c["terminal_growth"], "terminal_growth")
    roic = positive(c.get("terminal_roic", w), "terminal_roic")
    if not -1 < g < w or g >= roic:
        raise ValueError("terminal_growth must exceed -100% and be below both WACC and terminal RONIC")
    if c.get("terminal_da", "steady_state") not in ("steady_state", "final_year"):
        raise ValueError("invalid terminal_da method")
    threshold = number(c.get("terminal_reinvestment_threshold", 0.05), "terminal_reinvestment_threshold")
    if threshold < 0:
        raise ValueError("terminal_reinvestment_threshold must be nonnegative")


# ---------- helpers ----------
def path(spec, n, key):
    """Accept a list of n values, a scalar, or {"start": a, "end": b} linear fade."""
    if isinstance(spec, list):
        if len(spec) != n:
            sys.exit(f"{key}: expected {n} values, got {len(spec)}")
        return spec
    if isinstance(spec, dict):
        a, b = spec["start"], spec["end"]
        return [a + (b - a) * i / (n - 1) if n > 1 else b for i in range(n)]
    return [spec] * n


def money(x, dp=0):
    return "" if x is None else f"{x:,.{dp}f}"


def pct(x, dp=1):
    return "n/a" if x is None else f"{x * 100:.{dp}f}%"


# ---------- DCF ----------
def shift_to_end(m, x):
    """Shift a margin path so its final value is x while keeping its shape (linear blend)."""
    n = len(m)
    return [mt + (x - m[-1]) * (t + 1) / n for t, mt in enumerate(m)]


def asset_classes(c):
    """[(share of capex, life)] — `asset_classes` [{"share", "life"}] or a single `asset_life`."""
    if c.get("asset_classes"):
        cls = [(a["share"], a["life"]) for a in c["asset_classes"]]
        for share, life in cls:
            probability(share, "asset class share")
            if type(life) is not int or life < 1:
                raise ValueError("asset life must be a positive integer")
        if abs(sum(sh for sh, _ in cls) - 1) > 1e-6:
            sys.exit("asset_classes shares must sum to 1")
        return cls
    if type(c["asset_life"]) is not int or c["asset_life"] < 1:
        raise ValueError("asset_life must be a positive integer")
    return [(1.0, c["asset_life"])]


def da_from(hist, cls, lag):
    """Straight-line D&A for the latest year of `hist` (capex by year, oldest first); capex starts
    depreciating `lag` years after it is spent (construction in progress)."""
    end = len(hist) - lag
    return sum(sh * sum(hist[max(0, end - life):end]) / life for sh, life in cls)


def steady_da_ratio(cls, lag, g):
    """D&A / same-year capex when capex grows at g forever."""
    return sum(sh * sum((1 + g) ** -k for k in range(lag, lag + life)) / life for sh, life in cls)


def incremental_path(c, gr, n):
    """Average-margin path from a base margin plus an incremental margin on each year's new revenue:
    profit_t = profit_{t-1} + incremental_t x (rev_t - rev_{t-1}), optionally capped at margin_cap x rev_t."""
    inc = path(c["incremental_margin"], n, "incremental_margin")
    cap = c.get("margin_cap")
    rev_prev = c["revenue0"]
    profit = c["margin0"] * rev_prev
    out = []
    for t in range(n):
        rev = rev_prev * (1 + gr[t])
        profit += inc[t] * (rev - rev_prev)
        if cap is not None:
            profit = min(profit, cap * rev)
        out.append(profit / rev)
        rev_prev = rev
    return out


def bridge(c, ev):
    acts = c.get("capital_actions") or []
    equity = (ev + c.get("net_cash", 0.0) + c.get("investments", 0.0) - c.get("other_claims", 0.0)
              - c.get("excess_customer_advances", 0.0)
              + sum(a.get("cash", 0.0) for a in acts) - sum(a.get("claims", 0.0) for a in acts))
    shares = positive(c["diluted_shares"], "diluted_shares") + sum(a.get("shares", 0.0) for a in acts)
    return equity, positive(shares, "shares after capital actions")


def dcf_core(c, growth=None, margin_end=None, wacc=None, g=None, growth_scale=1.0, growth_shift=0.0):
    """Reinvestment modes (pick one):
      capex mode     : capex_pct (path) + ebitda_margin (path) + asset_life or asset_classes
                       [+ capex_history, in_service_lag, nwc_pct].
                       D&A is built from the capex vintage (straight-line), so a capex boom produces
                       the depreciation wave in EBIT; reinvestment = capex − D&A + nwc_pct × Δrevenue.
                       asset_classes: [{"share": 0.6, "life": 5}, {"share": 0.4, "life": 25}] splits each
                       year's capex between asset types (servers vs buildings). in_service_lag: years
                       before capex starts depreciating (large construction in progress; default 0).
                       nwc_pct = ΔNWC / Δrevenue: positive = growth ties up working capital; NEGATIVE
                       for advance-funded businesses (customer prepayments), where growth releases cash
                       and a revenue decline consumes it. capex_history lists the fiscal years BEFORE
                       year 1, oldest first, ending with the base period (if revenue0 is TTM, end with
                       TTM capex and drop the fiscal year it overlaps); padded with its first value if
                       shorter than the longest life + lag.
                       Terminal value uses steady-state D&A (capex growing at g with the final capex_pct),
                       not the final year's D&A, which still carries boom vintages (terminal_da:
                       "final_year" restores the old behaviour).
      sales_to_capital (scalar or path): reinvestment = Δrevenue / S2C.
    Revenue declines: by default no positive working capital or invested capital is released (a
      downturn rarely hands back cash at the growth-phase ratio — inventory is written down, receivables
      stretch). Set sales_to_capital_down (S2C mode) or nwc_pct_down (capex mode) to release capital on
      declines, from evidence in the last downturn. A negative nwc_pct (advance-funded) still consumes
      cash on a decline unless nwc_pct_down overrides it.
      reinvestment_rate (path): reinvestment = NOPAT × rate (growth is then 'free' — avoid for reverse growth).
    Margins (any mode): a path in ebit_margin (ebitda_margin in capex mode), OR incremental_margin
      (scalar/path, on each year's new revenue) + margin0 (base-year margin, same basis) [+ margin_cap,
      the steady-state ceiling]. Incremental mode re-derives margins from the revenue path, so faster
      growth lifts margins (operating leverage) — including in the reverse-DCF growth solve.
    """
    n = c["years"]
    gr = [x * growth_scale + growth_shift for x in path(growth if growth is not None else c["growth"], n, "growth")]
    capex_mode = "capex_pct" in c
    mkey = "ebitda_margin" if capex_mode else "ebit_margin"
    incremental = c.get("incremental_margin") is not None
    m = incremental_path(c, gr, n) if incremental else path(c[mkey], n, mkey)
    if margin_end is not None:
        m = shift_to_end(m, margin_end)
    tax = path(c.get("tax_rate", 0.21), n, "tax_rate")
    wacc = c["wacc"] if wacc is None else wacc
    g = c["terminal_growth"] if g is None else g
    if g >= wacc or wacc <= 0 or g <= -1 or g >= c.get("terminal_roic", wacc):
        return None
    mid = c.get("mid_year", True)
    if capex_mode:
        cx = path(c["capex_pct"], n, "capex_pct")
        cls = asset_classes(c)
        lag = c.get("in_service_lag", 0)
        if type(lag) is not int or lag < 0:
            raise ValueError("in_service_lag must be a nonnegative integer")
        hist = list(c.get("capex_history") or [c["revenue0"] * cx[0]])
        if any(number(value, "capex") < 0 for value in [*cx, *hist]):
            raise ValueError("capex_pct and capex_history must be nonnegative")
        hist = [hist[0]] * max(0, max(l for _, l in cls) + lag - len(hist)) + hist
        nwc = number(c.get("nwc_pct", 0.0), "nwc_pct")
        nwc_down = number(c.get("nwc_pct_down", min(nwc, 0.0)), "nwc_pct_down")
    elif c.get("sales_to_capital") is not None:
        s2c = [positive(v, "sales_to_capital") for v in path(c["sales_to_capital"], n, "sales_to_capital")]
        s2c_down = positive(c["sales_to_capital_down"], "sales_to_capital_down") if c.get("sales_to_capital_down") is not None else None
    else:
        rr = path(c.get("reinvestment_rate", 0.0), n, "reinvestment_rate")
    rev_prev, rows, pv_sum = c["revenue0"], [], 0.0
    for t in range(n):
        rev = rev_prev * (1 + gr[t])
        row = {"year": t + 1, "revenue": rev, "growth": gr[t]}
        if capex_mode:
            capex = rev * cx[t]
            hist.append(capex)
            da = da_from(hist, cls, lag)
            ebit = rev * m[t] - da
            reinv = capex - da + (nwc if rev >= rev_prev else nwc_down) * (rev - rev_prev)
            row.update({"ebitda_margin": m[t], "capex": capex, "da": da})
        else:
            ebit = rev * m[t]
        nopat = ebit * (1 - tax[t])
        if not capex_mode:
            if c.get("sales_to_capital") is None:
                reinv = nopat * rr[t]
            elif rev >= rev_prev:
                reinv = (rev - rev_prev) / s2c[t]
            else:
                reinv = (rev - rev_prev) / s2c_down if s2c_down else 0.0
        fcff = nopat - reinv
        pv = fcff / (1 + wacc) ** ((t + 0.5) if mid else (t + 1))
        pv_sum += pv
        row.update({"margin": ebit / rev, "ebit": ebit, "nopat": nopat, "reinvestment": reinv, "fcff": fcff, "pv": pv})
        rows.append(row)
        rev_prev = rev
    ronic = c.get("terminal_roic", wacc)
    final_margin = term_margin = rows[-1]["margin"]
    if capex_mode and c.get("terminal_da", "steady_state") == "steady_state":
        term_margin = m[-1] - cx[-1] * steady_da_ratio(cls, lag, g)
    nopat_next = rows[-1]["revenue"] * (1 + g) * term_margin * (1 - tax[-1])
    fcff_next = nopat_next * (1 - g / ronic)
    tv = fcff_next / (wacc - g)
    pv_tv = tv / (1 + wacc) ** (n - 0.5 if mid else n)
    ev = pv_sum + pv_tv
    equity, shares = bridge(c, ev)
    per_share = equity / shares
    for row in rows:
        row["nopat_ps"] = row["nopat"] / shares
    reconciliation = None
    if capex_mode:
        next_revenue = rev_prev * (1 + g)
        next_capex = next_revenue * cx[-1]
        # A steady-state D&A uses all vintages growing at g. In final-year mode, advance
        # the actual vintage schedule by one year to quantify the transition.
        next_da = (next_capex * steady_da_ratio(cls, lag, g)
                   if c.get("terminal_da", "steady_state") == "steady_state" else da_from(hist + [next_capex], cls, lag))
        schedule = next_capex - next_da + nwc * (next_revenue - rev_prev)
        required = nopat_next * g / ronic
        schedule_nopat = (next_revenue * m[-1] - next_da) * (1 - tax[-1])
        schedule_tv = (schedule_nopat - schedule) / (wacc - g)
        reconciliation = {"nopat": nopat_next, "schedule_nopat": schedule_nopat, "capex": next_capex, "da": next_da, "delta_nwc": nwc * (next_revenue - rev_prev),
                          "ronic_reinvestment": required, "schedule_reinvestment": schedule,
                          "gap_fraction_of_nopat": (schedule - required) / abs(nopat_next) if nopat_next else None,
                          "threshold": c.get("terminal_reinvestment_threshold", 0.05),
                          "ronic_tv": tv, "schedule_tv": schedule_tv,
                          "schedule_per_share": per_share + (schedule_tv - tv) / (1 + wacc) ** (n - 0.5 if mid else n) / shares}
    return {"terminal_reinvestment_reconciliation": reconciliation, "rows": rows, "excess_customer_advances": c.get("excess_customer_advances", 0.0), "pv_explicit": pv_sum, "tv": tv, "pv_tv": pv_tv, "ev": ev, "equity": equity, "per_share": per_share,
            "shares": shares, "capital_actions": c.get("capital_actions") or [], "split_factor": c.get("split_factor"),
            "tv_share": pv_tv / ev if ev else None, "tv_ev_ebit": tv / (rev_prev * (1 + g) * term_margin) if term_margin else None, "wacc": wacc, "g": g, "ronic": ronic,
            "capex_mode": capex_mode, "incremental": incremental, "margin_path": m, "terminal_ebit_margin": term_margin, "final_year_ebit_margin": final_margin}


def dcf(c):
    check_dcf(c)
    r = dcf_core(c)
    if r["tv"] <= 0:
        raise ValueError("terminal NOPAT and FCFF must be positive for a going-concern DCF")
    w, g = c["wacc"], c["terminal_growth"]
    step_w, step_g = c.get("wacc_step", 0.005), c.get("g_step", 0.005)
    ws = [w + step_w * k for k in (-2, -1, 0, 1, 2)]
    gs = [g + step_g * k for k in (-2, -1, 0, 1, 2)]
    grid = [[(dcf_core(c, wacc=wi, g=gi) or {}).get("per_share") for gi in gs] for wi in ws]
    r["wacc_swing"] = [(dcf_core(c, wacc=w + d) or {}).get("per_share") for d in (-0.01, 0.01)]
    warn = []
    rec = r["terminal_reinvestment_reconciliation"]
    if rec and abs(rec["schedule_reinvestment"] - rec["ronic_reinvestment"]) > rec["threshold"] * abs(rec["nopat"]):
        warn.append("Terminal reinvestment gap exceeds the threshold. Show terminal values under both RONIC and the capex schedule.")
    if r.get("capex_mode") and abs(r["terminal_ebit_margin"] - r["final_year_ebit_margin"]) > 0.01:
        warn.append(f"Final-year EBIT margin {pct(r['final_year_ebit_margin'])} vs steady-state {pct(r['terminal_ebit_margin'])} used for the terminal value — "
                    "D&A has not settled by the last explicit year (boom vintages still depreciating); the terminal value uses the steady state.")
    if g > 0.04:
        warn.append(f"Terminal growth {pct(g)} exceeds ~4% (long-run nominal GDP / risk-free) — justify or lower.")
    if r["tv_share"] is not None and r["tv_share"] > 0.80:
        warn.append(f"Terminal value is {pct(r['tv_share'])} of EV — value rests on the steady state; extend the explicit period or stress the terminal margin.")
    if r["ronic"] > 0.35:
        warn.append(f"Terminal RONIC {pct(r['ronic'])} assumes a very durable moat; most companies fade toward WACC + a few points.")
    if r.get("capex_mode") and c.get("terminal_da") == "final_year" and any(row["capex"] < 0.95 * row["da"] for row in r["rows"][-3:]):
        warn.append("Capex runs below D&A in the final explicit years and the terminal value uses that year's D&A — negative net reinvestment flatters the terminal FCFF; use terminal_da steady_state or extend the horizon.")
    declines = any(row["growth"] < 0 for row in r["rows"])
    if declines and not r.get("capex_mode") and c.get("sales_to_capital") is not None:
        if c.get("sales_to_capital_down") is not None:
            warn.append(f"Revenue declines release capital at sales_to_capital_down {c['sales_to_capital_down']:g}x (cash in) — cite the last downturn's working-capital release as evidence.")
        warn.append("Revenue declines in sales-to-capital mode: for advance-funded businesses (customer prepayments) a decline CONSUMES cash — use capex mode with a negative nwc_pct, or deduct excess_customer_advances.")
    if declines and r.get("capex_mode") and c.get("nwc_pct_down", 0) > 0:
        warn.append(f"Revenue declines release working capital at nwc_pct_down {pct(c['nwc_pct_down'])} — cite the last downturn's working-capital release as evidence.")
    if r["incremental"]:
        basis = "EBITDA" if r["capex_mode"] else "EBIT"
        if c.get("margin_cap") is None:
            warn.append(f"incremental_margin without margin_cap: the average {basis} margin keeps converging toward the incremental margin "
                        f"(final year {pct(r['margin_path'][-1])}). Set margin_cap at a steady state supported by peers at scale.")
        if any(row["growth"] < 0 for row in r["rows"]):
            warn.append("Revenue declines in incremental mode remove profit at the same incremental margin — check that the cost base is that flexible.")
    if any(row["fcff"] < 0 for row in r["rows"][-2:]):
        warn.append("FCFF still negative in the final explicit years — the terminal year is not steady state; extend the horizon.")
    if r["incremental"]:
        im = c["incremental_margin"]
        r["inc_label"] = pct(im) if isinstance(im, (int, float)) else (f"{pct(im['start'])}→{pct(im['end'])}" if isinstance(im, dict) else "path")
        r["margin_cap"] = c.get("margin_cap")
    r.update({"grid": grid, "grid_w": ws, "grid_g": gs, "warnings": warn, "price": c.get("price")})
    if c.get("margin_grid", True):
        # second grid: final-year margin (path shifted, shape kept) x WACC — usually the two inputs that matter most
        m_end = r["margin_path"][-1]
        step = c.get("margin_step", 0.02)
        ends = [m_end + step * k for k in (-2, -1, 0, 1, 2)]
        r["mgrid"] = [[(dcf_core(c, margin_end=me, wacc=wi) or {}).get("per_share") for me in ends] for wi in ws]
        r["mgrid_m"] = [(dcf_core(c, margin_end=me) or {}).get("terminal_ebit_margin") for me in ends]
    if c.get("price"):
        r["upside"] = r["per_share"] / c["price"] - 1
    return r


def action_lines(acts):
    out = []
    for a in acts:
        parts = [f"shares {a['shares']:+,.1f}" if a.get("shares") else "", f"cash {a['cash']:+,.0f}" if a.get("cash") else "",
                 f"claims −{a['claims']:,.0f}" if a.get("claims") else ""]
        out.append(f"| Capital action: {a.get('item', '?')} ({', '.join(p for p in parts if p)}) [{a.get('source', '')}] | {money(a.get('cash', 0.0) - a.get('claims', 0.0))} |")
    return out


def render_dcf(r, unit=""):
    if r.get("capex_mode"):
        o = ["## DCF (capex / D&A mode)", "", "| Yr | Revenue | Growth | EBITDA m | Capex | D&A | EBIT m | NOPAT | NOPAT/sh | Reinvest | FCFF | PV |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in r["rows"]:
            o.append(f"| {x['year']} | {money(x['revenue'])} | {pct(x['growth'])} | {pct(x['ebitda_margin'])} | {money(x['capex'])} | {money(x['da'])} | {pct(x['margin'])} | {money(x['nopat'])} | {money(x['nopat_ps'], 2)} | {money(x['reinvestment'])} | {money(x['fcff'])} | {money(x['pv'])} |")
        o.append(f"\nTerminal EBIT margin {pct(r['terminal_ebit_margin'])} (steady-state D&A) vs final explicit year {pct(r['final_year_ebit_margin'])}.")
    else:
        o = ["## DCF", "", "| Yr | Revenue | Growth | EBIT margin | NOPAT | NOPAT/sh | Reinvest | FCFF | PV |", "|---|---|---|---|---|---|---|---|---|"]
        for x in r["rows"]:
            o.append(f"| {x['year']} | {money(x['revenue'])} | {pct(x['growth'])} | {pct(x['margin'])} | {money(x['nopat'])} | {money(x['nopat_ps'], 2)} | {money(x['reinvestment'])} | {money(x['fcff'])} | {money(x['pv'])} |")
    rec = r.get("terminal_reinvestment_reconciliation")
    if rec:
        o += ["", "| Terminal method | Reinvestment | Terminal value | Value/share today |", "|---|---:|---:|---:|",
              f"| Growth / RONIC | {money(rec['ronic_reinvestment'])} | {money(rec['ronic_tv'])} | {money(r['per_share'], 2)} |",
              f"| Capex − D&A + ΔNWC | {money(rec['schedule_reinvestment'])} | {money(rec['schedule_tv'])} | {money(rec['schedule_per_share'], 2)} |",
              f"Gap as a share of terminal NOPAT: {pct(rec['gap_fraction_of_nopat'])} (warning threshold {pct(rec['threshold'])})."]
    if r.get("incremental"):
        basis = "EBITDA" if r["capex_mode"] else "EBIT"
        cap = f", capped at {pct(r['margin_cap'])}" if r.get("margin_cap") is not None else ""
        o.append(f"\n{basis} margin path built from incremental margin {r['inc_label']} on new revenue{cap}: "
                 f"year 1 {pct(r['margin_path'][0])} → final year {pct(r['margin_path'][-1])}.")
    o.append("NOPAT/sh ≈ EPS before net interest and non-operating items, on the bridge share count — use it to compare with consensus EPS.")
    o += ["", "| Bridge | Value |", "|---|---|",
          f"| PV explicit FCFF | {money(r['pv_explicit'])} |",
          f"| PV terminal value ({pct(r['tv_share'])} of EV; implied exit {money(r['tv_ev_ebit'], 1) or 'n/m'}x EBIT) | {money(r['pv_tv'])} |",
          f"| Enterprise value | {money(r['ev'])} |",
          *([f"| (−) Excess customer advances (debt-like float) | {money(r['excess_customer_advances'])} |"] if r.get("excess_customer_advances") else []),
          *action_lines(r["capital_actions"]),
          f"| Equity value | {money(r['equity'])} |",
          f"| Shares (incl. capital actions) | {money(r['shares'], 1)} |",
          f"| **Value per share** | **{money(r['per_share'], 2)}** |"]
    if r.get("split_factor"):
        o.append(f"| Value per share after {r['split_factor']:g}-for-1 split | {money(r['per_share'] / r['split_factor'], 2)} |")
    if r.get("price"):
        o.append(f"| Price / upside | {money(r['price'], 2)} / {pct(r['upside'])} |")
    lo, hi = r["wacc_swing"]
    if lo and hi and r["per_share"]:
        o.append(f"\nWACC swing: {money(lo, 2)} at {pct(r['wacc'] - 0.01)} · {money(r['per_share'], 2)} at {pct(r['wacc'])} · {money(hi, 2)} at {pct(r['wacc'] + 0.01)} "
                 f"(−1pt {pct(lo / r['per_share'] - 1)}, +1pt {pct(hi / r['per_share'] - 1)}). Put this line in the memo.")
    o += ["", f"Sensitivity — value/share (rows WACC, cols terminal g; centre = base, WACC {pct(r['wacc'])}, g {pct(r['g'])}, RONIC {pct(r['ronic'])}):", ""]
    o.append("| WACC \\ g | " + " | ".join(pct(g) for g in r["grid_g"]) + " |")
    o.append("|---" * (len(r["grid_g"]) + 1) + "|")
    for i, w in enumerate(r["grid_w"]):
        cells = [("**" + money(v, 2) + "**" if (i == 2 and j == 2) else money(v, 2)) if v else "n/m" for j, v in enumerate(r["grid"][i])]
        o.append(f"| {pct(w)} | " + " | ".join(cells) + " |")
    if r.get("mgrid"):
        o += ["", "Sensitivity — value/share (rows WACC, cols terminal-year EBIT margin; margin path shifted, shape kept; centre = base):", ""]
        o.append("| WACC \\ margin | " + " | ".join(pct(m) for m in r["mgrid_m"]) + " |")
        o.append("|---" * (len(r["mgrid_m"]) + 1) + "|")
        for i, w in enumerate(r["grid_w"]):
            cells = [("**" + money(v, 2) + "**" if (i == 2 and j == 2) else money(v, 2)) if v else "n/m" for j, v in enumerate(r["mgrid"][i])]
            o.append(f"| {pct(w)} | " + " | ".join(cells) + " |")
    if r["warnings"]:
        o += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(o)


# ---------- reverse DCF ----------
def reverse(c):
    check_dcf(c)
    price, target = c["price"], c.get("solve", "growth")

    constant = c.get("growth_mode") == "constant"
    # default: scale the whole growth path (keeps its fade toward terminal); shift it if it has negative years
    scale = not constant and min(path(c["growth"], c["years"], "growth")) >= 0

    def val(x):
        if target == "growth":
            r = dcf_core(c, growth=x) if constant else (dcf_core(c, growth_scale=x) if scale else dcf_core(c, growth_shift=x))
        else:
            r = dcf_core(c, margin_end=x)
        return r["per_share"] if r else None

    if target == "growth" and scale:
        lo, hi = -1.0, 6.0
    elif target == "growth" and not constant:
        lo, hi = -0.9 - min(path(c["growth"], c["years"], "growth")), 1.0
    else:
        lo, hi = (-0.30, 1.0) if target == "growth" else (-0.2, 0.9)
    vlo, vhi = val(lo), val(hi)
    if vlo is None or vhi is None or (vlo - price) * (vhi - price) > 0:
        return {"solve": target, "solution": None, "note": f"No solution in [{lo}, {hi}] (value range {money(vlo, 2)}–{money(vhi, 2)} vs price {price}). Value may not be monotonic (incremental ROIC < WACC) — check sales_to_capital."}
    for _ in range(100):
        mid = (lo + hi) / 2
        if (val(mid) - price) * (vlo - price) > 0:
            lo, vlo = mid, val(mid)
        else:
            hi = mid
    x = (lo + hi) / 2
    out = {"solve": target, "solution": x, "price": price, "warnings": []}
    if target == "growth":
        n = c["years"]
        base_path = path(c["growth"], n, "growth")
        ipath = [x] * n if constant else ([v * x for v in base_path] if scale else [v + x for v in base_path])
        fin = c["revenue0"]
        for v in ipath:
            fin *= 1 + v
        bfin = c["revenue0"]
        for v in base_path:
            bfin *= 1 + v
        out.update({"implied_final_revenue": fin, "implied_cagr": (fin / c["revenue0"]) ** (1 / n) - 1, "base_cagr": (bfin / c["revenue0"]) ** (1 / n) - 1,
                    "incremental": c.get("incremental_margin") is not None,
                    "adj": x, "mode": "constant" if constant else ("scale" if scale else "shift"), "path_first": ipath[0], "path_last": ipath[-1]})
        if "capex_pct" not in c and c.get("sales_to_capital") is None:
            out["warnings"].append("reinvestment_rate mode: extra growth needs no extra capital here, so the implied CAGR is biased LOW. Re-run with sales_to_capital or capex mode for the growth solve.")
    else:
        r = dcf_core(c, margin_end=x)
        out["implied_terminal_ebit_margin"] = r["terminal_ebit_margin"]
        out["mode"] = "EBITDA path shifted (capex mode); terminal EBIT margin shown" if "capex_pct" in c else "EBIT margin path shifted, shape preserved"
    return out


def render_reverse(r):
    if r["solution"] is None:
        return "## Reverse DCF\n\n" + r["note"]
    if r["solve"] == "growth":
        how = {"constant": "constant growth every year",
               "scale": f"your growth path scaled ×{r['adj']:.2f}, shape kept",
               "shift": f"your growth path shifted {r['adj'] * 100:+.1f}pts every year"}[r["mode"]]
        how += f": year 1 {pct(r['path_first'])}, final year {pct(r['path_last'])}" if r["mode"] != "constant" else ""
        txt = (f"## Reverse DCF\n\nAt {money(r['price'], 2)}/share the market implies a **{pct(r['implied_cagr'])} revenue CAGR** over the explicit period "
               f"vs {pct(r['base_cagr'])} in your base case ({how}; final-year revenue {money(r['implied_final_revenue'])}), holding "
               + ("the incremental margin (margins re-derived from the implied revenue path)" if r.get("incremental") else "the margin path")
               + ", reinvestment, WACC and terminal assumptions fixed.")
    else:
        txt = (f"## Reverse DCF\n\nAt {money(r['price'], 2)}/share the market implies a **terminal EBIT margin of {pct(r['implied_terminal_ebit_margin'])}** "
               f"({r['mode']}), holding the growth path fixed.")
    return txt + "".join(f"\n\n⚠ {w}" for w in r.get("warnings", []))


# ---------- SOTP ----------
def sotp(c):
    check_valuation_units(c)
    rows, total = [], 0.0
    for s in c["segments"]:
        v = s["value"] if "value" in s else s["metric"] * s["multiple"]
        v *= probability(s.get("probability", 1.0), "segment probability")
        rows.append({**s, "ev": v})
        total += v
    disc = c.get("holdco_discount", 0.0)
    ev = total * (1 - disc)
    equity, shares = bridge(c, ev)
    ps = equity / shares
    res = {"rows": rows, "gross": total, "holdco_discount": disc, "ev": ev, "equity": equity, "per_share": ps,
           "capital_actions": c.get("capital_actions") or [], "split_factor": c.get("split_factor")}
    if c.get("price"):
        res["price"], res["upside"] = c["price"], ps / c["price"] - 1
    return res


def render_sotp(r):
    o = ["## Sum of the parts", "", "| Segment | Basis | EV | Per share | % of gross |", "|---|---|---|---|---|"]
    sh = r["equity"] / r["per_share"] if r["per_share"] else 1
    for s in r["rows"]:
        basis = s.get("basis") or (f"{money(s['metric'])} x {s['multiple']}x" if "metric" in s else "explicit")
        if s.get("probability", 1) != 1 and not s.get("basis"):
            basis += f" x p={s['probability']}"
        o.append(f"| {s['name']} | {basis} | {money(s['ev'])} | {money(s['ev'] / sh, 2)} | {pct(s['ev'] / r['gross'])} |")
    o += [f"| Holdco / conglomerate discount | {pct(r['holdco_discount'])} | | | |",
          *[f"| Capital action: {a.get('item', '?')}" + (f" (+{a['shares']:,.1f} sh)" if a.get("shares") else "")
            + f" | {a.get('source', '')} | {money(a.get('cash', 0.0) - a.get('claims', 0.0))} | {money((a.get('cash', 0.0) - a.get('claims', 0.0)) / sh, 2)} | |"
            for a in r["capital_actions"]],
          f"| **Equity value / share** | | {money(r['equity'])} | **{money(r['per_share'], 2)}** | |"]
    if r.get("split_factor"):
        o.append(f"| Equity value / share after {r['split_factor']:g}-for-1 split | | | {money(r['per_share'] / r['split_factor'], 2)} | |")
    if r.get("price"):
        o.append(f"\nPrice {money(r['price'], 2)} → upside {pct(r['upside'])}")
    return "\n".join(o)


# ---------- scenarios ----------
def price_linked_dcf(c, s, yrs):
    fp = Path(c.get("_dir", ".")) / s["dcf"]
    model = json.loads(fp.read_text())
    check_dcf(model)
    if not c.get("unit") or units(model)[0] != units(c)[0]:
        raise ValueError("declare scenario unit with the same currency as the linked DCF")
    if "as_of" in c and (date.fromisoformat(model["as_of"]) > date.fromisoformat(c["as_of"]) or model.get("ticker") != c["ticker"]):
        raise ValueError("scenario DCF has a different issuer or later as_of")
    audit = verify(model, fp.parent, c.get("_require_evidence", False) or "as_of" in c)
    if audit:
        s["dcf_evidence"] = audit
    d = dcf_core(model)
    if d["tv"] <= 0:
        raise ValueError("linked DCF needs positive terminal FCFF")
    s["value_today"] = d["per_share"]
    if "horizon_bridge" in s:
        hb = s["horizon_bridge"]
        if not float(yrs).is_integer() or yrs > len(d["rows"]):
            raise ValueError("horizon_bridge requires a whole year within the explicit DCF")
        if units(c) != units(model) or units({**model, **hb}) != units(model):
            raise ValueError("horizon bridge and DCF must use the same money and share scale")

        def ev_at(t):
            # End of year t, after that year's FCFF. Keep the underlying DCF timing convention.
            return (sum(row["pv"] for row in d["rows"] if row["year"] > t) + d["pv_tv"]) * (1 + model["wacc"]) ** t

        s.setdefault("warnings", [])
        if "buyback_share" in hb:
            if "net_cash" in hb or "diluted_shares" in hb:
                raise ValueError("payout-mode horizon_bridge derives net_cash and diluted_shares — do not supply them")
            out, sched = payout_bridge(model, d, hb, c, int(yrs), ev_at, hb.get("repurchase_price", "market"))
            neutral, _ = payout_bridge(model, d, hb, c, int(yrs), ev_at, "intrinsic")
            equity, shares = bridge(out, ev_at(yrs))
            n_equity, n_shares = bridge(neutral, ev_at(yrs))
            s["payout_schedule"] = sched
            s["horizon_net_cash"], s["horizon_diluted_shares"] = out["net_cash"], out["diluted_shares"]
            s["buyback_value_effect"] = equity / shares - n_equity / n_shares
            dear = [row for row in sched if row["buyback"] > 0 and row["repurchase_price"] > row["intrinsic_value"] * 1.001]
            if dear:
                s["warnings"].append(f"buybacks at {money(dear[0]['repurchase_price'], 2)}/sh in year {dear[0]['year']} exceed intrinsic value "
                                     f"{money(dear[0]['intrinsic_value'], 2)} — repurchases destroy {money(-s['buyback_value_effect'], 2)}/sh by year {yrs:g}.")
        else:
            number(hb["net_cash"], "horizon net_cash")
            equity, shares = bridge(hb, ev_at(yrs))
            s["warnings"].append("explicit horizon net_cash/diluted_shares — prefer payout mode (buyback_share) so buybacks and retained cash follow one rule.")
        s["fundamentals_based_target"] = equity / shares


def payout_bridge(model, d, hb, c, yrs, ev_at, repurchase):
    """Roll the linked DCF's opening balances to year `yrs`: each year's FCFF (+ yield on net cash)
    is added to cash, buyback_share and dividend_share of positive FCFF are paid out, and repurchased
    shares are retired at the repurchase price — "market" (today's price rolled at Ke − DY),
    "intrinsic" (the scenario's own value per share that year: value-neutral) or an explicit list."""
    acts = model.get("capital_actions") or []
    cash = model.get("net_cash", 0.0) + sum(a.get("cash", 0.0) for a in acts)
    shares = positive(model["diluted_shares"], "diluted_shares") + sum(a.get("shares", 0.0) for a in acts)
    inv = number(hb.get("investments", model.get("investments", 0.0)), "horizon investments")
    claims = number(hb.get("other_claims", model.get("other_claims", 0.0) + sum(a.get("claims", 0.0) for a in acts)), "horizon other_claims")
    adv = number(hb.get("excess_customer_advances", model.get("excess_customer_advances", 0.0)), "horizon excess_customer_advances")
    bb = probability(hb["buyback_share"], "buyback_share")
    dv = probability(hb.get("dividend_share", 0.0), "dividend_share")
    if bb + dv > 1:
        raise ValueError("buyback_share + dividend_share cannot exceed 1")
    cy = number(hb.get("cash_yield", 0.0), "cash_yield")
    dil = number(hb.get("annual_dilution", 0.0), "annual_dilution")
    if repurchase == "market":
        if "cost_of_equity" not in c:
            raise ValueError("repurchase_price 'market' needs cost_of_equity")
        roll = 1 + number(c["cost_of_equity"], "cost_of_equity") - c.get("dividend_yield", 0.0)
    elif isinstance(repurchase, list):
        if len(repurchase) < yrs:
            raise ValueError(f"repurchase_price list needs {yrs} values")
        for v in repurchase:
            positive(v, "repurchase_price")
    elif repurchase != "intrinsic":
        raise ValueError("repurchase_price must be 'market', 'intrinsic' or a list of prices")
    rows = []
    for t in range(1, yrs + 1):
        fcff = d["rows"][t - 1]["fcff"]
        interest = cy * cash
        cash += fcff + interest
        shares *= 1 + dil
        buyback, dividends = bb * max(fcff, 0.0), dv * max(fcff, 0.0)
        intrinsic = (ev_at(t) + cash + inv - claims - adv) / shares
        rp = (c["price"] * roll ** t if repurchase == "market" else intrinsic if repurchase == "intrinsic" else repurchase[t - 1])
        retired = buyback / positive(rp, "repurchase price")
        cash -= buyback + dividends
        shares = positive(shares - retired, "horizon shares after buybacks")
        rows.append({"year": t, "fcff": fcff, "interest": interest, "buyback": buyback, "dividends": dividends, "repurchase_price": rp,
                     "intrinsic_value": intrinsic, "shares_retired": retired, "shares_end": shares, "net_cash_end": cash})
    return {"unit": model["unit"], "shares_unit": model["shares_unit"], "net_cash": cash, "diluted_shares": shares,
            "investments": inv, "other_claims": claims, "excess_customer_advances": adv}, rows


MOS_BASE = {"A": 0.15, "B": 0.25, "C": 0.35}
POLICY_THRESHOLD = 0.25


def mos_rule(m):
    """margin_of_safety: a number (legacy) or {"quality": A-D, "cyclical": bool, "policy_exposure": share of
    revenue that needs a discretionary government decision to keep selling at today's price,
    "net_debt_ebitda": x}. A 15 / B 25 / C 35, +10 per factor that applies, cap 50; D = no position."""
    if m is None:
        return None, None, False
    if not isinstance(m, dict):
        return probability(m, "margin_of_safety"), "supplied", False
    q = m.get("quality")
    if q == "D":
        return None, "quality D: no position", True
    if q not in MOS_BASE:
        raise ValueError("margin_of_safety.quality must be A, B, C or D")
    factors = []
    if m.get("cyclical"):
        factors.append("cyclical")
    exp = m.get("policy_exposure")
    if exp is not None:
        if probability(exp, "policy_exposure") >= POLICY_THRESHOLD:
            factors.append(f"policy-binary ({pct(exp, 0)} of revenue)")
    lev = m.get("net_debt_ebitda")
    if lev is not None and number(lev, "net_debt_ebitda") > 3.5:
        factors.append(f"levered ({lev:.1f}x)")
    raw = MOS_BASE[q] + 0.10 * len(factors)
    note = " + ".join([f"{q} {pct(MOS_BASE[q], 0)}"] + [f"{f} 10" for f in factors]) + f" = {pct(min(raw, 0.5), 0)}"
    if raw > 0.5:
        note += " (cap)"
    if exp is None:
        note += "; policy_exposure not given"
    return min(raw, 0.5), note, False


def rate(r, flags, quality_d, ke):
    """Ordered rating table (research-playbook §8): the first row that matches wins."""
    f = flags or {}
    skew_ok = (r["skew"] is not None and r["skew"] >= 2) or r["skew_note"] == "price ≤ bear case"
    if quality_d or f.get("kill_triggered") or f.get("thesis_broken") or f.get("accounting_flag"):
        row, new, held, why = 1, "Avoid", "Sell", "quality D, kill condition triggered, thesis broken or accounting score ≥ 7"
    elif r["irr"] >= r["hurdle"] and r["action_price"] is not None and r["price"] <= r["action_price"] and skew_ok and not f.get("kill_near"):
        row, new, held, why = 2, "Buy", "Add", "IRR ≥ hurdle, price ≤ action price, skew ≥ 2:1, no kill condition near"
    elif r["irr"] >= r["hurdle"]:
        row, new, held, why = 3, "Avoid (watchlist, near miss)", "Hold", "IRR ≥ hurdle but price > action price, skew < 2:1 or a kill condition near"
    elif ke is None or r["irr"] >= ke:
        row, new, held, why = 4, "Avoid (watchlist)", "Hold", "IRR between cost of equity and hurdle"
    else:
        row, new, held, why = 5, "Avoid (watchlist)", "Trim", "IRR below cost of equity"
    return {"rating": held if f.get("owned") else new, "rating_row": row, "rating_reason": why}


def scenarios(c):
    """Each scenario gives `value_today` (e.g. its DCF value) and/or `value` (per-share value at the
    horizon). A linked DCF plus a projected horizon_bridge values remaining cash flows at the horizon.
    The required-return roll uses the cost of equity net of dividend yield:
    value = value_today x (1 + ke − dy)^years. Skew and the bear check use today's values."""
    sc = [dict(s) for s in c["scenarios"]]
    total = sum(probability(s["prob"], "scenario probability") for s in sc)
    if abs(total - 1) > 1e-6:
        raise ValueError(f"scenario probabilities sum to {total:g}; expected 1")
    warn = []
    price, yrs = positive(c["price"], "price"), positive(c.get("years", 3), "years")
    dy = probability(c.get("dividend_yield", 0.0), "dividend_yield")
    ke = number(c["cost_of_equity"], "cost_of_equity") if "cost_of_equity" in c else None
    hurdle = number(c.get("hurdle", 0.15), "hurdle")
    roll = positive(1 + ke - dy, "roll-forward factor") ** yrs if ke is not None else None
    for s in sc:
        if "dcf" in s:
            price_linked_dcf(c, s, yrs)
        elif "horizon_bridge" in s:
            raise ValueError("horizon_bridge requires a linked DCF")
        rolled = s["value_today"] * roll if "value_today" in s and roll is not None else None
        s["required_return_rolled_target"] = rolled
        if "fundamentals_based_target" in s:
            s["value"] = number(s["fundamentals_based_target"], "fundamentals_based_target")
            s["target_basis"] = "fundamentals_based_target"
        elif "value" in s:
            s["target_basis"] = "supplied_horizon_value"
        elif rolled is not None:
            s["value"] = rolled
            s["target_basis"] = "required_return_rolled_target"
        else:
            raise ValueError("scenario needs a horizon value or value_today and cost_of_equity")
        if number(s["value"], "horizon value") < 0:
            raise ValueError("scenario equity target must be nonnegative")
        if "value_today" not in s and roll is not None:
            s["value_today"] = s["value"] / roll

    def weighted(key):
        if all(s.get(key) is not None for s in sc):
            return sum(s["prob"] * s[key] for s in sc)
        return None

    ev = sum(s["prob"] * s["value"] for s in sc)
    irr = (ev / price) ** (1 / yrs) - 1 + dy
    have_today = all("value_today" in s for s in sc)
    basis = "value_today" if have_today else "value"
    bear = min(s[basis] for s in sc)
    bull = max(s[basis] for s in sc)
    skew = (bull - price) / (price - bear) if (price > bear and bull > price) else None
    skew_note = None if skew is not None else ("price ≥ bull case" if bull <= price else "price ≤ bear case")
    buy_for_hurdle = ev / (1 + max(hurdle - dy, 0)) ** yrs
    fv_today = c.get("fair_value_today", weighted("value_today"))
    mos, mos_note, quality_d = mos_rule(c.get("margin_of_safety"))
    mos_price = fv_today * (1 - mos) if (fv_today is not None and mos is not None) else None
    action = None if quality_d else min(x for x in (mos_price, buy_for_hurdle) if x is not None)
    for s in sc:
        warn += [f"{s.get('name', '?')}: {w}" for w in s.get("warnings", [])]
    if len(sc) > 1 and not c.get("weight_basis"):
        warn.append("No weight_basis — state in one line which way the weights skew (which tail is fatter) and the evidence for it.")
    if bear < price * 0.6:
        warn.append(f"Bear case ({'today' if have_today else 'horizon'} value) implies {pct(bear / price - 1)} — size the position for that loss, not the expected value.")
    if skew is not None and skew < 2:
        warn.append(f"Upside/downside skew {skew:.1f}:1 is below 2:1.")
    if ke is not None and irr < ke:
        warn.append(f"Expected IRR {pct(irr)} is below the cost of equity {pct(ke)} — expected value-destroying at this price.")
    if not have_today:
        warn.append("No value_today per scenario (or cost_of_equity): skew/bear use horizon values, which understate downside vs today's price.")
    out = {"required_return_rolled_target": weighted("required_return_rolled_target"),
           "fundamentals_based_target": weighted("fundamentals_based_target"),
           "rows": sc, "expected_value": ev, "expected_return": ev / price - 1, "irr": irr, "skew": skew, "skew_note": skew_note, "skew_basis": basis, "years": yrs,
           "price": price, "buy_for_hurdle": buy_for_hurdle, "hurdle": hurdle, "fair_value_today": fv_today, "mos_price": mos_price,
           "mos": mos, "mos_note": mos_note, "action_price": action, "warnings": warn, "split_factor": c.get("split_factor"),
           "weight_basis": c.get("weight_basis")}
    out.update(rate(out, c.get("rating_flags"), quality_d, ke))
    if "rating_flags" not in c:
        warn.append("No rating_flags — the rating assumes no kill condition triggered or near, thesis intact, accounting score < 7, no position held.")
    return out


def render_scen(r):
    o = ["## Scenarios", "", "| Scenario | Prob | Value today | Value at horizon | Target basis | Horizon vs price | Key assumptions |", "|---|---|---|---|---|---|---|"]
    for s in r["rows"]:
        o.append(f"| {s['name']} | {pct(s['prob'], 0)} | {money(s.get('value_today'), 2)} | {money(s['value'], 2)} | {s['target_basis']} | {pct(s['value'] / r['price'] - 1)} | {s.get('assumptions', '')} |")
    o.append(f"| **Probability-weighted** | | **{money(r['fair_value_today'], 2)}** | **{money(r['expected_value'], 2)}** | | **{pct(r['expected_return'])}** | horizon {r['years']:g} yr |")
    o += ["", f"- Target price (prob-weighted, {r['years']:g}-yr horizon): **{money(r['expected_value'], 2)}**",
          f"- Expected IRR: **{pct(r['irr'])}** (hurdle {pct(r['hurdle'])})",
          f"- Upside/downside skew ({r['skew_basis']} basis): {('%.1f:1' % r['skew']) if r['skew'] is not None else 'n/a (' + r['skew_note'] + ')'}",
          f"- Max price that still earns the hurdle: {money(r['buy_for_hurdle'], 2)}"]
    for key, label in (("fundamentals_based_target", "Fundamentals-based target"), ("required_return_rolled_target", "Required-return rolled target")):
        o.append(f"- {label} (probability-weighted): {money(r[key], 2) if r[key] is not None else 'unavailable'}")
    for s in r["rows"]:
        if "payout_schedule" in s:
            o.append(f"- {s['name']} horizon bridge (payout mode): net cash {money(s['horizon_net_cash'])} · diluted shares {money(s['horizon_diluted_shares'], 1)}"
                     f" · buybacks vs value-neutral {s['buyback_value_effect']:+,.2f}/sh")
    if r["mos_price"] is not None:
        o.append(f"- Fair value today x (1 − {pct(r['mos'], 0)} MOS): {money(r['mos_price'], 2)}" + (f" — MOS {r['mos_note']}" if r.get("mos_note") else ""))
    if r["action_price"] is None:
        o.append(f"- **No action price: {r['mos_note']}**")
    else:
        o.append(f"- **Action price for the memo header (lower of the two): {money(r['action_price'], 2)}**")
    o.append(f"- **Rating for the memo header: {r['rating']}** (row {r['rating_row']}: {r['rating_reason']})")
    if r.get("split_factor"):
        k = r["split_factor"]
        o.append(f"- After the {k:g}-for-1 split: fair value {money((r['fair_value_today'] or 0) / k, 2)} · target {money(r['expected_value'] / k, 2)} · action price {money((r['action_price'] or 0) / k, 2)} — show both in the header until the split is effective.")
    if r["warnings"]:
        o += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(o)


# ---------- rNPV ----------
# Cumulative probability of approval from each phase. Source: BIO / Informa Pharma
# Intelligence / QLS, "Clinical Development Success Rates 2011-2020" (all indications).
# Oncology runs ~30-40% lower from Phase I/II; hematology and rare disease higher. Override per asset.
POS = {"preclinical": 0.05, "phase1": 0.079, "phase2": 0.151, "phase3": 0.524, "filed": 0.906, "approved": 1.0}


def rnpv(c):
    check_valuation_units(c)
    r = c.get("discount_rate", 0.10)
    tax = c.get("tax_rate", 0.15)
    rows, total = [], 0.0
    for a in c["assets"]:
        pos = probability(a.get("pos", POS[a["phase"]]), "probability of success")
        launch, peak = a["launch_year"], a["peak_sales"]
        ytp = a.get("years_to_peak", 5)
        loe = a.get("loe_year", launch + 12)
        ero1 = a.get("loe_erosion", 0.8)  # first-year revenue loss after LOE (small molecule ~0.8-0.9, biologic ~0.3-0.5)
        decay = a.get("post_loe_decline", 0.3)
        margin = a.get("operating_margin", 0.45)
        royalty = a.get("economics_share", 1.0)  # share of asset economics owned (royalty / partnership)
        rev_prev, pv_cf, t = 0.0, 0.0, 1
        while t <= 40:
            if t < launch:
                rev = 0.0
            elif t < loe:
                rev = peak * min(1.0, (t - launch + 1) / ytp)
            elif t == loe:
                rev = rev_prev * (1 - ero1)
            else:
                rev = rev_prev * (1 - decay)
            cf = rev * margin * (1 - tax) * royalty
            pv_cf += cf / (1 + r) ** (t - 0.5)
            if t > loe and rev < 0.01 * peak:
                break
            rev_prev, t = rev, t + 1
        # Spend dev cost evenly until launch, weighted by the probability the programme
        # is still running: 1.0 today, falling linearly to P(reaching filing) = pos / P(filed->approval).
        dev = a.get("remaining_dev_cost", 0.0)
        span = max(launch - 1, 1)
        p_file = min(1.0, pos / POS["filed"])
        pv_dev = sum(dev / span * (1 - (1 - p_file) * (k - 1) / span) / (1 + r) ** (k - 0.5) for k in range(1, span + 1))
        val = pos * pv_cf - pv_dev
        rows.append({"name": a["name"], "phase": a["phase"], "pos": pos, "pv_unrisked": pv_cf, "pv_dev": pv_dev, "rnpv": val})
        total += val
    equity = total + c.get("net_cash", 0.0) - c.get("other_claims", 0.0) - c.get("pv_corporate_costs", 0.0)
    shares = positive(c["diluted_shares"], "diluted_shares") * positive(1 + c.get("expected_dilution", 0.0), "dilution factor")
    res = {"rows": rows, "pipeline": total, "equity": equity, "per_share": equity / shares, "discount_rate": r}
    if c.get("price"):
        res["price"], res["upside"] = c["price"], res["per_share"] / c["price"] - 1
    return res


def render_rnpv(r):
    o = ["## rNPV", "", "| Asset | Phase | PoS | PV unrisked | PV dev cost | rNPV |", "|---|---|---|---|---|---|"]
    for x in r["rows"]:
        o.append(f"| {x['name']} | {x['phase']} | {pct(x['pos'])} | {money(x['pv_unrisked'])} | {money(x['pv_dev'])} | {money(x['rnpv'])} |")
    o.append(f"| **Pipeline** | | | | | **{money(r['pipeline'])}** |")
    o.append(f"\nEquity {money(r['equity'])} → **{money(r['per_share'], 2)}/share** (discount rate {pct(r['discount_rate'])}; dev costs weighted by probability the programme is still running)")
    if r.get("price"):
        o.append(f"Price {money(r['price'], 2)} → upside {pct(r['upside'])}")
    return "\n".join(o)


# ---------- LTV ----------
def ltv(c):
    arpa, gm, churn = c["arpa"], c["gross_margin"], c["annual_churn"]
    exp = c.get("annual_expansion", 0.0)
    r = c.get("discount_rate", 0.10)
    yrs = c.get("max_years", 10)
    val, survive, rev = 0.0, 1.0, arpa
    for t in range(1, yrs + 1):
        val += rev * gm * survive / (1 + r) ** t
        survive *= (1 - churn)
        rev *= (1 + exp)
    cac = c["cac"]
    payback = cac / (arpa * gm / 12)
    res = {"ltv": val, "cac": cac, "ltv_cac": val / cac, "payback_months": payback,
           "simple_ltv": arpa * gm / churn if churn else None, "nrr_implied": (1 - churn) * (1 + exp)}
    warn = []
    if res["ltv_cac"] < 3:
        warn.append(f"LTV/CAC {res['ltv_cac']:.1f}x < 3x — growth spend may destroy value.")
    if payback > 36:
        warn.append(f"CAC payback {payback:.0f} months > 36 — cash-hungry growth; check that cohorts actually survive that long.")
    res["warnings"] = warn
    return res


def render_ltv(r):
    o = ["## Unit economics", "", "| Metric | Value |", "|---|---|",
         f"| LTV (discounted, capped horizon) | {money(r['ltv'])} |",
         f"| Simple LTV (ARPA x GM / churn) | {money(r['simple_ltv'])} |",
         f"| CAC | {money(r['cac'])} |",
         f"| **LTV / CAC** | **{r['ltv_cac']:.1f}x** |",
         f"| CAC payback (gross-margin basis) | {r['payback_months']:.0f} months |",
         f"| Implied NRR (1 − churn) x (1 + expansion) | {pct(r['nrr_implied'])} |"]
    if r["warnings"]:
        o += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(o)


CMDS = {"dcf": (dcf, render_dcf), "reverse": (reverse, render_reverse), "sotp": (sotp, render_sotp),
        "scenarios": (scenarios, render_scen), "rnpv": (rnpv, render_rnpv), "ltv": (ltv, render_ltv)}


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in CMDS:
        sys.exit(__doc__)
    fn, rend = CMDS[sys.argv[1]]
    try:
        source = Path(sys.argv[2])
        cfg = json.loads(source.read_text())
        units(cfg)
        audit = verify(cfg, source.parent, "--require-evidence" in sys.argv)
        cfg["_dir"] = str(source.parent)
        cfg["_require_evidence"] = "--require-evidence" in sys.argv
        for key in ("split_factor", "price"):
            if key in cfg:
                positive(cfg[key], key)
        res = fn(cfg)
        if audit:
            res["evidence"] = audit
        print(json.dumps(res, indent=1, allow_nan=False) if "--json" in sys.argv else rend(res))
    except (ValueError, OSError, KeyError, TypeError, IndexError, AttributeError, ArithmeticError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
