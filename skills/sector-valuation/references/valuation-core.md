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
| Recurring high-growth (SaaS, subscription) | By stage (tech.md): early — LTV/CAC cohort build + scenario DCF; scaling — DCF on incremental margins; mature — DCF anchored by FCF yield + growth and ROIC | EV/NTM revenue vs (growth + FCF margin) regression — context only when incremental ≫ current margin; reverse DCF | P/E on depressed GAAP; EV/S or Rule of 40 as the valuation |
| Ad / consumer platforms | DCF or P/E on **core** EPS; SOTP when an investment segment exists | Value per user; reverse DCF | Headline GAAP P/E in a quarter with one-offs |
| Marketplaces / payments | DCF from GMV/TPV × take rate × contribution margin | EV/gross profit | EV/GMV across different take-rate models |
| E-commerce (1P) / DTC brands | Contribution-margin build (cohorts × orders × contribution after marketing − CAC) → DCF to steady-state margin | EV/gross profit; EV/EBITDA vs mature retail once profitable | Revenue multiple without contribution margin after marketing |
| Semis / hardware (cyclical) | Mid-cycle EPS × mid-cycle P/E; cycle-normalized DCF | EV/EBITDA at mid-cycle; replacement value | Peak EPS × peak multiple |
| Regulated utilities / infra | Rate-base growth → EPS → DDM / P/E vs group, judged by the **earned ROE − cost of equity** spread | RAB multiple; justified P/B from earned ROE | Unregulated DCF ignoring allowed ROE; paying for rate-base growth when earned ROE ≤ COE |
| E&P / mining (finite reserves) | NAV (risked PV of reserves + inventory) at a stated price deck | EV/DACF, FCF yield at strip | Perpetuity DCF on today's production |
| REITs | NAV via cap rates | P/AFFO, implied cap rate | P/E on GAAP EPS (depreciation of appreciating assets) |
| Banks | P/TBV justified by sustainable ROTCE | P/E on normalized credit costs | EV/EBITDA (debt is raw material) |
| Insurers | P/B vs normalized ROE; embedded value (life) | P/E on cat-normalized earnings | Unnormalized cat-light years |
| Pharma / biotech | rNPV per asset + base business DCF with LOE cliffs | EV/sales on peak-sales; pipeline-adjusted P/E | P/E ignoring patent expiries |
| Retail / restaurants | Unit-economics DCF (units × AUV × 4-wall margin) | EV/EBITDA (lease-adjusted) | Store-count extrapolation without returns |
| Industrials / capital goods | Through-cycle EV/EBIT + ROIC spread | Backlog-implied revenue DCF | Peak margins |
| Airlines | Mid-cycle EV/EBITDAR (lease-adjusted), asset value | Replacement cost; loyalty-program SOTP | Peak EPS |
| Rail / trucking / logistics | Mid-cycle P/E or EV/EBITDA on an operating-ratio path; DCF for rail | Network replacement cost (rail, LTL doors) | Peak freight-cycle EPS |
| Shipping | P/NAV on broker vessel values | FCF yield at mid-cycle TCE; charter-backlog DCF | Annualized spot TCE |
| Early-stage / pre-profit | Scenario DCF (survival probability × steady state), dilution-adjusted | EV/forward revenue discounted back | Single-point DCF |
| Conglomerates / holdcos | SOTP with holdco discount | — | One multiple for unlike parts |

Core rule: **value is forward FCF and its certainty.** An EV/S of 40 can be cheap if incremental EBITDA margins are 75–85%, FCF conversion ~95% and 30%+ growth is durable. Always look at incremental, not average, economics for scaling businesses.

Putting the rule into the model: today's average margin hides operating leverage, and anything priced off current margins (EV/S, P/E, the growth + FCF-margin regression, Rule of 40) calls such a company expensive by construction. Build the margin path from the incremental margin instead — average margin_t = (m₀·R₀ + Σ m_inc·ΔR) / R_t — with the calculator's `margin0` + `incremental_margin` + `margin_cap` (`examples/dcf_incremental.json`). Evidence for m_inc: Δcore EBIT ÷ Δcore revenue over 4–8 quarters (earnings-normalization), gross margin as its ceiling, and which cost lines are genuinely fixed; fade it toward, and cap the average at, a steady state supported by peers at scale. Then FCF conversion (EBITDA → FCF after capex, SBC and working capital) decides how much of that margin is cash. The same arithmetic runs in reverse: high-fixed-cost businesses have high decremental margins in a downturn.

---

## 2. Discount rate

