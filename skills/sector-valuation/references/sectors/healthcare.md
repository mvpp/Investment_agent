# Healthcare Playbooks

Large-cap pharma · Clinical-stage biotech · Medical devices · Life-science tools · Managed care · Home & community care · Hospitals & outsourced providers

---

## Large-cap pharma

**Value equation:** Base business (marketed products through loss of exclusivity) + risked pipeline (rNPV) − LOE cliffs − IRA price negotiation − corporate costs.

**KPIs:** revenue concentration (top product %) · patent/LOE schedule by product and region · pipeline by phase and indication · R&D productivity (approvals per $B R&D) · gross margin · IRA negotiation selections · business-development spend (acquired IPR&D).

**If undisclosed:** product-level revenue is usually disclosed; LOE dates from 10-K patent tables + Orange/Purple Book; consensus peak sales from Evaluate/sell-side; PoS by phase defaults in `valuation.py rnpv` (BIO/Informa 2011–2020: Phase I→approval ~7.9%, Phase II ~15%, Phase III ~52%, filed ~91%; oncology lower, hematology/rare higher).

**Benchmarks:** small-molecule revenue typically falls ~80–90% within 1–2 years of generic entry; biologics erode more slowly (biosimilars ~30–60% over 3 years). US IRA: negotiated prices can apply ~9 years post-approval for small molecules and ~13 years for biologics.

**Valuation:** DCF of base business with explicit LOE erosion + rNPV of pipeline (`valuation.py rnpv`); cross-check P/E on core EPS (note: acquired IPR&D expense is lumpy — R1 for serial dealmakers, not R0).

**Traps:** P/E ignoring a 2–4 year patent cliff; treating acquired IPR&D as one-off every year; peak-sales consensus anchored on management; IRA and MFN pricing policy shifts.

---

## Clinical-stage biotech

**Value equation:** Σ risked asset NPVs + net cash − PV of corporate burn − expected dilution.

**KPIs:** cash runway (months) · burn rate · catalyst calendar (readouts, PDUFA dates) · asset quality (mechanism validation, competitive landscape, differentiation) · partnership economics.

**Valuation:** rNPV per asset with phase PoS adjusted for indication and mechanism validation; scenario tree around binary readouts; enterprise value vs cash (negative EV = market pricing failure).

**Traps:** using company peak-sales guidance; ignoring dilution (runway <18 months → raise likely); single-asset binary risk sized as if diversified.

---

## Medical devices

**Value equation:** Procedures × penetration × share × ASP; recurring consumables (razor/blade) drive predictability.

**KPIs:** procedure volume growth · recurring/consumables % revenue · installed base and utilization · reimbursement codes and changes · ASP trends · new-product cycle · R&D %.

**If undisclosed:** procedure volumes from CMS data, hospital surveys, peer commentary; installed base × utilization × disposables per procedure.

**Benchmarks:** recurring >25% of revenue = sticky; gross margins 60–70%+ for differentiated devices.

**Valuation:** DCF with recurring revenue modeled separately (premium for stickiness); EV/EBIT vs peers; growth-adjusted P/E.

**Traps:** recalls (R1 for large device companies); reimbursement cuts; GLP-1-type demand shocks for adjacent procedures.

---

## Life-science tools & diagnostics

**Value equation:** Installed instruments × consumables pull-through; customer mix (pharma, biotech funding, academic/government, China).

**KPIs:** consumables % revenue · instrument orders (leading) · biotech funding cycle · academic/NIH budgets · China exposure.

**Valuation:** P/E / DCF through-cycle; normalize COVID-type windfalls (R0/R3).

---

## Managed care (health insurers)

**Value equation:** Members × premium × (1 − medical loss ratio − admin ratio) + services segments.

**KPIs:** MLR vs guidance (utilization trends) · membership mix (Medicare Advantage, Medicaid, commercial) · star ratings / risk-adjustment changes · PBM/services margins.

**Valuation:** P/E on normalized MLR; SOTP for services businesses.

**Traps:** MA rate notices and risk-adjustment model changes; utilization surprises; PBM regulatory reform.

---

## Home & community care (private-duty nursing, home health, hospice, personal care)

**Value equation:** Hours or episodes × payer rate − caregiver wage & benefits − branch/corporate overhead. The unit of value is the **spread per hour** (rate per hour − wage cost per hour) for hourly services, and the **margin per episode/admission** for home health and hospice. Government payers (state Medicaid/MCOs, Medicare) set the rate; the labor market sets the wage.

**KPIs:** revenue and gross margin by service line · hours (or episodes/admissions) growth, organic vs acquired · rate per hour vs wage per hour → spread per hour and its trend · payer mix (Medicaid FFS, Medicaid MCO, Medicare, commercial) and **preferred-payer** contract share · state concentration (top states % of revenue) and the state budget/rate calendar · caregiver headcount, hiring and turnover · Medicare home-health/hospice final rules (annual) · days sales outstanding · leverage (net debt / adj. EBITDA) and floating-rate exposure, hedges and their expiry.

**If undisclosed:**
- Spread per hour = (service-line revenue − cost of service) ÷ hours, when hours are disclosed; otherwise infer hours from revenue ÷ published state rates for the main states.
- Rate tailwinds: state Medicaid budget documents and enacted rate increases (state legislature/Medicaid agency notices); management lists the states on calls.
- Wage pressure: BLS home-health-aide / LPN / RN wage series by state; minimum-wage schedules.
- Policy exposure: share of revenue in states affected by federal Medicaid financing changes (provider-tax limits, FMAP changes) and by HCBS rules that mandate a share of payments go to direct-care wages (pass-through rules cap the spread).

**Benchmarks:** private-duty/personal-care gross margins ~25–35%; home health ~45–50%; adjusted EBITDA margins ~8–15% for scaled operators. Leverage above ~4x with floating debt makes equity value highly rate-sensitive.

**Valuation:** 10-yr FCFF DCF on **core** EBIT (SBC expensed; serial-M&A costs kept — R2), with explicit scenarios for the payer rate path. Cross-check EV/adjusted EBITDA vs listed home-care peers, adjusted for leverage and payer mix. Treat acquisitions as value-neutral unless acquired ROIC demonstrably beats WACC. Bridge: subtract securitization/receivable facilities and finance leases as debt; value hedges at their remaining life, not forever.

**Traps:** capitalizing a single year of large state rate increases; ignoring wage pass-through mandates that convert rate increases into wages; valuation-allowance releases inflating GAAP EPS once the company turns profitable; hedge income from caps that are about to expire; adjusted EBITDA that excludes recurring acquisition/integration costs; state budget cycles (rates can be cut as easily as raised).

---

## Hospitals & outsourced providers

**KPIs:** volumes (admissions, adjusted admissions), payer mix, labor cost per adjusted admission, same-facility growth, supplemental Medicaid payments.
**Valuation:** 10-yr FCFF DCF on core earnings (calculator), cross-checked with lease-adjusted EV/EBITDA and FCF yield vs peers.
**Traps:** policy-dependent supplemental payments (R3), labor inflation, sale-leaseback gains (R0).
