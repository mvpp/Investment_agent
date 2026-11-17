# Valuation Core — method choice, discount rates, terminal value, bridges, targets

## Contents
1. Method selection by business model
2. Discount rate
3. DCF discipline
4. Justified multiples (no naked multiples)
5. Reverse DCF
6. SOTP
7. Scenarios, target price, action price, IRR
8. EV → equity bridge
9. Reconciliation & sanity checks
10. Common errors

---

## 1. Method selection by business model

Ask first: **what is the unit of value creation, and what makes its cash flow certain or uncertain?** Match the method to cash-flow visibility, capital intensity, cyclicality, accounting distortion, asset-vs-franchise value, and binary risk.

| Business model | Primary | Cross-check | Never |
|---|---|---|---|
| Recurring high-growth (SaaS, subscription) | DCF with margin path + customer-economics (LTV/CAC) build | EV/NTM revenue vs (growth + FCF margin) regression; reverse DCF | P/E on depressed GAAP |
| Ad / consumer platforms | DCF or P/E on **core** EPS; SOTP when an investment segment exists | Value per user; reverse DCF | Headline GAAP P/E in a quarter with one-offs |
| Marketplaces / payments | DCF from GMV/TPV × take rate × contribution margin | EV/gross profit | EV/GMV across different take-rate models |
| Semis / hardware (cyclical) | Mid-cycle EPS × mid-cycle P/E; cycle-normalized DCF | EV/EBITDA at mid-cycle; replacement value | Peak EPS × peak multiple |
| Regulated utilities / infra | Rate-base growth → EPS → DDM / P/E vs group | RAB multiple | Unregulated DCF ignoring allowed ROE |
| E&P / mining (finite reserves) | NAV (risked PV of reserves + inventory) at a stated price deck | EV/DACF, FCF yield at strip | Perpetuity DCF on today's production |
| REITs | NAV via cap rates | P/AFFO, implied cap rate | P/E on GAAP EPS (depreciation of appreciating assets) |
| Banks | P/TBV justified by sustainable ROTCE | P/E on normalized credit costs | EV/EBITDA (debt is raw material) |
| Insurers | P/B vs normalized ROE; embedded value (life) | P/E on cat-normalized earnings | Unnormalized cat-light years |
| Pharma / biotech | rNPV per asset + base business DCF with LOE cliffs | EV/sales on peak-sales; pipeline-adjusted P/E | P/E ignoring patent expiries |
| Retail / restaurants | Unit-economics DCF (units × AUV × 4-wall margin) | EV/EBITDA (lease-adjusted) | Store-count extrapolation without returns |
| Industrials / capital goods | Through-cycle EV/EBIT + ROIC spread | Backlog-implied revenue DCF | Peak margins |
| Airlines / transport | Mid-cycle EV/EBITDAR (lease-adjusted), asset value | Replacement cost | Peak EPS |
| Early-stage / pre-profit | Scenario DCF (survival probability × steady state), dilution-adjusted | EV/forward revenue discounted back | Single-point DCF |
| Conglomerates / holdcos | SOTP with holdco discount | — | One multiple for unlike parts |

Core rule: **value is forward FCF and its certainty.** An EV/S of 40 can be cheap if incremental EBITDA margins are 75–85%, FCF conversion ~95% and 30%+ growth is durable. Always look at incremental, not average, economics for scaling businesses.

---

## 2. Discount rate

