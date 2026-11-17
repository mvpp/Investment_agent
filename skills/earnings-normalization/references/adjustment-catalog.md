# Adjustment Catalog — what to look for, where it hides, how to treat it

Use this as the sweep list in Step 2. Default class is a starting point; the recurrence test (bottom) decides.
Classes: **R0** true one-off (remove) · **R1** lumpy-recurring (replace with run-rate) · **R2** recurring, keep · **R3** cyclical (replace with mid-cycle) · **TAX** discrete tax item · **EST** accounting-estimate change (disclose; like-for-like only if asked).

## Contents
1. Where to look (search map)
2. Revenue items
3. Operating cost items
4. Non-operating items
5. Tax items
6. Share count
7. Investment-phase segments
8. Accounting-estimate changes
9. Cash-flow-only items
10. Recurrence test & tax-effect rules
11. Company non-GAAP: audit checklist
12. Sector overlays

---

## 1. Where to look (search map)

| Source | What it reveals | How to search |
|---|---|---|
| 8-K Ex-99.1 earnings release & CFO commentary | Management-quantified one-offs ("excluding the X charge, EPS would have been…") | Search "excluding", "one-time", "non-recurring", "charge", "would have been" |
| Earnings call transcript (CFO prepared remarks + Q&A) | Size and nature of items, guidance on what recurs | Search "one-time", "headwind", "benefit", "lapping", "normalize" |
| 10-Q/10-K income statement | Unusual line items, "Other income (expense)" swings | Compare each line's QoQ/YoY change vs revenue change |
| Notes: Income taxes | ETR reconciliation, valuation allowances, discrete items, law changes | "valuation allowance", "discrete", "enactment", "settlement", "excess tax benefit" |
| Notes: Commitments & contingencies / Legal | Accruals, settlements, fines | "accrued", "settlement", "probable", "estimable", "fine", "penalty" |
| Notes: Restructuring / Exit costs | Severance, facility consolidation, lease impairments | "restructuring", "severance", "facilities consolidation", "impairment" |
| Notes: Other income (expense) / Investments | Mark-to-market gains, FX, debt extinguishment | "unrealized gain", "non-marketable equity", "fair value", "remeasurement" |
| Notes: Segment information | Investment-phase segments, reallocations, segment re-definitions | Segment op income table; "reclassified", "recast" |
| Notes: PP&E / Significant accounting policies | Useful-life changes, capitalization policy | "useful life", "change in estimate", "depreciation expense would have" |
| Cash-flow statement (operating section) | Non-cash add-backs, working-capital swings, deferred taxes | Each adjustment line vs prior years |
| MD&A "Results of Operations" | Management's own bridge of changes | "primarily due to", "partially offset by" |
| `scripts/sec_facts.py` output | 5-year / 8-quarter history of candidate tags | Spikes in restructuring, impairment, legal, investment gains, tax |

Start from management's quantified items (they are usually right about *what*), then go hunting for what they did not mention (they are often silent about gains).

---

## 2. Revenue items

| Item | Typical class | Treatment | Notes / examples |
|---|---|---|---|
| Catch-up license / patent settlement revenue (past periods) | R0 | Remove the catch-up portion; keep the go-forward run-rate | Settlement-driven royalty catch-ups at chip licensors |
| Contract termination fees, one-off milestone payments | R0 (or R1 for biotech with steady milestones) | Remove | |
| 53rd week / extra selling days | R0 | Remove ~1/52 of the year's revenue and its profit at incremental margin | Retailers, restaurants |
| Acquired revenue (first 12 months) | — | Not removed from core revenue, but report **organic** growth separately | Growth quality |
| FX translation | R3 | Report constant-currency growth; don't adjust level unless FX is far from normal | |
| Pull-forward / channel fill / price-increase pre-buying | R0 or R3 | Remove the excess vs sell-through; check DSO and channel inventory | Hardware, semis, consumer |
| Election-year / event ad spend | R3 | Normalize over the cycle | Ad platforms, broadcasters |
| Rate-driven interest/reserve income | R3 | Model explicitly at forward-curve rates; show sensitivity | Brokers (cash sweep), stablecoin issuers, payment cos with float |
| Crypto / volatility-driven transaction revenue | R3 | Normalize to mid-cycle volumes | Retail brokers, exchanges |
| Regulatory credits (e.g. emissions credits) | R3 / R0 | Separate; value as a declining stream, not core | EV makers |
| Gross vs net presentation change, ASC 606 transition | EST | Restate prior periods for comparability | |
| Revenue from a customer in distress / related party | flag | Not an adjustment — a quality flag | |

