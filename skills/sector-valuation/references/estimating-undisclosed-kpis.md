# Estimating Undisclosed KPIs

Most of the drivers that matter (CAC, LTV, churn, unit costs, reserve quality) are disclosed only partially or not at all. A rough estimate with a stated range and confidence beats ignoring the driver and falling back on P/E. The goal is a **range good enough to change a decision**, not false precision.

## The triangulation ladder (use at least two rungs; report which)

| Rung | Source | Confidence |
|---|---|---|
| 1 | Direct disclosure (10-K/10-Q KPI tables, investor-day slides, S-1 cohort charts) | A |
| 2 | Derived from disclosed financials with a formula (below) | A– / B |
| 3 | Management commentary (calls, conferences, investor days) — "payback under 2 years", "churn in the single digits" | B |
| 4 | Peer disclosure: same business model, similar scale/customer type (one peer's S-1 often discloses what the incumbent hides) | B / C |
| 5 | Industry survey benchmarks (see source list) | C |
| 6 | Alternative data: app downloads/MAU (Sensor Tower, data.ai), web traffic (Similarweb), job postings, card-spend panels, satellite, shipping/customs, store counts, rig counts | C |
| 7 | First-principles bottom-up (price × units × utilization; physics/engineering constraints) | C |

Rules:
- If two rungs disagree by >30%, widen the range and say so; don't average them silently.
- Label every estimated KPI in the memo: `NRR ~108–113% (E, B: derived from cRPO growth vs revenue growth + mgmt "above 110%")`.
- Benchmarks are bounds, not answers: use them to reject impossible estimates, then lean on company-specific evidence.
- Benchmarks drift. The numbers in the sector playbooks are rough 2024–26 ranges for sanity checks; fetch the latest survey before relying on one.

## Generic derivation formulas

| Want | Derive from |
|---|---|
| ARR | Subscription revenue (last quarter) × 4; or cRPO trend |
| Net new ARR | ARR_t − ARR_{t−1} |
| Customers / users | Revenue ÷ disclosed ARPU/ARPA; or disclosed "customers > $100k" cohorts scaled by a peer's distribution |
| Gross churn | 1 − GRR if disclosed; else from NRR − expansion estimate; else peer/benchmark by segment |
| Implied NRR (when only revenue is known) | (Revenue_t − revenue from new customers_t) / Revenue_{t−1}; new-customer revenue ≈ new logos × starting ARPA |
| CAC (blended) | S&M_{t−1} (one-quarter lag) ÷ new customers_t; for new-logo CAC, allocate 60–80% of S&M to new business unless disclosed |
| CAC payback (months) | S&M_{t−1} ÷ (net new ARR_t × gross margin) × 12 |
| Magic number | (ΔQuarterly revenue × 4) ÷ S&M_{t−1}; >0.75 efficient, <0.5 inefficient |
| LTV | ARPA × GM ÷ churn (simple, cap lifetime at 5–7 yrs); or `valuation.py ltv` (discounted, with expansion) |
| Unit cost | Segment opex ÷ volume (e.g. lease operating expense ÷ boe; fulfillment cost ÷ orders) |
| Maintenance capex | D&A adjusted for asset-life changes and inflation; or Greenwald: growth capex = (PP&E/Sales) × ΔSales |
| Incremental margin | ΔEBIT ÷ ΔRevenue over 4–8 quarters |
| Pricing vs volume | Revenue growth decomposed using disclosed volumes (impressions, units, shipments, transactions) |
| Take rate | Revenue ÷ GMV/TPV (disclosed or estimated from alt data) |
| Capacity / utilization | Revenue ÷ (capacity × price); industry utilization from trade associations |
| Remaining inventory (E&P) | Undeveloped locations (investor decks) × EUR per well (state/permitting databases, peer type curves) × risk factor |

## Benchmark source directory (fetch fresh)

| Domain | Sources |
|---|---|
| Cross-industry multiples, betas, margins, ROIC, sales-to-capital | Damodaran Online datasets (NYU Stern), updated each January |
| Public SaaS metrics (growth, NRR, multiples, Rule of 40) | Clouded Judgement (Jamin Ball, weekly), Meritech public comps, Bessemer "State of the Cloud", company S-1s |
| Private SaaS benchmarks (CAC payback, churn by segment) | KeyBanc/Sapphire SaaS survey, ICONIQ Growth "Topline Growth & Operational Efficiency", OpenView/SaaS Capital |
| Consumer apps / subscriptions | Sensor Tower, data.ai, RevenueCat "State of Subscription Apps" |
| E-commerce / marketplaces | Marketplace Pulse, company S-1s, Census e-commerce data |
| Ads | eMarketer/Insider Intelligence, IAB/PwC ad revenue report, company KPI disclosures (impressions, price per ad) |
| Semis | SIA, SEMI (WFE, book-to-bill), WSTS, TrendForce |
| Oil & gas | SEC 10-K supplemental oil & gas data (ASC 932), EIA, Dallas Fed Energy Survey (breakevens), Enverus/state well data |
| Mining | Company technical reports (NI 43-101 / S-K 1300), World Gold Council (AISC), USGS |
| Banks | FDIC Quarterly Banking Profile, Fed stress-test results, company NII-sensitivity tables |
| Insurance | NAIC, AM Best, Schedule P reserve triangles |
| REITs | Nareit T-Tracker, CBRE/Green Street cap-rate surveys |
| Utilities | State PUC rate cases, EEI, RRA allowed-ROE data |
| Biopharma | BIO/Informa/QLS clinical success rates, FDA approvals, IQVIA, Evaluate Pharma consensus peak sales |
| Retail/restaurants | Company FDDs (Franchise Disclosure Documents: AUVs, unit economics), Placer.ai traffic |
| Airlines | DOT/BTS T-100, A4A |
| Macro | FRED, BLS, BEA, Census |
