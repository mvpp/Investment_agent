# Valuation Model.

All valuation models should match:

* **Cash flow visibility**
* **Capital intensity**
* **Cyclicality**
* **Accounting distortions**
* **Asset vs franchise value**
* **Binary risk**

Below is the most sensible *primary valuation framework* for each of the 20 industries, plus when to adjust.

---

## 1) Software / SaaS

**Primary model:**
→ **Revenue multiple (EV/Revenue) transitioning to DCF (FCF-based)**

**Why:**
Cash flow is back-loaded; margins expand over time. Near-term earnings are distorted by growth reinvestment.

**Best practice:**

* Early stage → EV/Revenue + Rule of 40
* Mid stage → 5–10 year DCF with margin expansion curve
* Mature → FCF yield + ROIC

---

## 2) Internet / Marketplaces / Platforms

**Primary model:**
→ **Unit economics model + Long-term DCF**

**Why:**
Network effects create operating leverage. Near-term profits unreliable.

**Best practice:**

* Value per active user / per GMV
* Model take-rate stabilization
* DCF with long terminal moat assumptions

---

## 3) Hardware / Consumer Electronics

**Primary model:**
→ **Earnings multiple (P/E or EV/EBITDA)**

**Why:**
Margins fairly stable but cyclical; capital moderate.

**Best practice:**

* Mid-cycle EPS multiple
* Normalize for product cycle peaks

---

## 4) Semiconductors

**Primary model:**
→ **Mid-cycle EV/EBITDA + Cycle-normalized DCF**

**Why:**
Highly cyclical; peak multiples misleading.

**Best practice:**

* Normalize margins to mid-cycle
* Stress-test ASP compression

---

## 5) Infrastructure / Utilities / Regulated Assets

**Primary model:**
→ **Dividend Discount Model (DDM) or Regulated Asset Base (RAB) model**

**Why:**
Returns tied to regulated capital base; stable cash flow.

**Best practice:**

* Value equity as growing annuity
* Check allowed ROE vs cost of capital

---

## 6) Energy & Oil & Gas

**Primary model:**
→ **NAV (Net Asset Value) model + Commodity price sensitivity**

**Why:**
Finite reserves; value driven by discounted reserves.

**Best practice:**

* Discount proven reserves (2P)
* Stress oil/gas price scenarios
* Add EV/EBITDA sanity check

---

## 7) Real Estate / REITs

**Primary model:**
→ **NAV (Cap rate-based property valuation) + AFFO yield**

**Why:**
Assets mark-to-market via cap rates.

**Best practice:**

* Value properties at market cap rate
* Cross-check with AFFO multiple

---

## 8) Banks

**Primary model:**
→ **Price-to-Book (P/B) relative to ROE**

**Why:**
Book value approximates earning asset base.

**Core equation insight:**
P/B ≈ (ROE – g) / (Cost of Equity – g)

**Best practice:**

* Focus on sustainable ROTCE
* Adjust for credit cycle

---

## 9) Insurance

**Primary model:**
→ **P/B tied to ROE + Embedded Value model (life insurers)**

**Why:**
Float and reserves drive value.

**Best practice:**

* Combined ratio sustainability
* Investment yield outlook

---

## 10) Pharmaceuticals

**Primary model:**
→ **Risk-adjusted DCF (rNPV) of pipeline**

**Why:**
Patent cliffs + probabilistic drug approvals.

**Best practice:**

* Assign success probability by trial phase
* Model patent expiry explicitly

---

## 11) Biotech (clinical stage)

**Primary model:**
→ **rNPV (probability-adjusted pipeline value)**

**Why:**
Binary outcomes dominate.

**Best practice:**

* Discount per asset
* Add cash balance
* Subtract future dilution

---

## 12) Medical Devices

**Primary model:**
→ **DCF with recurring revenue weighting**

**Why:**
Consumables + moderate growth = stable cash flow.

**Best practice:**

* Model recurring % separately
* Apply premium multiple if sticky