---

## 3. Operating cost items

| Item | Typical class | Treatment | Notes / examples |
|---|---|---|---|
| Restructuring / severance | R0 if first in 5 yrs; else R1 | R1 run-rate = 5-yr average; include facility/lease impairments that belong to the same program | Serial restructurers (every 2-3 years) get no add-back beyond the average |
| Facility consolidation, lease (ROU) impairments | R0/R1 | As above | Big-tech "efficiency" programs |
| Goodwill / intangible impairment | R0 | Remove (non-cash) — but it is evidence of past capital misallocation; note in ROIC | Usually not tax-deductible |
| Legal accruals, settlements, regulatory fines | R1 for mega-caps and regulated businesses | Run-rate = multi-year average; fines usually **non-deductible** (tax rate 0) — see "Legal run-rate" below | For platforms facing continuous antitrust/privacy action, legal cost is a cost of doing business |
| Inventory write-downs from a discrete event (e.g. export ban) | R0 | Remove; but watch for later reversal (gain) when inventory sells | Semis export-control charges |
| Routine inventory obsolescence | R2 | Keep | |
| M&A transaction & integration costs | R0 for rare acquirers; R2 for serial acquirers | | Roll-ups: integration is the business model |
| Amortization of acquired intangibles | R2 in Core EPS | Keep in Core EPS; may exclude in *owner-earnings* view only if no future acquisitions needed to sustain growth | Many company non-GAAP figures exclude it — reverse that |
| Stock-based compensation | **R2 always** | Keep. Exception: one-time IPO RSU catch-up (double-trigger RSUs recognized at IPO) → R0 | It is real dilution; non-GAAP that adds it back overstates earnings |
| Employer payroll tax on equity awards | R2 | Keep | |
| Earn-out / contingent consideration fair-value changes | R0 | Remove (both gains and losses) | |
| Disaster / pandemic / cyber-incident costs | R0 (R1 if recurring exposure) | | Insurers: use cat-load normalization instead |
| Pension mark-to-market (MTM accounting) | R0 | Replace with expected-return basis | Industrials using MTM |
| Gains on sale of PP&E / businesses (recorded in opex) | R0 | Remove (negative adjustment) | |
| Reserve releases (warranty, bad debt, returns) | R3 | Normalize to historical provision rate | Cookie-jar check |

**Legal run-rate — data path.** (1) Pull every quantified legal charge and reversal for 5 years from 8-K releases and 10-Q/10-K notes (`filings.py text <url> --grep "legal|accru|settle"`; the "accrued liabilities" note often has a legal-accruals line). (2) Net reversals against charges in the year they occur. (3) Run-rate = 5-yr net total ÷ 5 (include zero years). (4) If quantification is patchy, bound it: lower = quantified items only; upper = G&A growth in excess of headcount/comp growth; pick within the range and mark `(E)`. (5) Multi-year installment settlements: the accrual is the P&L event (R1 via the run-rate); the cash goes out over years — in core CFO, charge the run-rate cash cost, not the year's actual installment. (6) Contingent amounts not yet accrued: disclose as a risk/EV-bridge item, not in core EPS.

---

## 4. Non-operating items

| Item | Typical class | Treatment |
|---|---|---|
| Unrealized gains/losses on equity securities (marks on private stakes, strategic holdings) | R0 | Remove both directions; value the stakes separately in the EV bridge (avoid double counting) |
| Realized gains on investment sales | R0 | Remove |
| FX remeasurement gains/losses | R3 | Remove if large; usually noise |
| Debt extinguishment gains/losses | R0 | Remove |
| Interest income on excess cash | R2 (rate-sensitive) | Keep, but note sensitivity; for valuation, cash is in the EV bridge — don't capitalize the interest too |
| Equity-method income from affiliates | R2 | Keep, but check whether it is cash (dividends) |
| Warrant / convertible derivative fair-value changes | R0 | Remove |

---

## 5. Tax items

| Item | Class | Treatment |
|---|---|---|
| Tax-law change remeasurement of deferred taxes (e.g. a DTA valuation allowance after a new law) | TAX | Remove full after-tax amount |
| Valuation-allowance establishment/release | TAX | Remove |
| Audit settlements, uncertain-tax-position releases | TAX | Remove |
| Intra-entity IP transfer step-ups | TAX | Remove the one-time benefit; note future cash-tax effect |
| Excess tax benefits/shortfalls from SBC | TAX with `normal_after_tax` (R3-like) | Remove only the excess over the multi-year normal level — they vary with the share price, not the business |
| Structural low rate (foreign-derived income deductions, R&D credits, foreign mix) | R2 | Keep — it is durable unless law changes; flag policy risk |

