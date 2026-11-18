# Technology Playbooks

Software/SaaS · Consumer subscription · Ad platforms · Marketplaces · E-commerce (1P) & DTC brands · Semiconductors · Hardware & devices · AI infrastructure & neoclouds

Each block: value equation → KPIs that move value → how to estimate if undisclosed → sanity benchmarks (approximate 2024–26 ranges; refresh before relying) → valuation → traps.

---

## Software / SaaS

**Value equation:** Value = value of existing customers (ARR × GM × expected lifetime, with expansion) + value of future cohorts (new ARR × (LTV − CAC)) − corporate costs, all after SBC.

**KPIs:** ARR & net new ARR · NRR and GRR · CAC payback / magic number · gross margin (subscription) · FCF margin and SBC % revenue · Rule of 40 (growth + FCF margin) · cRPO/RPO growth vs revenue growth · seat vs consumption mix · AI-attached revenue.

**If undisclosed:**
- ARR ≈ subscription revenue × 4; net new ARR from the change.
- CAC payback = S&M_{t−1} ÷ (net new ARR × GM) × 12.
- NRR from management phrases ("above 110%"), cohort charts in S-1, or cRPO growth − new-logo contribution.
- Churn by customer type when nothing is disclosed: SMB ~15–30%/yr gross, mid-market ~8–15%, enterprise ~5–10%.
- LTV/CAC via `valuation.py ltv`.

**Sanity benchmarks (public SaaS, refresh via Clouded Judgement/Meritech):** median revenue growth mid-teens; median NRR ~105–112% (top quartile >120%); median GRR ~88–92%; subscription GM 75–82%; CAC payback 20–35 months (median), <18 best-in-class; Rule of 40 median ~25–35; SBC 10–25% of revenue (lower for mature); mature steady-state FCF margin 25–35% (after SBC ~15–25%).

**Valuation — the method changes with the company's stage:**
- **Early** (growth >30%, FCF ≈ 0 or negative): customer-based valuation — cohort LTV − CAC (`valuation.py ltv`) × new customers the S&M budget buys — plus a scenario DCF (each scenario with a survival/success probability). Rule of 40 is a quality gate here, not a price; EV/NTM revenue vs growth-matched peers is context only.
- **Scaling** (growth ~15–30%, margins rising): 10-yr DCF in **incremental-margin mode** (`margin0` = core EBIT margin, `incremental_margin` from Δcore EBIT ÷ Δcore revenue over 4–8 quarters, `margin_cap` at the steady state of peers at scale; `examples/dcf_incremental.json`). Reverse DCF for implied growth.
- **Mature** (growth <15%, stable FCF): DCF still anchors, cross-checked by FCF yield after SBC + sustainable growth ≈ expected return (compare with the hurdle), ROIC on incremental capital including acquisitions, and P/E on core EPS.

At every stage, cross-check EV/NTM revenue against a regression on growth + FCF margin across peers — but that regression and Rule of 40 price **current** margins. When the incremental margin is far above the current one (e.g. 5% EBIT margin, 40%+ on new revenue), they call the stock expensive by construction; that is exactly when the incremental-margin DCF should override them. State the incremental margin and its evidence in the memo.

**Traps:** non-GAAP margins that exclude 20% SBC; "ARR" definitions that include usage or one-off services; NRR boosted by price increases that churn later; seat-based models exposed to AI headcount compression; capitalized commissions (ASC 340-40) flattering S&M; multi-year prepaid deals inflating RPO.

---

## Consumer subscription (streaming, music, apps)

**Value equation:** Subscribers × ARPU × (1 − churn) − content/royalty cost − marketing; value = steady-state margin × subscriber base × lifetime.

**KPIs:** paid net adds by region · ARPU (FX-neutral) · monthly churn · content cash spend vs content amortization · gross margin (royalty-bound for music) · ad-tier mix · price-increase elasticity.

**If undisclosed:** churn from third-party panels (Antenna) or survival curves implied by gross adds vs net adds; content cash vs P&L from the cash-flow statement (content asset additions vs amortization).

**Benchmarks:** monthly churn: leader streaming ~2%, subscale streamers 5%+; music GM ~25–35% (royalty-capped).