- Risk-free: current 10-year Treasury yield. Sources in order: FRED series DGS10 (`https://fred.stlouisfed.org/series/DGS10`, fetchable), Treasury.gov daily par yield curve, then a market-data page. Record the date.
- Equity risk premium: Damodaran's implied ERP. The current month's figure is on his home page (`https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm`, "Implied ERP on <date>"; the bare `~adamodar/` URL can return an empty page); year-end values are in `New_Home_Page/datafile/histimpl.html` — the **last** row is the latest year. (`implpr.html` is a stale copy that ends in 2016; don't use it.) If unreachable, use the last value you can confirm and date it; if none, use 4.5% and say "ERP assumed". His ERP is solved at that date's Treasury yield; if the yield has since moved by more than ~0.5pt, hold the implied expected market return constant: ERP = (his rf + his ERP) − today's rf.
- Beta: bottom-up **industry unlevered beta** (corrected for cash) from Damodaran's "Betas by Sector (US)" — read the HTML table at `https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html` (the .xls link is hard to parse; the table is updated each January and is current for the year) — relevered at the company's market D/E: βL = βU × (1 + (1 − t) × D/E).
  - **Pick industries by where the money is made, weighted by the revenue (or operating income) mix** — not by how the company describes itself and not an equal blend. A company earning ~98% of revenue from advertising takes the Advertising beta, even if it is also an internet/software company; a conglomerate takes the segment-weighted average.
  - Cross-check against the stock's own 2-year weekly or 5-year monthly regression beta (a finance site's "beta"). If the two differ by more than ~0.3, say which you used and why; don't average them silently.
  - If the defensible betas give different ratings (one says Buy, the other Avoid), report both values in the memo and lower conviction — the decision then rests on a judgment input, not the business.
  - If the page is unreachable, use these January-2026 values and label them "Damodaran Jan-26, not refreshed":

  | Sector | βU | Sector | βU |
  |---|---|---|---|
  | Utility (general) | 0.15 | Homebuilding | 0.85 |
  | Food processing | 0.47 | Machinery | 0.89 |
  | Hospitals / facilities | 0.56 | Total market ex-financials | 0.90 |
  | Healthcare support services | 0.74 | Shoe | 1.00 |
  | Household products | 0.74 | Retail (special lines) | 1.00 |
  | Retail (general) | 0.78 | Software | 1.25 |
  | Restaurant / dining | 0.78 | Auto & truck | 1.31 |
  | Apparel | 0.79 | Semiconductor | 1.50 |