- Risk-free: current 10-year Treasury yield (look it up; don't assume).
- Equity risk premium: Damodaran's current implied ERP (pages.stern.nyu.edu/~adamodar) — historically ~4–5.5%.
- Beta: bottom-up industry unlevered beta (Damodaran dataset) relevered at target D/E; avoid noisy single-stock regressions.
- Cost of debt: rating-implied yield or current bond YTM, after tax.
- Sanity ranges are **spreads over the current 10-yr yield**, not fixed levels (rates move): regulated utilities rf + 2–3%; large-cap staples rf + 3–4%; mega-cap tech rf + 4.5–6%; high-growth/unprofitable tech rf + 6–9%; clinical biotech rf + 7–11% (risk mostly in PoS, not the rate — don't double count). With rf ≈ 4%, mega-cap tech lands at 8.5–10%; with rf ≈ 5%, 9.5–11%.
- Always show ±1% WACC sensitivity. A conclusion that flips inside ±1% is a low-conviction conclusion.

---

## 3. DCF discipline

- Horizon: 5 years for steady businesses; 10 years for growth businesses that need time to reach steady state. The final explicit year must look like steady state (growth near terminal, positive FCF, stable margins).
- **Reinvestment must fund growth.** Use sales-to-capital (Δrevenue / reinvestment; check the company's history and peers) or explicit capex/D&A/NWC. Terminal reinvestment rate = g / RONIC — growth without reinvestment is free money that doesn't exist.
- Terminal growth ≤ risk-free rate and ≤ long-run nominal GDP (2–3.5% USD). Terminal RONIC: WACC (no moat) to WACC + 10pts (wide moat); >35% needs proof.
- Terminal value share of EV >80% → the explicit period is too short or the steady state is doing all the work. State it.
- **SBC: count it once.** Either treat SBC as a cash expense in FCF (use GAAP EBIT, which includes it) and use today's diluted shares, OR exclude it from costs and project the share count growth. Never exclude it from costs *and* use today's share count.
- Use **core** earnings/FCF from the earnings-normalization skill as the base year, never a distorted GAAP year.
- Working capital sign: sales-to-capital mode treats any revenue decline as capital released (cash in) — right for inventory/receivable-heavy businesses, wrong for **advance-funded** ones, where a decline unwinds customer prepayments and consumes cash. For those use capex mode with a negative `nwc_pct` (ΔNWC/Δrevenue from the last cycle).
- Capex booms: model the depreciation wave. Future D&A ≈ Σ recent capex / useful life (servers 5–6 yrs, buildings 20–30+). EBIT margins that ignore a coming D&A step-up are overstated.

---

## 4. Justified multiples (no naked multiples)

Every multiple in the memo must be tied to growth, returns and risk:
- Justified P/E (steady state) = (1 − g / ROE) / (r − g). Example: ROE 25%, g 5%, r 9% → (1 − 0.2)/0.04 = 20x.
- Justified P/B = (ROE − g) / (r − g). Banks: ROTCE 15%, g 4%, COE 10.5% → 1.7x TBV.
- Justified EV/EBIT = (1 − t)(1 − g / RONIC) / (WACC − g).
- PEG only as a sanity check, and only for companies with comparable durability.
- Always state: which earnings (core vs GAAP), which period (NTM vs FY+2), and why the multiple deserves a premium/discount to peers and to the company's own 5-yr range.

---

## 5. Reverse DCF (mandatory)

Hold everything else at your base case and solve for what the price implies — revenue CAGR (`valuation.py reverse`, `"solve": "growth"`) or terminal margin (`"solve": "margin"`). Then compare with your base case and with consensus:
- Market-implied CAGR well below a credible base case → potential mispricing (find out *why* the market is skeptical before celebrating).
- Market-implied above base case → the stock already prices the good news; the variant view must be bullish *beyond* consensus to justify a long.
The gap, in one sentence, is the core of the memo's variant view.

---

## 6. SOTP

Use when segments differ in growth, margins, capital intensity or risk (ads + cloud + moonshots; retail + AWS-like units; holdcos).
- Value each segment with its own playbook (multiple on segment EBIT, DCF, or option value).
- Allocate corporate costs to segments or value them as a negative segment (capitalized at the group multiple).
- Investment segments: probability × payoff (option value) or zero/negative if you believe the spend is wasted — say which.
- Equity stakes: at market or latest round marks less a liquidity haircut; don't also count their income in core EPS.
- Holdco discount 0–25% depending on capital-allocation track record, tax leakage, and control.

---

## 7. Scenarios, target price, action price, IRR

- Scenarios are built from **KPI values**, not ±X% on the price. Bear/base/bull each change the 2–3 drivers that matter (e.g. NRR, margin, multiple) — the same drivers named as Key Forces.
- Probabilities sum to 1 and reflect your evidence, not symmetry. A 25/50/25 default is a sign you haven't thought about it.
- **Time basis.** A DCF gives value *today*. Give each scenario its `value_today`; `valuation.py scenarios` rolls it to the horizon at (1 + cost of equity − dividend yield)^years. If you instead value at the horizon directly (exit multiple × year-N core EPS), give `value` and the script backs out today's value. Skew and the bear-case check use today's values — horizon values understate downside.
- **Target price** = probability-weighted value at the horizon (default 3 years, the same horizon as the IRR).
- **Expected IRR** = (prob-weighted value / price)^(1/years) − 1 + dividend yield. Hurdle: long ≥ 15% expected IRR; short ≥ 20–25%.
- **Action price** = the lower of (fair value today × (1 − margin of safety)) and (the max price that still earns the hurdle). This one number goes in the memo header. MOS by quality/predictability: wide moat & predictable 15–20%; narrow moat 25–30%; cyclical, no moat or binary 35–50%.
- Skew = (bull − price)/(price − bear). Prefer ≥ 2:1. Size the position for the bear case, not the expected value.
- `valuation.py scenarios` computes all of the above.

---

## 8. EV → equity bridge

Equity = EV + cash & marketable securities + non-operating investments − debt − finance & (for lease-adjusted multiples) operating lease liabilities − minority interests − pension/OPEB deficits − non-convertible preferred − other debt-like items (accrued legal settlements payable, deferred consideration, factoring, residual-value guarantees likely to be called) ± tax assets (if not in FCF).
- **Customer advances / contract liabilities** (project businesses, defense, equipment makers, software with annual prepay): cash on the balance sheet that customers prepaid is not fully the shareholders'. Normal float = contract liabilities ÷ revenue at a mid-cycle level × the revenue you expect to sustain; **excess** float = current contract liabilities − normal float. Deduct the excess as `excess_customer_advances` in the bridge (it unwinds as orders normalize), **or** model the unwind in FCFF with capex mode and a negative `nwc_pct` — never both. Net it against contract assets/unbilled receivables when billing runs ahead the other way.
- Use **post-period** balances: debt raised, equity issued and settlements agreed after the quarter end (8-Ks) belong in the bridge. Mandatory convertible preferred → shares, not a deduction.
- Be consistent: if EBITDA is pre-lease-expense (IFRS 16 style / EBITDAR), subtract lease liabilities; if lease cost is in EBIT, don't.
- Shares: fully diluted (treasury method for options/RSUs; if-converted for in-the-money converts).

---

## 9. Reconciliation & sanity checks

- Present a football field (method → range). Weight methods by your confidence in their inputs (e.g. DCF 50%, comps 30%, SOTP/precedents 20%), and say why.
- Checks: (1) implied multiple at your fair value vs peers and the company's own history; (2) market-implied growth (reverse DCF); (3) implied market share/TAM penetration at the terminal year — absurd if the company must exceed the whole market; (4) implied IRR; (5) does terminal FCF/share imply a dividend capacity that makes sense?

---

## 10. Common errors
- Terminal growth ≥ WACC, or growth with no reinvestment.
- Peak-cycle earnings × a peak multiple.
- Double-counting SBC (excluded from costs and ignored in dilution).
- Double-counting cash (interest income in EPS × multiple **and** cash added in the bridge — fine for P/E only if you use EV-based multiples consistently).
- Margin expansion with no operational mechanism named.
- Discount rates fudged to hit a target; scenario probabilities fudged to clear a hurdle.
- Using GAAP EPS from a quarter with a giant discrete tax charge.
