# Forensic Accounting Checklist (accounting aggressiveness score 1–10)

Framework: Howard Schilit, *Financial Shenanigans* (CFRA approach), plus standard quantitative screens. Review 5 years of statements, footnotes and MD&A. Output one score and at most 3 flags for the memo; keep the rest in workpapers.

## A. Earnings manipulation (EM)
| # | Shenanigan | What to check |
|---|---|---|
| EM1 | Recording revenue too soon | DSO trend vs revenue growth; unbilled receivables growth; bill-and-hold; percentage-of-completion estimates; long-term contracts recognized up front |
| EM2 | Recording bogus revenue | Related-party / round-trip sales; barter; revenue from customers financed by the company; vendor financing |
| EM3 | Boosting income with one-time or unsustainable activities | Gains in operating income; reclassifying gains into revenue; reserve releases; investment gains supporting EPS growth |
| EM4 | Shifting current expenses to a later period | Capitalizing operating costs (software, customer acquisition, contract costs); lengthening depreciation lives; under-reserving |
| EM5 | Other techniques to hide expenses or losses | Off-balance-sheet vehicles; unconsolidated entities; aggressive pension assumptions |
| EM6 | Shifting current income to a later period | Cookie-jar reserves built in good years, released in bad years; deferred revenue manipulation |
| EM7 | Shifting future expenses into the current period | "Big bath" restructuring charges that later reverse; excessive write-downs before a new CEO's baseline |

## B. Cash-flow manipulation (CF)
| # | Shenanigan | What to check |
|---|---|---|
| CF1 | Shifting financing inflows into operating | Receivable factoring / securitization; supplier finance programs stretching payables |
| CF2 | Shifting normal operating outflows into investing | Capitalized software or content spend in investing; "purchases of intangible assets" that are really operating |
| CF3 | Inflating CFO via acquisitions or disposals | Acquired working capital boosting CFO; selling receivables with a business |
| CF4 | Boosting CFO with unsustainable activities | Delaying payables; cutting inventory sharply; one-off customer prepayments; tax deferrals |

## C. Key-metrics manipulation (KM)
| # | Shenanigan | What to check |
|---|---|---|
| KM1 | Showcasing misleading metrics | KPI definition changes (users, ARR, bookings, "AI revenue"); dropping a KPI once it weakens; adjusted metrics excluding recurring costs |
| KM2 | Distorting balance-sheet metrics | Window-dressing at quarter end; reclassifying debt; hiding leverage in leases or factoring |

## D. Acquisition-accounting manipulation (AA)
| # | Shenanigan | What to check |
|---|---|---|
| AA1 | Boosting revenue/earnings through acquisitions | Organic growth not disclosed; deferred-revenue write-downs; reserves set up at acquisition then released |
| AA2 | Inflating CFO through acquisitions | Acquired receivables collected as CFO; acquisition spend in investing while organic would be opex |
| AA3 | Manipulating metrics around acquisitions | Pro-forma comparisons; frequent segment re-cuts |

## E. Quantitative screens
| Screen | Formula | Flag level |
|---|---|---|
| Accrual ratio (Sloan) | (NI − CFO) / avg total assets | > 10% for 2+ years |
| CFO / NI | 3-yr sum | < 0.8 persistently (ex high-growth working-capital builds) |
| FCF-after-SBC / Core NI | 3-yr sum | < 0.5 needs an explanation (capex cycle is a valid one — say so) |
| DSO change vs revenue growth | ΔDSO | DSO rising >10% YoY while growth slows |
| Inventory days | ΔDIO | Rising inventory days with falling gross margin = write-down risk |
| Deferred revenue vs revenue | growth gap | Deferred revenue shrinking while revenue grows = pulled-forward recognition |
| Capitalized costs | capitalized dev cost / R&D; contract cost assets / revenue | Rising share |
| Depreciation / gross PP&E | trend | Falling rate = longer lives |
| Reserve ratios | allowance / receivables; warranty reserve / revenue | Falling while risk rises |
| Non-GAAP gap | (non-GAAP − GAAP NI) / GAAP NI | > 50% |
| SBC / revenue | | > 15% for mature companies |
| Beneish M-score (optional) | 8-variable model | > −1.78 suggests manipulation risk |

## F. Governance & audit signals
- Auditor change, auditor resignation, adverse/qualified opinion, critical audit matters that are new.
- Material weakness in internal controls; late filings (NT 10-K/10-Q); restatements.
- CFO or chief accounting officer turnover, especially near year-end.
- SEC comment letters (EDGAR "CORRESP"/"UPLOAD") on revenue recognition or non-GAAP.
- Related-party transactions; founder-controlled entities transacting with the company.
- Insider selling outside 10b5-1 plans ahead of weak results.
- Short-seller reports: read them, test each claim against filings, record which ones survive.

## Scoring rubric
| Score | Meaning |
|---|---|
| 1–2 | Conservative: GAAP close to cash, few adjustments, clean audit, adjustments symmetric |
| 3–4 | Normal: some estimate choices favor earnings, fully disclosed |
| 5–6 | Moderately aggressive: several favorable estimates (lives, capitalization), non-GAAP gap large, metrics redefined |
| 7–8 | Aggressive: multiple EM/CF flags, persistent CFO < NI without explanation, frequent "one-offs" |
| 9–10 | Red alert: restatement risk, governance failures, related-party revenue — do not invest without resolution |

Write the score with the two or three facts that drove it. "4/10 — depreciation-life extension added ~X% to EPS; CFO/NI healthy; no audit issues."