**Valuation:** DCF on FCF (content cash spend, not amortization); P/E on core EPS; value per subscriber vs peers as a check.

**Traps:** content amortization curves that lag cash spend (earnings flattered in growth years); password-sharing crackdowns as one-off subscriber boosts; FX on international ARPU.

---

## Ad-supported platforms (social, search, video, ad-tech)

**Value equation:** Users × engagement (time) × ad load × price per ad (CPM, which reflects ROI to advertisers — measurement, targeting and AI ranking) − traffic acquisition/infra cost − investment segments.

**KPIs:** DAU/MAU (or "daily active people") by region · ARPU by region · ad impressions growth vs price-per-ad growth (decompose revenue) · time spent per user · conversion/measurement quality (signal loss) · TAC % (search) · capex/revenue and D&A trajectory · investment-segment losses.

**If undisclosed:** impressions vs price split from mgmt commentary; regional ARPU from segment geography notes ÷ users; capex-driven D&A wave = Σ recent capex / useful life (servers 5–6 yrs).

**Benchmarks:** best-in-class mega-cap ad platforms run 35–45%+ operating margins in the core business; capex intensity at the hyperscale ad platforms rose from ~10–15% of revenue pre-2023 to 30%+ in 2025–26 (AI infrastructure).

**Valuation:** P/E (or EV/EBIT) on **core EPS** from earnings-normalization; DCF with explicit capex/D&A path; **SOTP** when an investment segment exists (core apps on core-ex-investment EBIT × justified multiple + investment segment at option value). Cross-check: value per DAP vs peers; reverse DCF.

**Traps:** GAAP quarters with giant discrete tax charges or legal accruals; useful-life extensions flattering EPS during the capex boom; regulatory (DMA, privacy, antitrust) drag treated as one-off; ad-tech take-rate compression; counting AI capex as "growth" forever without asking for a return (incremental ROIC on capex).

---

## Marketplaces (3P)

**Value equation:** GMV × take rate × contribution margin − fixed costs; GMV = buyers × frequency × order value.

**KPIs:** GMV / gross bookings growth · take rate (and ads/fintech attach) · contribution margin per order · buyer cohort repeat rate · CAC and payback · supply-side liquidity (sellers, utilization).

**If undisclosed:** take rate = revenue ÷ GMV (GMV from S-1/alt data); contribution per order from (gross profit − variable marketing/incentives) ÷ orders; repeat from cohort charts or app retention data.

**Benchmarks:** take rates 10–20% (incl. ads) for e-commerce, 15–30% for services/travel; contribution margin per transaction >15% at scale.

**Valuation:** DCF from GMV × take rate × steady-state margin (incremental-margin mode once contribution is positive); EV/gross profit vs peers; for unprofitable names, scenario DCF.

**Traps:** EV/GMV across different take-rate models; gross vs net revenue presentation; incentives booked as contra-revenue vs marketing; ads revenue growth masking core marketplace stagnation.

---

## E-commerce (1P) & DTC brands

The company owns the inventory, so there is no take rate: value is decided by what each order and each customer cohort leaves after fulfillment and the marketing that bought them.

**Value equation:** Orders × AOV × contribution margin per order (gross margin − fulfillment & shipping − payment − variable marketing) − fixed costs; customer value = Σ cohort contribution over its life − CAC.

**KPIs:** active customers and cohort repeat rate (orders per customer by acquisition year) · AOV · gross margin · fulfillment + shipping % of sales · contribution margin after marketing · CAC and payback · marketing split (acquisition vs retention) · return rate · inventory turns and markdowns · channel mix (own site vs Amazon vs wholesale).

**If undisclosed:**
- CAC ≈ acquisition marketing ÷ new customers; new customers ≈ active_t − active_{t−1} × retention (retention from cohort charts or "% of revenue from returning customers").
- Contribution margin = (gross profit − fulfillment − payment fees − performance marketing) ÷ revenue, rebuilt from 10-K cost lines (shipping and fulfillment often sit in opex, not COGS).
- LTV with `valuation.py ltv` using **contribution margin** (not gross margin) as `gross_margin`, annual orders × AOV as `arpa`, and 1 − repeat rate as `annual_churn`.