**Core ETR check:** after adjustments, Core ETR should sit near management's guided rate or the 3-year average ex-discrete items. If not, something is missing.

**Cash taxes vs book taxes:** Bonus depreciation and immediate domestic R&D expensing (restored by the 2025 US tax law) cut **cash** taxes well below book taxes for capex- and R&D-heavy companies for several years. That is a timing benefit (deferred-tax liability builds), so treat the excess cash-tax saving as **R3** in core FCF.
Formula: normalized cash tax = core pretax income × core ETR (minus any *durable* structural deferral you can name). One-off cash item (enter as a **negative** `one_off_cash` amount, since it lowers core CFO) = cash taxes paid − normalized cash tax. Show core FCF both with and without this normalization if it swings the conclusion.

---

## 6. Share count

- Use **diluted** weighted shares; for a GAAP loss, the diluted count excludes anti-dilutive securities — use the fully diluted count (treasury method on options/RSUs, if-converted on converts) when core earnings are positive.
- For forward EPS, project shares: net dilution = SBC grants − buybacks. If buybacks merely offset SBC, there's no shareholder return — note it.
- Watch for share-count bumps from converts crossing conversion price, and from acquisitions paid in stock.
- **Post-period capital actions** (check every 8-K after the period end with `filings.py list`):
  - Forward equity sales / ATM programs: add the shares (and the cash at settlement) to the pro-forma count used for valuation.
  - Mandatory convertible preferred: treat as equity — add the shares at the conversion rate implied by the current price (between the min and max rates), and do not also subtract the preferred as debt; preferred dividends reduce EPS until conversion.
  - Optional converts: if-converted when in the money; otherwise debt.
  - Splits / stock dividends (including new share classes distributed pro rata): restate every per-share number (EPS, target, action price) — state both pre- and post-split values in the memo header until the split is effective.
  - New debt: update net debt in the EV bridge.

---

## 7. Investment-phase segments (discretionary losses)

Examples: an AR/VR hardware segment, "Other Bets", satellite-broadband build-outs, autonomous-driving units.

- **Not non-recurring.** Management can spend this for a decade. Keep in Core EPS.
- Add `"investment": true` (class R2) so `core_eps.py` also prints **Core EPS ex investment segments** — an SOTP input, never the headline.
- In valuation: value the core business on core-ex-investment earnings, then add the investment segment at **option value** (probability × payoff), or subtract the capitalized losses if you believe the money is wasted. State which.
- Track "years of losses × cumulative spend" — capital that could have been returned.

---

## 8. Accounting-estimate changes (EST)

| Change | Effect | Treatment |
|---|---|---|
| Lengthening useful life of servers/network gear | Lowers depreciation → flatters EPS | Disclose the annual uplift (companies usually quantify it in the year of change); show like-for-like EPS; ask whether economic life (AI accelerators especially) supports it |
| Shortening useful life | Raises depreciation | Same, other direction |
| Capitalizing more software/development cost | Shifts expense into capex/amortization | Compare capitalized dev cost / total R&D over time |
| Changing revenue recognition (principal vs agent, bundles) | Level shift | Restate prior periods |
| Changing segment definitions / KPI definitions | Obscures trends | Not an adjustment; a forensic flag |

Rule: estimates are legitimate GAAP, so Core EPS keeps them. The memo states the uplift so the reader knows how much earnings growth is accounting.

---

## 9. Cash-flow-only items (normalizing FCF)

