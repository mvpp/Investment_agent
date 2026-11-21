---
name: investment-memo
description: Write a convergent, decision-ready investment memo (≤5 pages) on a public company — business overview, key forces, industry structure and competitive landscape, GAAP→core earnings, industry-specific valuation, variant view vs consensus, target price and action price, risks, devil's advocate, kill conditions and a monitoring dashboard. Orchestrates the earnings-normalization and sector-valuation skills. Use whenever the user asks to analyze/research/cover a stock, write an investment memo or thesis, decide whether to buy/sell/hold, do a deep dive, initiate coverage, update a thesis after earnings, or asks things like "should I buy NVDA", "write up META", "is my thesis on X still intact". Also 投资备忘录, 投资memo, 个股研究, 深度研究, 投资逻辑, 买入/卖出/持有, 目标价, 止损条件, 关注点, 风险提示. Prefer this over the more generic tech-earnings-deepdive or us-value-investing skills when the user wants a single concise memo with a decision.
---

# Investment Memo

Produce the memo a disciplined long-term investor would want before committing capital: one that converges on a decision, with a defensible target price and explicit conditions under which the thesis is wrong. Research broadly, write narrowly. The memo is at most 5 pages; the research behind it can be much larger and stays in workpapers.

This skill combines: Key-Forces focus, multi-lens challenge and actionable triggers (tech-earnings-deepdive); the quality scorecard (us-value-investing); primary-source discipline, industry/competitive-advantage analysis, hidden-risk, forensic and devil's-advocate passes (Mishuris, *AI Equity Analyst*); and the balanced IC-memo structure and falsifiable thesis tracking (Anthropic financial-services ic-memo / thesis-tracker). It calls sibling skills in this bundle:
- `earnings-normalization` — GAAP → Core revenue/EPS/FCF (`../earnings-normalization/`)
- `sector-valuation` — industry-specific valuation, undisclosed-KPI estimation, calculator (`../sector-valuation/`)
- `us-industry-deepdive` — full industry study when the industry pass needs more depth (`../us-industry-deepdive/`)

Paths to scripts and references below are relative to this skill's directory (sibling skills live one level up), not to the user's working directory.

## Before starting

Confirm (ask only what you can't infer): ticker; purpose — **new idea**, **existing position review**, or **post-earnings update** (→ Update mode below); horizon (default 3 years for both the target price and the IRR — one horizon keeps the numbers consistent); any portfolio rules (position sizing, hurdle rate). Match the user's language for the memo (Chinese request → Chinese memo; keep tickers, metrics and accounting terms in English where natural), unless the user or system prompt specifies an output language.

**Unattended runs.** When the request says no one can answer questions (a scheduled job, a hosted agent, a batch), don't ask: take the ticker and any stated purpose from the request, use the defaults for everything else (new idea, 3-year horizon, 15% hurdle, the request's language), and say in one line under the memo header which defaults were assumed. If something essential can't be established (the ticker doesn't exist, no filings are reachable), stop and say why instead of writing a memo on guesses.

**Supplied data pack.** If the request points to a local folder of data (prices, statement history, consensus, peers, holders, a transcript, an earnings release), read its README first. Use the pack for orientation, screening, the competitor table, consensus and cross-checks — it saves searches. Calculator inputs still come from filings you read yourself (`../earnings-normalization/references/reading-filings.md`); where the pack and a filing disagree, the filing wins and the gap is worth one line in the workpapers. Cite pack data with the label its README gives.

Get fresh data first: latest price, market cap, the most recent 10-K/10-Q, last call transcript, consensus estimates. Training-data knowledge is a starting hypothesis, never a source — later filings exist.
- Read the filings yourself and build the data sheet per `../earnings-normalization/references/reading-filings.md` (5 years / 8 quarters / TTM, every number verbatim with its URL). Archive the evidence manifest and local filing extracts with the workpapers. Run the earnings and valuation calculators with `--require-evidence --json` and retain their output. [Evidence format](../earnings-normalization/references/evidence.md)
- **Every 8-K filed after the latest quarter end.** Financings, share issuance (forward sales, mandatory converts, ATMs), splits/stock dividends, settlements and M&A after the period change the share count, net debt and thesis; they never show up in the quarter's statements.
- If the latest results exist only as an 8-K release (10-Q/10-K pending), use the release as the latest period and follow the earnings-normalization "release out, filing pending" steps. If the price you have predates the release (e.g. after-hours print), say so in the header and, if you can get it, show both pre- and post-release prices.

