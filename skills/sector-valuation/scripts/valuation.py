#!/usr/bin/env python3
"""Deterministic valuation math so the memo never relies on mental arithmetic.

Subcommands (each takes a JSON file; see ../examples/*.json):
  dcf        FCFF DCF with growth/margin fade; reinvestment via capex/D&A vintages (models
             the depreciation wave of a capex boom), sales-to-capital (scalar or path) or a
             reinvestment-rate path; value-consistent terminal value (g / RONIC); 5x5 sensitivity.
  reverse    Reverse DCF: solve the constant revenue CAGR (or terminal margin) the
             current price implies, holding the rest of the dcf inputs fixed.
  sotp       Sum-of-the-parts: segment metric x multiple (or explicit value), bridge to per share.
  scenarios  Bear/base/bull probability-weighted value, expected IRR, upside/downside skew,
             hurdle-based buy price and margin-of-safety action price.
  rnpv       Risk-adjusted NPV for drug pipelines (phase PoS defaults, ramp, LOE erosion).
  ltv        SaaS / subscription unit economics: LTV, LTV/CAC, CAC payback.

Usage: python3 valuation.py <subcommand> input.json [--json]
All money inputs in one consistent unit (e.g. USD M); shares in the same scale (M).
"""
import json
import sys


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


def dcf_core(c, growth=None, margin_end=None, wacc=None, g=None):
    """Reinvestment modes (pick one):
      capex mode     : capex_pct (path) + ebitda_margin (path) + asset_life [+ capex_history, nwc_pct].
                       D&A is built from the capex vintage (straight-line), so a capex boom produces
                       the depreciation wave in EBIT; reinvestment = capex − D&A + nwc_pct × Δrevenue.
                       nwc_pct = ΔNWC / Δrevenue: positive = growth ties up working capital; NEGATIVE
                       for advance-funded businesses (customer prepayments), where growth releases cash
                       and a revenue decline consumes it. capex_history lists the years before year 1,
                       oldest first; if shorter than asset_life it is padded with its first value
                       (give asset_life years of history for an accurate opening D&A).
      sales_to_capital (scalar or path): reinvestment = Δrevenue / S2C.
      reinvestment_rate (path): reinvestment = NOPAT × rate (growth is then 'free' — avoid for reverse growth).
    """
    n = c["years"]
    gr = path(growth if growth is not None else c["growth"], n, "growth")
    capex_mode = "capex_pct" in c
    mkey = "ebitda_margin" if capex_mode else "ebit_margin"
    m = path(c[mkey], n, mkey)
    if margin_end is not None:
        m = shift_to_end(m, margin_end)
    tax = path(c.get("tax_rate", 0.21), n, "tax_rate")
    wacc = c["wacc"] if wacc is None else wacc
    g = c["terminal_growth"] if g is None else g
    if g >= wacc:
        return None
    mid = c.get("mid_year", True)
    if capex_mode:
        cx = path(c["capex_pct"], n, "capex_pct")
        life = c["asset_life"]
        hist = list(c.get("capex_history") or [c["revenue0"] * cx[0]])
        hist = [hist[0]] * max(0, life - len(hist)) + hist
        nwc = c.get("nwc_pct", 0.0)
    elif c.get("sales_to_capital") is not None:
        s2c = path(c["sales_to_capital"], n, "sales_to_capital")
    else:
        rr = path(c.get("reinvestment_rate", 0.0), n, "reinvestment_rate")
    rev_prev, rows, pv_sum = c["revenue0"], [], 0.0
    for t in range(n):
        rev = rev_prev * (1 + gr[t])
        row = {"year": t + 1, "revenue": rev, "growth": gr[t]}
        if capex_mode:
            capex = rev * cx[t]
            hist.append(capex)
            da = sum(hist[-life:]) / life
            ebit = rev * m[t] - da
            reinv = capex - da + nwc * (rev - rev_prev)
            row.update({"ebitda_margin": m[t], "capex": capex, "da": da})
        else:
            ebit = rev * m[t]
        nopat = ebit * (1 - tax[t])
        if not capex_mode:
            reinv = (rev - rev_prev) / s2c[t] if c.get("sales_to_capital") is not None else nopat * rr[t]
        fcff = nopat - reinv
        pv = fcff / (1 + wacc) ** ((t + 0.5) if mid else (t + 1))
        pv_sum += pv
        row.update({"margin": ebit / rev, "ebit": ebit, "nopat": nopat, "reinvestment": reinv, "fcff": fcff, "pv": pv})
        rows.append(row)
        rev_prev = rev
    ronic = c.get("terminal_roic", wacc)
    term_margin = rows[-1]["margin"]
    nopat_next = rows[-1]["revenue"] * (1 + g) * term_margin * (1 - tax[-1])
    fcff_next = nopat_next * (1 - g / ronic)
    tv = fcff_next / (wacc - g)
    pv_tv = tv / (1 + wacc) ** (n - 0.5 if mid else n)
    ev = pv_sum + pv_tv
    equity = ev + c.get("net_cash", 0.0) + c.get("investments", 0.0) - c.get("other_claims", 0.0) - c.get("excess_customer_advances", 0.0)
    per_share = equity / c["diluted_shares"]
    return {"rows": rows, "excess_customer_advances": c.get("excess_customer_advances", 0.0), "pv_explicit": pv_sum, "tv": tv, "pv_tv": pv_tv, "ev": ev, "equity": equity, "per_share": per_share,
            "tv_share": pv_tv / ev if ev else None, "tv_ev_ebit": tv / (nopat_next / (1 - tax[-1])), "wacc": wacc, "g": g, "ronic": ronic,
            "capex_mode": capex_mode, "terminal_ebit_margin": term_margin}


