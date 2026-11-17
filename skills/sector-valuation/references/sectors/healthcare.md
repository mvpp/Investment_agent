# Healthcare Playbooks

Large-cap pharma · Clinical-stage biotech · Medical devices · Life-science tools · Managed care · Providers/services

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

## Providers & services (hospitals, outsourcing)

**KPIs:** volumes, payer mix, labor cost per adjusted admission, same-facility growth.
**Valuation:** EV/EBITDA (lease-adjusted), FCF yield.
**Traps:** policy-dependent supplemental payments (R3), labor inflation.