**Benchmarks:** repeat purchase >30%; contribution margin after marketing >10%; CAC payback <12 months; DTC gross margins 50–70%, of which fulfillment + marketing commonly absorb 35–50 points; 1P generalist retailers earn low-single-digit EBIT.

**Valuation:** contribution-margin build → DCF. Revenue = retained cohorts + new customers (acquisition budget ÷ CAC); steady-state margin = contribution at mature marketing spend (mostly retention) − fixed costs; reach it with incremental-margin mode. Cross-check EV/gross profit vs peers and, once profitable, EV/EBITDA vs mature retail.

**Traps:** blended CAC hiding worsening new cohorts; "contribution margin" quoted before marketing; free shipping and returns buried in opex; growth from wholesale or Amazon that lifts revenue but cuts margin and customer ownership; dependence on paid-social ad prices; inventory build and markdowns.

---

## Semiconductors & semicap

**Value equation:** Units × ASP × GM through the cycle; design-win share determines units 2–4 years out.

**KPIs:** revenue vs end-market (data center, PC, mobile, auto, industrial) · inventory days (company and channel) · book-to-bill / backlog · gross margin vs utilization · customer concentration (hyperscalers) · design wins · capex/sales (IDMs) · WFE share (semicap) · export-control exposure.

**If undisclosed:** channel inventory from distributors' filings; hyperscaler capex guides as top-line driver for AI names; ASP × units splits from teardown/industry trackers (TrendForce).

**Benchmarks:** inventory days rising >20% with falling GM = downturn; book-to-bill <1 for 2 quarters = cycle turn; fabless GM 55–75% at mid-cycle; IDM capex/sales 20–40% in build phases.

**Valuation:** mid-cycle (normalized) EPS × mid-cycle P/E; cycle-normalized DCF (average margins over a full cycle); for AI leaders, explicit scenarios on data-center capex and share. Use industry-deepdive second-derivative signals (capex/D&A, utilization) to place the cycle.

**Traps:** peak EPS × peak multiple; customer concentration and in-sourcing (custom ASICs); export-control charges (R0 in core EPS but a structural risk in valuation); inventory write-down reversals.

---

## Hardware & devices

**Value equation:** Installed base × (hardware replacement rate × ASP × GM) + installed base × services ARPU × services GM.

**KPIs:** installed base (active devices) · upgrade cycle length · hardware GM · services revenue/ARPU and attach · inventory turns · warranty/returns.

**If undisclosed:** installed base from mgmt milestones and replacement-cycle math (units sold over N years × survival); services ARPU = services revenue ÷ installed base.

**Benchmarks:** inventory turns >4x; services GM typically 2x hardware GM.

**Valuation:** P/E on core EPS (mid-product-cycle); SOTP hardware vs services (services deserve software-like multiples only if recurring and defensible).

**Traps:** product-cycle peaks; regulatory risk to services (app-store, default-search payments); tariff-driven pull-forward.

---

## AI infrastructure, data centers & neoclouds

**Value equation:** Contracted capacity (MW / GPUs) × price per unit-hour × utilization − power & opex − depreciation over the true economic life − financing cost.

**KPIs:** contracted backlog and tenor · customer concentration · $/MW build cost · power secured (GW) and timing · utilization · GPU depreciation life assumed vs economic life · cost of debt/lease financing · incremental ROIC on capex (for hyperscalers).

**If undisclosed:** revenue per GPU-hour × fleet size × utilization; build cost from peer disclosures and project announcements; depreciation sensitivity with 4 vs 6-year lives.

**Valuation:** contracted-cash-flow DCF (backlog at contract terms, then re-contracting risk) + EV/EBITDA vs infra peers; for hyperscalers, ROIC on incremental invested capital — capex that doesn't earn > WACC destroys value no matter how fast revenue grows.

**Traps:** depreciation lives longer than the chip's economic life (earnings flattered); vendor financing and circular deals (supplier invests in customer who buys supplier's chips); backlog with weak counterparties; power-interconnection delays; financing leases hiding leverage.