def dcf(c):
    r = dcf_core(c)
    if r is None:
        sys.exit("terminal_growth must be below wacc")
    w, g = c["wacc"], c["terminal_growth"]
    step_w, step_g = c.get("wacc_step", 0.005), c.get("g_step", 0.005)
    ws = [w + step_w * k for k in (-2, -1, 0, 1, 2)]
    gs = [g + step_g * k for k in (-2, -1, 0, 1, 2)]
    grid = [[(dcf_core(c, wacc=wi, g=gi) or {}).get("per_share") for gi in gs] for wi in ws]
    warn = []
    if g > 0.04:
        warn.append(f"Terminal growth {pct(g)} exceeds ~4% (long-run nominal GDP / risk-free) — justify or lower.")
    if r["tv_share"] > 0.80:
        warn.append(f"Terminal value is {pct(r['tv_share'])} of EV — value rests on the steady state; extend the explicit period or stress the terminal margin.")
    if r["ronic"] > 0.35:
        warn.append(f"Terminal RONIC {pct(r['ronic'])} assumes a very durable moat; most companies fade toward WACC + a few points.")
    if r.get("capex_mode") and any(row["capex"] < 0.95 * row["da"] for row in r["rows"][-3:]):
        warn.append("Capex runs below D&A in the final explicit years — negative net reinvestment flatters FCFF; steady-state capex should be ≥ D&A for a growing business.")
    if not r.get("capex_mode") and c.get("sales_to_capital") is not None and any(row["growth"] < 0 for row in r["rows"]):
        warn.append("Revenue declines while reinvestment is sales-to-capital: a decline is treated as capital RELEASED (cash in). For advance-funded businesses (customer prepayments) a decline CONSUMES cash — use capex mode with a negative nwc_pct, or deduct excess_customer_advances.")
    if any(row["fcff"] < 0 for row in r["rows"][-2:]):
        warn.append("FCFF still negative in the final explicit years — the terminal year is not steady state; extend the horizon.")
    r.update({"grid": grid, "grid_w": ws, "grid_g": gs, "warnings": warn, "price": c.get("price")})
    if c.get("margin_grid", True):
        # second grid: final-year margin (path shifted, shape kept) x WACC — usually the two inputs that matter most
        mkey = "ebitda_margin" if r.get("capex_mode") else "ebit_margin"
        m_end = path(c[mkey], c["years"], mkey)[-1]
        step = c.get("margin_step", 0.02)
        ends = [m_end + step * k for k in (-2, -1, 0, 1, 2)]
        r["mgrid"] = [[(dcf_core(c, margin_end=me, wacc=wi) or {}).get("per_share") for me in ends] for wi in ws]
        r["mgrid_m"] = [(dcf_core(c, margin_end=me) or {}).get("terminal_ebit_margin") for me in ends]
    if c.get("price"):
        r["upside"] = r["per_share"] / c["price"] - 1
    return r


