# Research Playbook — the work behind the memo

The memo is short; the research isn't. Each pass below produces **workpaper notes** (keep them in the conversation, or in `workpapers.md` if the user wants a file). Only conclusions that change the target price, the rating or the kill conditions get promoted into the memo.

## Contents
1. Evidence standards
2. Pass A — Fact base (business, history, management)
3. Pass B — Industry structure
4. Pass C — Competitive position & quality
5. Pass D — Key Forces
6. Pass E — Expectations (consensus & variant view)
7. Pass F — Red team (hidden risks, devil's advocate, six lenses, pre-mortem, thesis check)
8. Pass G — Decision rules

---

## 1. Evidence standards

**Verification hierarchy (cite the highest tier available):**
1. SEC filings: 10-K, 10-Q, 8-K (earnings releases Ex-99.1), DEF 14A (management, pay), S-1, Forms 3/4 (insiders), 13F (holders).
2. Earnings-call transcripts, investor-day decks, company IR.
3. Regulators/courts/government data (FDA, FCC, FERC, DOJ/FTC, EIA, Census).
4. High-reputation industry sources (trade associations, consultancies, industry trackers).
5. News and sell-side — usable for consensus and color, never the sole basis for a thesis-critical fact.
Primary evidence (customer reviews on G2/App Store, employee reviews on Glassdoor/Blind, job-posting counts, patents, app download/usage estimates, expert-call transcripts the user provides) is gold for competitive questions. Aim for three data points tied to the Key Forces; time-box it (a few targeted searches), and if you couldn't get them, say so in Sources rather than padding with company-reported figures.

**Citation format (inline, compact):** `[10-Q Q3'26, Note 12]`, `[Q3'26 call, CFO]`, `[DEF 14A 2026]`. Label `(E)` estimated, `(I)` inferred. Flag `⚠ verify` when a number could not be confirmed in a primary source. Never invent a quote, number, or source — say "not disclosed" instead.

**Freshness:** search for the latest filings, price and consensus at the start. State the "as of" date. Anything from model memory is a hypothesis to verify.

---

## 2. Pass A — Fact base

Answer briefly, with citations:
- **What it sells, to whom, how it gets paid** (revenue model: recurring, transactional, usage, licensing, spread, commodity).
- **Segment table:** revenue, growth, operating margin, share of total, and (later) share of value.
- **Customers:** concentration (top-10 %), geography, end markets.
- **History:** founding thesis → 3–5 inflection points (pivots, acquisitions, crises) → how they shaped today's position. Last 10 years: what management said it would do (annual letters/MD&A) vs what actually happened. **What went to plan and what didn't** is the best management-credibility test available.
- **Management & governance:** CEO/CFO tenure and background; pay design (what metrics drive bonuses — EPS? ROIC? revenue?); insider ownership and recent Form 4 activity (10b5-1 vs discretionary); dual-class control; board independence; related-party dealings.
- **Capital allocation record:** ROIC on past acquisitions, buybacks (price paid vs intrinsic value), dividend policy, SBC dilution net of buybacks.

---

## 3. Pass B — Industry structure

For a full industry study, use the sibling `us-industry-deepdive` skill. For the memo, a compressed version:
- **Stage:** introduction / growth / maturity / decline, with the penetration denominator stated.
- **Five forces scorecard** (each Strong/Moderate/Weak, with the trend over ~10 years and one piece of evidence): buyer power, supplier power, threat of entry, substitutes, rivalry. Rate overall attractiveness and whether it's improving or deteriorating.
- **Profit pool:** which link in the value chain captures the profit today, and where it is migrating.
- **Chokepoint:** the hardest-to-substitute, slowest-to-expand link — and whether the company owns it.
- **Cycle position** (cyclicals): capex/D&A, utilization direction, inventory quadrant.
- **Policy:** is regulation an exogenous shock or the pricing mechanism itself (utilities, pharma, defense, export-controlled semis)?

---

## 4. Pass C — Competitive position & quality

- **Competitive advantage size:** None / Small / Large, and its 10-year trend (widening / stable / eroding), per Porter: is the advantage from lower cost or higher willingness-to-pay, and what activity system sustains it?
- **Moat type(s)** with quantifiable evidence: intangibles (pricing premium, renewal), switching costs (retention/NRR), network effects (engagement growth, multi-homing), cost advantage (unit cost vs peers), efficient scale.
- **Competitor table:** 3–5 rivals — share, growth, margin, where each wins, direction of threat. Include the non-obvious threat (a hyperscaler building in-house, an open-source substitute, an adjacent giant).
- **Quality scorecard** (from the value-investing frame, 0–3 each, max 12):
  1. Return durability — ROIC (preferred over ROE, which buybacks and leverage inflate) >20% for 3+ years = 3; >15% = 2; 10–15% or volatile = 1; <10% = 0.
  2. Balance-sheet safety — net cash or net debt/EBITDA <1x = 3; <2x = 2; <3.5x = 1; higher = 0 (financials: CET1/RBC instead).
  3. Cash conversion — FCF-after-SBC / core NI >100% = 3; >80% = 2; 50–80% = 1; <50% = 0 (explain capex cycles).
  4. Moat — 2+ strong moats = 3; one clear = 2; weak = 1; none = 0.
  10–12 A · 7–9 B · 4–6 C · 0–3 D. Quality sets the margin of safety, not the rating by itself.
  **Governance cap:** an open governance red flag caps the grade at B. Red flags are a CEO or CFO exit tied to an investigation, a material weakness in internal control, a restatement in the last 3 years, an auditor resignation, or a material undisclosed related-party dealing. Name the flag next to the grade.
- **Fisher spot-checks** (pick the 3–4 that are most diagnostic for this company): durable sales runway; R&D effectiveness relative to size; sales organization strength; margin-improvement plans; long-range vs short-range profit outlook; candor when things go wrong; equity-financing needs that would dilute growth; management integrity.

---

## 5. Pass D — Key Forces

Ask: **over the next 3–5 years, which 1–3 forces will change this company's value the most?** Candidates: technology shift, regulation, competitive entry/exit, pricing power change, capex cycle, management pivot, market misunderstanding of a structural change, hidden-asset monetization.

A Key Force qualifies if it plausibly moves fair value by ≥15–20%. A salient issue that fails the test (a headline lawsuit worth 2% of market cap) goes in the risk table with one line on why it isn't a Key Force — readers will ask. For each, write: force → mechanism → which KPI shows it → value impact (bear vs bull). Give Key-Force-related analysis 2–3× the depth of everything else; if the memo reads like an even-handed checklist, the Key Forces weren't found.

---

## 6. Pass E — Expectations

- **Consensus:** revenue/EPS for the next 2 years, rating distribution, target-price range, forward multiple vs history. Free sources: stockanalysis.com (forecast page), Yahoo Finance (analysis tab), MarketBeat, the company's IR consensus page if it publishes one; record the source and date, and mark summarized figures ⚠. Basis: if the company publishes no non-GAAP EPS, consensus is GAAP; otherwise check last quarter's "actual" on the consensus page against the company's GAAP and adjusted EPS to see which one the Street tracks. Restate consensus EPS and company guidance to **our core basis** before comparing (catalog §11): strip one-off gains they include (a refund inside FY guidance), deduct recurring costs they exclude. Show both: "FY27 consensus $1.95 adjusted → $1.80 core".
- **Market-implied:** reverse DCF (sector-valuation skill).
- **Variant view:** "Consensus believes ___. We believe ___ because ___. The gap closes via ___ by ___ (catalyst + date)." If our view equals consensus, say so — the rating then rests on valuation alone, and conviction should be lower.

---

## 7. Pass F — Red team (this must be able to change the answer)

Run these after the valuation draft, then revise if they land. Revise the **KPI values** in the scenario DCFs first; a scenario weight moves only under the valuation-core §7 rule (a cyclical base rate or a dated event, ≤10 points). The rating then follows from the calculator. Log each change and its cause in the workpapers.

1. **Hidden risks scan** — regulatory, geopolitical, technological, competitive, supply-chain, environmental, governance/behavioral. For each candidate: title (≤10 words); structural vs event-driven; mechanism of impact; why it isn't yet visible in the financials; early indicators; likelihood × impact (L/M/H). Rank the top three under-appreciated risks.
2. **Devil's advocate** — argue **against your own call**: for a Buy, the strongest short thesis; for an Avoid/Sell, the strongest long thesis (what would make today's price cheap). Write it as a skeptical buy-side analyst would: fundamentals first (industry, business, management, financial statements), valuation last. Deliberately seek negative sources (short reports, lawsuits, critical former employees, competitor claims) and keep only arguments supported by facts.
3. **Six-lens check** — one line each: Quality compounder (stronger in 20 years? ROIC trend) · Imaginative growth (how big if everything works?) · Fundamental long/short (what is the market missing?) · Deep value (what would a private buyer pay?) · Catalyst (what event re-prices it, when?) · Macro (does liquidity/rates help or hurt?). Long / Pass / Short for each. Note in the memo only the lens(es) that disagree with the call.
4. **Pre-mortem** — "It's two years later and this lost 40%. The most likely reasons were…" List three; each should map to a kill condition or a risk-table row.
5. **Thesis check** — reread the draft as a senior reviewer: which arguments are strongest, which are logically flawed (circular, survivorship, extrapolation, base-rate neglect), what is missing?
6. **Bias self-check** — confirmation (did I seek disconfirming evidence?), anchoring (on the current price or a prior target?), narrative fallacy, recency, overconfidence (are my bear-case probabilities honest?), sunk cost (if already owned).