## Workflow

Read `references/research-playbook.md` for the detail behind each pass (evidence standards, scorecards, red-team prompts, decision rules).

1. **Fact base** (playbook §2) — how the company makes money, segment economics, inflection points, management credibility (what they promised vs delivered), incentives, capital allocation.
2. **Industry & competition** (§3–§4) — stage, five-forces scorecard with trend, profit pool & chokepoint, competitor table, moat type/size/trend, quality score /12. For a full sector study run the sibling `us-industry-deepdive` skill (`../us-industry-deepdive/SKILL.md`).
3. **Key Forces** (§5) — the 1–3 forces that move fair value ≥15–20% over 3–5 years. From here on, spend 2–3× the depth on anything tied to them.
4. **Core earnings** — run the `earnings-normalization` workflow: bridge table, core EPS/FCF, accounting score.
5. **Valuation** — run the `sector-valuation` workflow on core numbers: business-model method, KPI estimates with confidence, DCF/SOTP/rNPV/NAV via the calculator, reverse DCF, scenarios → target, IRR, action price.
6. **Expectations** (§6) — consensus vs market-implied vs ours → the variant view sentence. No variant view → lower conviction; say so.
7. **Red team** (§7) — hidden risks, devil's advocate, six-lens check, pre-mortem, thesis check, bias check. Then **revise** KPI values or scenario weights if any of it lands, log the change, and rerun the calculator. A red team that never changes anything is theater.
8. **Decide** (§8) — rating, conviction, sizing guidance, 2–4 kill conditions (for an Avoid on a new idea: entry conditions + the kill conditions that would apply once bought), monitoring KPIs, catalysts, add/trim/exit triggers.
9. **Write and compress** — fill `references/memo-template.md`, apply its compression rules, then run `python3 scripts/memo_check.py memo.md --calc scenarios_out.json` (the `valuation.py scenarios ... --json` output) and fix until it passes (≤5 pages, required sections present, numeric kill conditions, no filler, header target / fair value / action price / rating equal to the calculator's).

Steps 4 and 5 are where the value is. Don't let the qualitative passes crowd them out.

## Writing the memo — why it must be short

The reader is going to make a decision and then track it. Every extra paragraph dilutes the three things that matter and makes it harder to see when the thesis breaks. So:
- Lead with the decision and the variant view; the header line alone should tell a reader what to do and at what price.
- Numbers in tables, causality in prose. Each claim quantified and sourced.
- State what you did **not** adjust or include and why — that's where readers find hidden assumptions.
- Balanced: present the bear case at full strength. Don't minimize risks; a reader will find them anyway, and credibility is the asset.
- Tables must tie: §4 core figures are the base year for §5; scenario values in §2 = calculator output; kill conditions in §6 = red lines in §7. State the four quarterly EPS denominators, today's pro-forma valuation shares, and the expected horizon share count used for a fundamentals-based target.

## Output

- Default: the memo as Markdown, saved to `memos/<TICKER>_<YYYY-MM-DD>.md` in the working directory, and shown in the conversation.
- Optional (if asked): `.docx`/`.pdf` via the docx/pdf skills; a workpapers file with the full research; a thesis card (below).
- If the request names output paths, write there instead: the memo, and next to it the scenarios JSON the memo's header was checked against (`valuation.py scenarios <input> --json`, saved unedited) so a host can collect both. Finish only after `memo_check.py <memo> --calc <that JSON>` passes on the saved files.
- End the reply with 2–3 lines: rating/target/action price, the single most important thing to watch, and any ⚠ items needing the user's verification.

## Update mode (after earnings or news)

When a prior memo exists (look in `memos/`): don't rewrite it. Produce a ≤1-page update:
1. Thesis scorecard — each pillar / Key Force: original expectation → latest datapoint → status (on track / behind / broken) and trend.
2. Kill conditions — each one's current value vs threshold.
3. Core EPS bridge for the new quarter (earnings-normalization) and what changed in the valuation.
4. Update log line: date · datapoint · pillar affected · action (no change / add / trim / exit) · new conviction.
5. Revised target/action price only if inputs changed; say which.
Track disconfirming evidence as rigorously as confirming evidence.

## Thesis card (optional, for tracking)

A short block the user can keep with the position: thesis (1–2 sentences) · pillars (3–5) · kill conditions · target & action price · catalysts with dates · KPI red lines. Save it as `memos/<TICKER>_thesis.md` if the user wants persistent tracking.

## Disclaimer
End every memo with one line: research only, not investment advice.