def render_dcf(r, unit=""):
    if r.get("capex_mode"):
        o = ["## DCF (capex / D&A mode)", "", "| Yr | Revenue | Growth | EBITDA m | Capex | D&A | EBIT m | NOPAT | Reinvest | FCFF | PV |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in r["rows"]:
            o.append(f"| {x['year']} | {money(x['revenue'])} | {pct(x['growth'])} | {pct(x['ebitda_margin'])} | {money(x['capex'])} | {money(x['da'])} | {pct(x['margin'])} | {money(x['nopat'])} | {money(x['reinvestment'])} | {money(x['fcff'])} | {money(x['pv'])} |")
    else:
        o = ["## DCF", "", "| Yr | Revenue | Growth | EBIT margin | NOPAT | Reinvest | FCFF | PV |", "|---|---|---|---|---|---|---|---|"]
        for x in r["rows"]:
            o.append(f"| {x['year']} | {money(x['revenue'])} | {pct(x['growth'])} | {pct(x['margin'])} | {money(x['nopat'])} | {money(x['reinvestment'])} | {money(x['fcff'])} | {money(x['pv'])} |")
    o += ["", "| Bridge | Value |", "|---|---|",
          f"| PV explicit FCFF | {money(r['pv_explicit'])} |",
          f"| PV terminal value ({pct(r['tv_share'])} of EV; implied exit {r['tv_ev_ebit']:.1f}x EBIT) | {money(r['pv_tv'])} |",
          f"| Enterprise value | {money(r['ev'])} |",
          *([f"| (−) Excess customer advances (debt-like float) | {money(r['excess_customer_advances'])} |"] if r.get("excess_customer_advances") else []),
          f"| Equity value | {money(r['equity'])} |",
          f"| **Value per share** | **{money(r['per_share'], 2)}** |"]
    if r.get("price"):
        o.append(f"| Price / upside | {money(r['price'], 2)} / {pct(r['upside'])} |")
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
    price, target = c["price"], c.get("solve", "growth")

    def val(x):
        if target == "growth":
            r = dcf_core(c, growth=x)
        else:
            r = dcf_core(c, margin_end=x)
        return r["per_share"] if r else None

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
        out["implied_final_revenue"] = c["revenue0"] * (1 + x) ** c["years"]
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
        txt = (f"## Reverse DCF\n\nAt {money(r['price'], 2)}/share the market implies a **{pct(r['solution'])} revenue CAGR** "
               f"(final-year revenue {money(r['implied_final_revenue'])}), holding the margin path, reinvestment, WACC and terminal assumptions fixed.")
    else:
        txt = (f"## Reverse DCF\n\nAt {money(r['price'], 2)}/share the market implies a **terminal EBIT margin of {pct(r['implied_terminal_ebit_margin'])}** "
               f"({r['mode']}), holding the growth path fixed.")
    return txt + "".join(f"\n\n⚠ {w}" for w in r.get("warnings", []))


# ---------- SOTP ----------
def sotp(c):
    rows, total = [], 0.0
    for s in c["segments"]:
        v = s["value"] if "value" in s else s["metric"] * s["multiple"]
        v *= s.get("probability", 1.0)
        rows.append({**s, "ev": v})
        total += v
    disc = c.get("holdco_discount", 0.0)
    ev = total * (1 - disc)
    equity = ev + c.get("net_cash", 0.0) + c.get("investments", 0.0) - c.get("other_claims", 0.0)
    ps = equity / c["diluted_shares"]
    res = {"rows": rows, "gross": total, "holdco_discount": disc, "ev": ev, "equity": equity, "per_share": ps}
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
          f"| **Equity value / share** | | {money(r['equity'])} | **{money(r['per_share'], 2)}** | |"]
    if r.get("price"):
        o.append(f"\nPrice {money(r['price'], 2)} → upside {pct(r['upside'])}")
    return "\n".join(o)