| Item | Treatment |
|---|---|
| Working-capital swings (large deferred-revenue surge, payables stretch, receivable factoring/supply-chain finance) | Normalize ΔNWC to % of Δrevenue (3-5 yr average). Factoring or supplier-finance programs: treat as debt, reverse the CFO benefit |
| Customer-advance inflows (contract liabilities jumping on mega-orders) | Remove the excess over normal float from core CFO (negative `one_off_cash`); in valuation deduct the same excess once (valuation-core §8) — not in both core FCF capitalization and the bridge |
| Legal settlements paid (accrued earlier) | Payment is the cash side of an R1 accrual — use the same run-rate |
| Cash-tax timing (bonus depreciation, R&D expensing, deferred payments allowed by tax authorities) | Normalize cash taxes to a sustainable rate |
| Sale-leaseback proceeds, asset sales | Investing, not operating — check classification |
| **Finance-lease principal** (data centers, equipment) | Subtract from FCF like capex. Many headline "FCF" figures ignore it |
| Capex: maintenance vs growth | Maintenance ≈ D&A (adjust for inflation and for asset-life changes), or Greenwald method: (avg PP&E/Sales) × ΔSales = growth capex; the rest is maintenance. Report total-capex FCF **and** owner earnings |
| SBC | Report FCF **after** SBC (or after the buybacks needed to offset dilution) |
| Capitalized software / contract costs | Treat as operating outflow when comparing FCF across peers |

---

## 10. Recurrence test & tax-effect rules

**Recurrence test (apply to every candidate):**
1. Seen in ≥2 of the last 5 years (any label)? → R1 (run-rate), not R0.
2. Caused by the business model itself (serial acquirer's integration costs, platform's legal costs, retailer's store closures)? → R2.
3. Moves with a macro or market variable (rates, commodity, crypto, FX, share price)? → R3 with a mid-cycle level.
4. Does a gain of the same type get treated symmetrically? If you remove losses, remove gains.
5. Burden of proof is on removal: if the filing text doesn't support "non-recurring", keep it.

**Run-rate for R1:** average of the item over 5 years (include zeros). For big-tech legal costs, a 3-5 year average is a reasonable "cost of doing business".

**Tax effect:**
- Deductible items: use the jurisdiction's marginal rate (US federal 21% + state ≈ 23-25%, or the company's effective marginal rate if disclosed).
- Fines and penalties paid to governments: usually **non-deductible** → tax rate 0.
- Goodwill impairment: usually non-deductible (stock deals) → 0.
- Items in low-tax jurisdictions: use local rate.
- Discrete tax items: already after-tax → class TAX.

**Quality gauges (put the result in the memo):**
- Cumulative 5-yr |adjustments| / cumulative GAAP NI: <10% clean · 10-20% normal · >20% low quality.
- Direction: adjustments that only ever raise earnings → skeptical stance.

---

## 11. Company non-GAAP: audit checklist

When the company does report non-GAAP, rebuild it rather than accepting it:
- Reverse the SBC add-back (and related payroll tax).
- Reverse amortization add-back for serial acquirers.
- Check that gains are excluded, not just losses.
- Compare the gap: (non-GAAP NI − GAAP NI) / GAAP NI. Gap > 50% → investigate deeply; persistent large gap → earnings quality flag.
- Check whether the definition changed this year (new exclusions appearing right when results weaken is a classic flag).
- Check that guidance and consensus are on the same basis as your Core EPS before calling a beat/miss.

---

## 12. Sector overlays

Set `"sector"` in the core_eps input and tag adjustments with `"category"`; the script flags removals that are ordinary business in that sector. The Core EPS definition doesn't change — the overlay tells you which companion metric carries the valuation.

| Sector (`sector`) | Don't remove as one-off (`category`) | Companion metric |
|---|---|---|
| `bank` | securities gains/losses (`investment_gain_loss`), loan-loss provisions (`credit_provision` → R3 through-cycle), hedging (`hedge`) | ROTCE, normalized NCOs, CET1; value on P/TBV |
| `insurance` | investment results (`investment_gain_loss` → R3), reserve development (`reserve_development` → R3), cat losses (`catastrophe_loss` → normalized cat load) | Cat-normalized combined ratio, ROE; P/B |
| `reit` | property depreciation (`property_depreciation`) — use FFO/AFFO as a separate measure, not inside Core EPS | Nareit FFO, AFFO, NAV |
| `commodity` | price swings (`commodity_price`), hedges (`hedge`), LIFO/LCM inventory effects (`inventory_valuation`) → R3 at a mid-cycle price | Through-cycle margins, NAV at a price deck |
| `retail` | store closures (`store_closure`), lease impairments (`lease_impairment`) — R1 run-rate at most | Unit economics, lease-adjusted ROIC |
| `pharma` | acquired IPR&D / licensing (`iprd_licensing`) — recurring pipeline investment | rNPV; cash runway for pre-profit biotech |

Also for SaaS/internet: retained SBC and infrastructure depreciation stay in Core even where Street EPS excludes them; for serial acquirers, deal costs and acquired-intangible amortization are structural (R2).