---

## 8. Pass G — Decision rules

- **Rating** — walk the rows in order; the **first** that matches wins. The label depends on whether the user already owns it. `valuation.py scenarios` applies this table from `rating_flags`; use its rating.

  | # | Situation | New idea (no position) | Existing position |
  |---|---|---|---|
  | 1 | Kill condition triggered, thesis broken, accounting score ≥ 7, or quality D | **Avoid** | **Sell** |
  | 2 | Expected IRR ≥ hurdle (15%), price ≤ action price, skew ≥ 2:1, no kill condition near trigger | **Buy** | **Add** |
  | 3 | IRR ≥ hurdle but price > action price, skew < 2:1 or a kill condition near | **Avoid (watchlist, near miss)** — give the action price | **Hold** |
  | 4 | IRR between cost of equity and hurdle | **Avoid (watchlist)** — give the action price | **Hold** |
  | 5 | IRR < cost of equity (price ahead of value) | **Avoid (watchlist)** | **Trim** |

  For a watchlist name, write kill conditions as "if bought at the action price, exit if…". Low conviction + Avoid = watchlist, not a short.
- **Conviction:** start at High and step down one level for each that applies: (a) no variant view, or the reverse-DCF growth within ±1 point of our base case; (b) a Key Force rests on management-only or ⚠ secondary evidence; (c) the base-case value moves >25% across the WACC ±1pt swing or the beta used; (d) an open governance red flag. Floor at Low. Name the steps in the workpapers.
- **Action price in the header** = the lower of (fair value today × (1 − MOS)) and (the max price that still earns the hurdle) — `valuation.py scenarios` prints it. MOS comes from the quality grade, not taste: A 15% · B 25% · C 35%, +10 points for each of cyclical / policy-binary (≥25% of revenue) / levered >3.5x, cap 50% (valuation-core §7).
- **Sizing guidance** (default; the user's own rules override): High conviction & bear-case loss <25% → full position; Medium → half; Low → starter or watchlist. Size for the bear case.
- **Kill conditions** — 2–4, each tied to a thesis pillar, measurable, dated, and leading to exit **regardless of price**. "If NRR < 105% for two consecutive quarters by Q2'27 → exit" passes; "if growth slows" doesn't. Distinct from a price stop.
- **Monitoring** — the 3–5 KPIs from the value-driver tree, each with current value, what the thesis needs, and a red line; plus a dated catalyst calendar and add/trim/exit triggers.