# ---------- scenarios ----------
def scenarios(c):
    """Each scenario gives `value_today` (e.g. its DCF value) and/or `value` (per-share value at the
    horizon). Missing one is derived by rolling at the cost of equity net of dividend yield:
    value = value_today x (1 + ke − dy)^years. Skew and the bear check use today's values."""
    sc = [dict(s) for s in c["scenarios"]]
    p = sum(s["prob"] for s in sc)
    warn = [] if abs(p - 1) < 1e-6 else [f"Probabilities sum to {p:.2f}, not 1.00."]
    price, yrs = c["price"], c.get("years", 3.0)
    dy = c.get("dividend_yield", 0.0)
    ke = c.get("cost_of_equity")
    hurdle = c.get("hurdle", 0.15)
    roll = (1 + ke - dy) ** yrs if ke is not None else None
    for s in sc:
        if "value" not in s and "value_today" in s:
            if roll is None:
                sys.exit("cost_of_equity is required to roll value_today forward to the horizon")
            s["value"] = s["value_today"] * roll
        if "value_today" not in s and roll is not None:
            s["value_today"] = s["value"] / roll
    ev = sum(s["prob"] * s["value"] for s in sc)
    irr = (ev / price) ** (1 / yrs) - 1 + dy
    have_today = all("value_today" in s for s in sc)
    basis = "value_today" if have_today else "value"
    bear = min(s[basis] for s in sc)
    bull = max(s[basis] for s in sc)
    skew = (bull - price) / (price - bear) if (price > bear and bull > price) else None
    skew_note = None if skew is not None else ("price ≥ bull case" if bull <= price else "price ≤ bear case")
    buy_for_hurdle = ev / (1 + max(hurdle - dy, 0)) ** yrs
    fv_today = c.get("fair_value_today") or (sum(s["prob"] * s["value_today"] for s in sc) if have_today else None)
    mos = c.get("margin_of_safety")
    mos_price = fv_today * (1 - mos) if (fv_today and mos is not None) else None
    action = min(x for x in (mos_price, buy_for_hurdle) if x is not None)
    if bear < price * 0.6:
        warn.append(f"Bear case ({'today' if have_today else 'horizon'} value) implies {pct(bear / price - 1)} — size the position for that loss, not the expected value.")
    if skew is not None and skew < 2:
        warn.append(f"Upside/downside skew {skew:.1f}:1 is below 2:1.")
    if ke is not None and irr < ke:
        warn.append(f"Expected IRR {pct(irr)} is below the cost of equity {pct(ke)} — expected value-destroying at this price.")
    if not have_today:
        warn.append("No value_today per scenario (or cost_of_equity): skew/bear use horizon values, which understate downside vs today's price.")
    return {"rows": sc, "expected_value": ev, "expected_return": ev / price - 1, "irr": irr, "skew": skew, "skew_note": skew_note, "skew_basis": basis, "years": yrs,
            "price": price, "buy_for_hurdle": buy_for_hurdle, "hurdle": hurdle, "fair_value_today": fv_today, "mos_price": mos_price,
            "mos": mos, "action_price": action, "warnings": warn}


def render_scen(r):
    o = ["## Scenarios", "", "| Scenario | Prob | Value today | Value at horizon | Horizon vs price | Key assumptions |", "|---|---|---|---|---|---|"]
    for s in r["rows"]:
        o.append(f"| {s['name']} | {pct(s['prob'], 0)} | {money(s.get('value_today'), 2)} | {money(s['value'], 2)} | {pct(s['value'] / r['price'] - 1)} | {s.get('assumptions', '')} |")
    o.append(f"| **Probability-weighted** | | **{money(r['fair_value_today'], 2)}** | **{money(r['expected_value'], 2)}** | **{pct(r['expected_return'])}** | horizon {r['years']:g} yr |")
    o += ["", f"- Target price (prob-weighted, {r['years']:g}-yr horizon): **{money(r['expected_value'], 2)}**",
          f"- Expected IRR: **{pct(r['irr'])}** (hurdle {pct(r['hurdle'])})",
          f"- Upside/downside skew ({r['skew_basis']} basis): {('%.1f:1' % r['skew']) if r['skew'] is not None else 'n/a (' + r['skew_note'] + ')'}",
          f"- Max price that still earns the hurdle: {money(r['buy_for_hurdle'], 2)}"]
    if r["mos_price"]:
        o.append(f"- Fair value today x (1 − {pct(r['mos'], 0)} MOS): {money(r['mos_price'], 2)}")
    o.append(f"- **Action price for the memo header (lower of the two): {money(r['action_price'], 2)}**")
    if r["warnings"]:
        o += ["", "Warnings:"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(o)


# ---------- rNPV ----------
# Cumulative probability of approval from each phase. Source: BIO / Informa Pharma
# Intelligence / QLS, "Clinical Development Success Rates 2011-2020" (all indications).
# Oncology runs ~30-40% lower from Phase I/II; hematology and rare disease higher. Override per asset.
POS = {"preclinical": 0.05, "phase1": 0.079, "phase2": 0.151, "phase3": 0.524, "filed": 0.906, "approved": 1.0}


def rnpv(c):
    r = c.get("discount_rate", 0.10)
    tax = c.get("tax_rate", 0.15)
    rows, total = [], 0.0
    for a in c["assets"]:
        pos = a.get("pos", POS[a["phase"]])
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
    shares = c["diluted_shares"] * (1 + c.get("expected_dilution", 0.0))
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
    res = fn(json.load(open(sys.argv[2])))
    print(json.dumps(res, indent=1, default=float) if "--json" in sys.argv else rend(res))


if __name__ == "__main__":
    main()
