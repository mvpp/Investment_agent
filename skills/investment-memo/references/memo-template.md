# Memo Template (≤5 pages; target 4)

Budget: ~2,200 English words or ~4,000 Chinese characters **including tables**. Word budgets per section are ceilings, not targets; for Chinese, multiply them by ~1.8 to get characters. Headings may be translated (the checker accepts English or Chinese); keep the section order.

Notation: `(E)` estimate · `(I)` inference · `⚠ verify` unconfirmed · citations `[10-Q Q3'26, Note 12]`.

---

```markdown
# $TICKER — <thesis in ≤15 words: the variant view, not a description>

As of YYYY-MM-DD · Price $X · Mkt cap $XB · EV $XB · **Rating: BUY / AVOID (watchlist) / AVOID — or for holders ADD / HOLD / TRIM / SELL** · Conviction: High/Med/Low
**Target (prob-weighted, <horizon, default 3 yr>): $X (+Y%)** · Fair value today $X · Action price ≤ $X · Expected IRR X% vs hurdle 15% · Skew X:1 (or "n/a — price above bull case") · Position: full / half / starter / none

<If the rating looks at odds with the target's % upside — e.g. AVOID with a +30% 3-yr target — add one line under the header: "3-yr target includes the required return; expected IRR X% < hurdle 15%.">

## 1. Thesis & Variant View  (≤220 words + 1 table)

<2–4 sentences: what we own, why it's mispriced, what closes the gap and when.>

| Disputed variable | Consensus / market-implied | Our view | Evidence | When we'll know |
|---|---|---|---|---|
| <e.g. FY28 revenue CAGR> | <reverse DCF: 6.5%> | <12%> | <1-line evidence + cite> | <Q2'27 print> |
| … (2–3 rows max) | | | | |

**Key Forces**
1. <Force> → <mechanism> → <KPI that shows it> → value impact <bear $X / bull $Y>.
2. …
3. … (max 3)

## 2. Valuation Snapshot  (table only)

| Scenario | Prob | Key assumptions (KPI levels) | Value/share | vs price |
|---|---|---|---|---|
| Bear | | | | |
| Base | | | | |
| Bull | | | | |
| **Prob-weighted** | | horizon <n> yr | **$X** | **+Y%** |

Method: <primary + why it fits this business model>. Reverse DCF: price implies <X>; our base case <Y>. Margin of safety <Z%> (quality <grade>) → action price $X.

## 3. Business & Competitive Position  (≤380 words + 2 tables)

<1 paragraph: what it sells, to whom, how it gets paid; the 1–2 historical inflections that explain today's position.>

| Segment | Revenue (TTM) | Growth | Op margin | % of value |
|---|---|---|---|---|

(Single-segment company: use end markets or product lines instead — revenue, growth, % of backlog/orders — and drop "% of value".)

**Industry:** stage <…>; profit pool sits in <…>, migrating to <…>; chokepoint <…>; five forces <one-line scorecard, e.g. Buyers M↑ · Suppliers L · Entry L · Substitutes M↑ · Rivalry M>.

| Competitor | Share / scale | Where they win | Threat direction |
|---|---|---|---|

**Moat:** <type(s)>, advantage size <None/Small/Large>, trend <↑/→/↓>, evidence <1 line>. **Quality score** <x/12> (returns <x> · balance sheet <x> · cash conversion <x> · moat <x>). **Management:** <tenure, incentives, credibility (plan vs delivery), insider activity — 1–2 lines>.

## 4. Earnings Quality: GAAP → Core  (≤250 words + 1 table)

| (TTM, $M) | GAAP | Adjustments (class · source) | Core |
|---|---|---|---|
| Revenue | | | |
| Operating income | | | |
| Net income | | | |
| Diluted EPS | | | **$X** |
| FCF after SBC / share | | | |

- Largest adjustments and why (≤3 bullets).
- Not adjusted, deliberately: <SBC; investment segment loss $X (SOTP); legal run-rate>.
- Estimate changes: <e.g. useful-life extension adds ~$X to EPS>.
- Accounting score <x/10>: <the 1–2 facts behind it>. Cash conversion <x%>.

## 5. Valuation  (≤300 words + 2 tables)

<Method rationale in 1–2 sentences, tied to the business model.>

| Driver / KPI | Value | Disclosed or (E) · confidence | Source |
|---|---|---|---|

<Sensitivity: 5×5 grid (WACC × g, or the two KPIs that matter most).>

Cross-checks: implied <multiple> vs peers <x> and 5-yr range <x–y>; SOTP $X; <structural check>. Methods agree within <x%> / differ because <…>.

## 6. Risks & Kill Conditions  (≤330 words + 1 table)

| Risk | Type | Mechanism → early indicator | L × I | Mitigant / our answer |
|---|---|---|---|---|
| (4–6 rows, ranked) | structural / event | | | |

**Devil's advocate (≤80 words):** <strongest case AGAINST our call — the bear case for a Buy, the bull case for an Avoid/Sell; fundamentals first> — **Our answer:** <rebuttal, or what we concede and how it's priced>.

**Kill conditions** (exit regardless of price; for a watchlist name: "if bought at the action price, exit if…"):
1. <Metric> <threshold> by <date> → <pillar it breaks>.
2. …
3. … (2–4)

## 7. Monitoring & Catalysts  (≤150 words + 1 table)

| KPI | Current | Thesis needs | Red line | Source / frequency |
|---|---|---|---|---|

Catalysts: <date — event — what we're looking for> (3–5 items).
Action triggers: Add if <…> · Trim if <…> · Exit if <kill condition>.

## Sources
Tier 1–2: <filings, transcripts with dates> · Tier 3: <industry/sell-side>. ⚠ items: <list or "none">.
*Research only; not investment advice.*
```

---

## Compression rules (apply while writing, then again with the checker)

1. **Every sentence must change a number, the rating, or a kill condition.** If deleting it changes nothing, delete it.
2. **Say each thing once.** The header and §1 summarize; later sections hold evidence, not repetition.
3. **Tables for numbers, prose for causality.** A paragraph that lists numbers should be a table row.
4. **Three things that matter beat fifteen that are true.** Background the reader can look up (founding date, HQ, full product list) stays out unless it explains the thesis.
5. **Quantify claims.** "Margins will expand" → "core op margin +300bp to 41% by FY28 from mix shift to X (E)".
6. **Uncertainty is information** — mark `(E)`/`(I)`/`⚠ verify` instead of hedging every sentence with "may" and "could".
7. **No throat-clearing.** Lead with the conclusion; no "This memo aims to…", no closing summary that repeats §1.
8. If over budget, cut in this order: §3 history → competitor rows → risk rows below the top four → cross-check prose → §7 catalysts beyond the next 12 months.