- No size premium by default (the evidence is weak and it double-counts risks you should model in scenarios); if you add one, show the value with and without it.
- Cost of debt (pre-tax): the yield to maturity on the company's traded bonds; for floating-rate loans, forward SOFR + the loan spread; with neither, a rating-implied yield (or the interest-coverage synthetic rating). Then × (1 − marginal tax rate). Use market weights for D/V, with debt including leases, the revolver and any debt-like items in the EV bridge (§8).
- Sanity ranges are **spreads over the current 10-yr yield**, not fixed levels (rates move): regulated utilities rf + 2–3%; large-cap staples rf + 3–4%; mega-cap tech rf + 4.5–6%; high-growth/unprofitable tech rf + 6–9%; clinical biotech rf + 7–11% (risk mostly in PoS, not the rate — don't double count). With rf ≈ 4%, mega-cap tech lands at 8.5–10%; with rf ≈ 5%, 9.5–11%.
- Always show ±1% WACC sensitivity — `valuation.py dcf` prints a "WACC swing" line; put it in the memo's valuation section. A conclusion that flips inside ±1% is a low-conviction conclusion.

---

## 3. DCF discipline

- Horizon: 5 years for steady businesses; 10 years for growth businesses that need time to reach steady state. The final explicit year must look like steady state (growth near terminal, positive FCF, stable margins).
- **Reinvestment must fund growth.** Use sales-to-capital (Δrevenue / reinvestment; check the company's history and peers) or explicit capex/D&A/NWC. Terminal reinvestment rate = g / RONIC — growth without reinvestment is free money that doesn't exist.
- Terminal growth ≤ risk-free rate and ≤ long-run nominal GDP (2–3.5% USD). Terminal RONIC: WACC (no moat) to WACC + 10pts (wide moat); >35% needs proof.
- Terminal value share of EV >80% → the explicit period is too short or the steady state is doing all the work. State it.
- **SBC: count it once.** Either treat SBC as a cash expense in FCF (use GAAP EBIT, which includes it) and use today's diluted shares, OR exclude it from costs and project the share count growth. Never exclude it from costs *and* use today's share count.
- Use **core** earnings/FCF from the earnings-normalization skill as the base year, never a distorted GAAP year.
- Working capital sign: sales-to-capital mode treats any revenue decline as capital released (cash in) — right for inventory/receivable-heavy businesses, wrong for **advance-funded** ones, where a decline unwinds customer prepayments and consumes cash. For those use capex mode with a negative `nwc_pct` (ΔNWC/Δrevenue from the last cycle).
- Capex booms: model the depreciation wave. Future D&A ≈ Σ recent capex / useful life. Split capex by asset type when lives differ (`asset_classes`: servers 5–6 yrs, network gear ~10, buildings 20–30+; the PP&E note gives the mix) and add `in_service_lag` when construction in progress is large (assets don't depreciate until placed in service; CIP ÷ annual capex ≈ the lag in years). EBIT margins that ignore a coming D&A step-up are overstated. The calculator's terminal value uses steady-state D&A, so a 10-year horizon no longer bakes boom-vintage depreciation into perpetuity; it prints both margins.

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
- **Time basis.** For a fundamentals-based horizon price, supply each scenario's `dcf` filename and a `horizon_bridge` containing projected `net_cash` and `diluted_shares` plus applicable investments and claims. At the end of year H, the calculator values the remaining FCFF and terminal value using the original DCF timing, then applies the horizon equity bridge. Include all horizon balances in that bridge. For an independent exit-multiple model, supply its `fundamentals_based_target` directly. With `value_today` and cost of equity, the calculator also reports `required_return_rolled_target = value_today × (1 + Ke − DY)^H`. The fundamental target takes priority, followed by an explicit legacy `value`, then the return roll-forward. Each method has a probability-weighted total when available across every scenario. State the basis beside the selected target.
- **Terminal reinvestment.** In vintage mode read `terminal_reinvestment_reconciliation`. Compare T+1 capex less D&A plus incremental working capital with NOPAT × g/RONIC. Report both terminal values and per-share sensitivities when the absolute difference exceeds `terminal_reinvestment_threshold` × absolute T+1 NOPAT (default 5%).
- **Target price** = probability-weighted value at the horizon (default 3 years, the same horizon as the IRR). Annualize the projected return over the full horizon. For example, "+33% target" can still be a below-hurdle investment — judge it by the expected IRR, never by the % upside.
- **Expected IRR** = (prob-weighted value / price)^(1/years) − 1 + dividend yield. Hurdle: long ≥ 15% expected IRR; short ≥ 20–25%.
- **Action price** = the lower of (fair value today × (1 − margin of safety)) and (the max price that still earns the hurdle). This one number goes in the memo header.
- **Margin of safety — one rule.** Start from the quality grade (research-playbook §4 scorecard): **A 15% · B 25% · C 35% · D no position**. Add **+10 points** if the business is cyclical, policy-binary (a regulator or government payer sets price) or levered above ~3.5x net debt/EBITDA; add another +10 if two or more apply. Cap at 50%. State the arithmetic in the memo ("C 35% + policy-binary 10 = 45%").
  - **Cyclical** = revenue fell ≥15% or operating margin fell by a third or more peak-to-trough in any downturn in the company's last 15 years (the sector's, if the company is younger) — or the business is in a sector where that is the norm: energy and materials, capital goods, autos, semis, airlines, homebuilders, discretionary durables, apparel and footwear brands, ad-funded media. Check the company's own history; don't add it because "the consumer is weak".
  - **Policy-binary** = a regulator or government payer sets the price or decides whether the product can be sold (Medicaid/Medicare rates, utility rate cases, drug approvals, licences). A cost-side policy such as tariffs is not policy-binary: model it in the scenarios.
- Skew = (bull − price)/(price − bear). Prefer ≥ 2:1. Size the position for the bear case, not the expected value.
- `valuation.py scenarios` computes all of the above.

---

## 8. EV → equity bridge

Equity = EV + cash & marketable securities + non-operating investments − debt − finance & (for lease-adjusted multiples) operating lease liabilities − minority interests − pension/OPEB deficits − non-convertible preferred − other debt-like items (accrued legal settlements payable, deferred consideration, factoring, residual-value guarantees likely to be called) ± tax assets (if not in FCF).
- **Customer advances / contract liabilities** (project businesses, defense, equipment makers, software with annual prepay): cash on the balance sheet that customers prepaid is not fully the shareholders'. Normal float = contract liabilities ÷ revenue at a mid-cycle level × the revenue you expect to sustain; **excess** float = current contract liabilities − normal float. Deduct the excess as `excess_customer_advances` in the bridge (it unwinds as orders normalize), **or** model the unwind in FCFF with capex mode and a negative `nwc_pct` — never both. Net it against contract assets/unbilled receivables when billing runs ahead the other way.
- Use **post-period** balances: debt raised, equity issued and settlements agreed after the quarter end (8-Ks and prospectuses — 424B5 shows final sizes and over-allotment exercise) belong in the bridge. Enter each as a `capital_actions` row in the dcf/sotp input (shares, cash, claims, source) instead of editing net cash by hand:
  - **Forward equity sale:** add the shares and the settlement cash (shares × forward price, net of fees). If settlement is optional, assume physical settlement.
  - **Mandatory convertible preferred:** add the shares at the conversion rate implied by today's price (between the min and max rates), add the net proceeds as cash, and deduct the PV of the preferred dividends until conversion as a claim. Don't also deduct the preferred as debt.
  - **New debt:** cash in and the same amount as a claim (net zero) unless the proceeds have a stated use.
- **Commitments that aren't yet liabilities:** leases signed but not commenced and purchase commitments are future capex/opex — make sure the DCF's capex and margin paths include them; don't deduct them again. **Residual-value guarantees** (e.g. on leased data centers) are contingent claims: deduct probability × expected shortfall, and show the full amount as a risk.
- **Unaccrued legal penalties and pending judgments:** deduct the expected value (probability × amount × (1 − tax rate if deductible; fines usually aren't)) as a claim; put the full amount in the bear case. Accrued amounts are already on the balance sheet — don't double count.
- **Pending split or stock dividend** (announced, not yet effective): value on the pre-split share count; set `split_factor` so the calculators print post-split values, and show both in the memo header until the effective date.
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