---

## 13) Retail (Brick & Mortar)

**Primary model:**
→ **EV/EBITDA (mid-cycle) + Store-level DCF**

**Why:**
Unit economics matter; cyclicality moderate.

**Best practice:**

* Normalize margins
* Value per store sanity check

---

## 14) E-commerce / DTC

**Primary model:**
→ **Contribution margin model → DCF**

**Why:**
Must prove sustainable unit economics before earnings matter.

**Best practice:**

* Model CAC, repeat rate
* Discount to steady-state margin

---

## 15) Consumer Staples

**Primary model:**
→ **Dividend Discount Model or DCF**

**Why:**
Predictable cash flows; bond-like characteristics.

**Best practice:**

* Value as steady grower
* Emphasize FCF yield vs bonds

---

## 16) Industrials / Capital Goods

**Primary model:**
→ **EV/EBITDA (mid-cycle) + ROIC spread analysis**

**Why:**
Cyclical but durable assets.

**Best practice:**

* Normalize backlog
* Use through-cycle margin

---

## 17) Transportation / Airlines

**Primary model:**
→ **Asset-based valuation + Mid-cycle EV/EBITDAR**

**Why:**
Thin margins, heavy leverage.

**Best practice:**

* Avoid peak EPS multiples
* Adjust for lease liabilities

---

## 18) Materials / Mining

**Primary model:**
→ **NAV (discounted reserves) + EV/EBITDA mid-cycle**

**Why:**
Commodity reserve depletion.

**Best practice:**

* Use long-term commodity price
* Apply country risk discount

---

## 19) Restaurants / Franchised Food

**Primary model:**
→ **Unit economics DCF + EV/EBITDA**

**Why:**
Value tied to store-level ROIC.

**Best practice:**

* Franchise-heavy = higher multiple
* Company-owned = lower multiple

---

## 20) Telecom

**Primary model:**
→ **DCF + Dividend yield model**

**Why:**
Stable cash flows but heavy capex.

**Best practice:**

* Model capex cycle explicitly
* Check spectrum amortization impact

---

## Big Pattern Summary

| Industry Type            | Best Model             |
| ------------------------ | ---------------------- |
| Recurring high-growth    | Revenue multiple → DCF |
| Regulated capital-heavy  | DDM / RAB              |
| Commodity / reserves     | NAV                    |
| Financial intermediaries | P/B tied to ROE        |
| Asset-heavy cyclical     | Mid-cycle EV/EBITDA    |
| Binary R&D               | rNPV                   |

---

# Unified Format for Different Valuation Models

Use a single, industry-agnostic **output format** for *every* valuation model. It’s both human-readable (for reports) and machine-friendly (for spreadsheets / automation). Use the “Report” structure when presenting to humans and the “Workbook / JSON” structure for tooling or batch screening.

## 1) One-line executive summary

* Ticker / Name — Date — Industry — Primary model used — **Fair value: $X.XX / share** — Upside: +YY% vs price — Recommendation (Buy / Hold / Sell)

## 2) Key identifiers & market snapshot (single table)

* Ticker, Company name, Industry, Currency, Report date
* Shares outstanding (diluted), Share price, Market cap, Net debt (cash negative = -), Enterprise value

## 3) Model choice & rationale

* Primary valuation model (e.g., DCF, rNPV, NAV, P/B)
* Secondary checks (e.g., EV/Revenue, EV/EBITDA, NAV)
* Why primary model is appropriate (1–2 short bullets)

## 4) Core assumptions (single table)

* Forecast horizon (years)
* Revenue growth (year0, year1… or CAGR)
* Gross margin / EBITDA margin path (year-by-year)
* Capex (% of sales or $ by year)
* Change in NWC (days or $ by year)
* Tax rate (%)
* WACC / Discount rate (%) — state assumptions & how computed
* Terminal value method & parameters (g-rate OR exit multiple)
* Share count adjustments (options, dilution)

Tip: include a short footnote for each assumption explaining source or justification.

## 5) Forecast (yearly rows; exportable CSV)

Columns: Year | Revenue | YoY % | Gross Profit | Gross Margin % | EBITDA | EBITDA % | EBIT | Tax | NOPAT | Depreciation | Capex | Change in NWC | Unlevered FCF

(Provide 5–10 years depending on industry; keep consistent column order for automation.)

## 6) Valuation arithmetic (clear stepwise)

* Sum PV of explicit period unlevered FCF = $A
* PV of terminal value = $B (show formula: TV = FCF_N * (1+g)/(r-g) OR TV = EBITDA_N * multiple)
* Enterprise value = A + B
* Less: Net debt + other adjustments = Equity value
* Per share fair value = Equity value / diluted shares

## 7) Sensitivity analysis (matrix)

* Show a grid (rows = Discount rates, cols = Terminal growth or Terminal multiple) with resulting per-share price.
* Include simple tornado chart of top 5 drivers (e.g., terminal multiple, long-run margin, year1 growth, WACC, capex intensity).

## 8) Scenario table (Bull / Base / Bear)

For each scenario list the key assumption differences and resulting fair value & upside.

## 9) Comparable multiples & sanity checks

* Peer medians for EV/Revenue, EV/EBITDA, P/E and implied multiples from this valuation.
* Short commentary: “Valuation is X% premium/discount to peers — reason(s).”

## 10) Diagnostics & risk checklist (bullet list)

* Top model risks (3–5 bullets) and what would invalidate the valuation (e.g., regulatory change, patent loss, commodity shock, poor retention).
* Accounting / one-offs to watch (pension, reserves, unusual tax items).
* Liquidity / financing risk (if relevant).

## 11) Key driver break-even points

* e.g., Revenue CAGR needed to justify current market price; Terminal multiple at which recommendation flips.

## 12) Recommendation & trade plan

* One sentence recommendation + 2–3 tactical ideas (e.g., “Add on weakness to $X if ARR growth reverts above 20%” or “Avoid until combined ratio <100%”).

## 13) Deliverables & file structure (spreadsheet / automation)

Recommended workbook (one workbook per company; sheet names):

* Sheet: `00_Metadata` (identifiers & snapshot)
* Sheet: `01_Inputs` (assumptions)
* Sheet: `02_Forecast` (yearly P&L → FCF)
* Sheet: `03_DCF` (discounting steps + TV)
* Sheet: `04_Sensitivity` (matrix)
* Sheet: `05_Scenarios` (Bull/Base/Bear)
* Sheet: `06_Comps` (peer multiples)
* Sheet: `07_Outputs` (fair value, multiples, recommendation)
  Keep all formulas visible and separate raw assumptions from calculated cells.

(You can expand types/names as needed — this is a compact starting schema.)

## 14) Recommended visuals (one-page dashboard)

* Revenue & Margin waterfall (years)
* Unlevered FCF line chart & cumulative PV bar
* Sensitivity heatmap (WACC vs g / multiple)
* Tornado chart of top drivers
* Peer multiples bar chart with implied valuation marker

## 15) Guidelines / defaults (industry-aware)

* Forecast length: 5 years (consumer/industrial/repeatable cash flows); 7–10 years for high growth platform that needs longer convergence; use rNPV per-asset for biotech.
* Terminal choice: use growth rate for stable cash businesses (0–3% depending on geography), use exit multiple for cyclical/commodity where asset multiples are standard.
* Discount rate: pick WACC but show sensitivity ±200–500 bps. For guidance: Regulated/utilities 4–7%; large cap consumer 6–9%; high-growth tech 8–12%; biotech higher due to risk 10–18% (but always show sensitivity).

## Quick exportable CSV headers (Forecast)

Year,Revenue,YoY%,GrossProfit,GrossMargin%,EBITDA,EBITDA%,EBIT,Tax,NOPAT,Depreciation,Capex,ChangeInNWC,UnleveredFCF

---
