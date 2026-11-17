# Investment Memo Skills Bundle

Four Claude skills that turn a ticker (or an industry) into a short, decision-ready investment memo:

| Skill | What it does | Key assets |
|---|---|---|
| `earnings-normalization` | Rebuilds **Core revenue / Core EPS / Core FCF** from GAAP filings: finds non-recurring items in the P&L and cash-flow statement, classifies them (one-off, lumpy-recurring, cyclical, discrete tax, estimate change), tax-effects them, and scores accounting aggressiveness. Built for GAAP-only reporters like META. | filing-reading guide (where each number lives, R pages, cross-footing, data-sheet checklist), `scripts/core_eps.py` (bridge calculator), adjustment catalog, forensic checklist |
| `sector-valuation` | Values the business by **how its cash is actually made**: SaaS unit economics (CAC/LTV/NRR), ad-platform SOTP, E&P NAV on proved reserves, bank P/TBV vs ROTCE, pharma rNPV, restaurant unit economics, and more. Estimates undisclosed KPIs by triangulating filings, peers and benchmarks, with confidence grades. | `scripts/valuation.py` (DCF incl. capex/D&A-vintage mode, reverse DCF, SOTP, rNPV, LTV, scenarios/IRR/action price), 6 sector playbooks, KPI-estimation guide |
| `us-industry-deepdive` | Top-down industry study: life-cycle stage by penetration, profit-pool migration, chokepoints, capacity-cycle second derivative, expectation gap, tracking dashboard. Feeds the memo's industry pass. | `SKILL.md` |
| `investment-memo` | Orchestrates research → core earnings → valuation → red team → decision, and writes a **≤5-page memo**: thesis & variant view, key forces, competitive position, GAAP→core bridge, valuation, risks, kill conditions, monitoring. | memo template with word budgets, research playbook, `scripts/memo_check.py` (length/structure linter) |

## Install

Claude Code (any project), via this repo as a plugin marketplace:
```
/plugin marketplace add /path/to/Investment_agent
/plugin install investment-memo-bundle@investment-agent
```
Or for a single session: `claude --plugin-dir /path/to/Investment_agent`.
Or copy/symlink the four folders in `skills/` into `~/.claude/skills/`. Keep them together — the memo skill calls its siblings by relative path.

The agent reads filings itself from SEC EDGAR with web fetch (no API key needed). Scripts only calculate: they never fetch data, so every input number traces to a filing the agent read.

## Use

- "Write an investment memo on META" / "帮我写一份 META 的投资备忘录"
- "Is the semicap sector investable right now?" → us-industry-deepdive
- "What is META's real EPS ex one-offs this quarter?" → earnings-normalization
- "Value XOM on its reserves" / "What growth does SNOW's price imply?" → sector-valuation
- "META just reported — is my thesis intact?" → memo update mode (reads the prior memo in `memos/`)

Calculators run standalone too:
```
python3 skills/earnings-normalization/scripts/core_eps.py skills/earnings-normalization/examples/core_eps_input.json
python3 skills/sector-valuation/scripts/valuation.py dcf skills/sector-valuation/examples/dcf.json
python3 skills/investment-memo/scripts/memo_check.py memos/META_2026-11-17.md
```

## Where the ideas come from

- **tech-earnings-deepdive** (Day1Global): Key Forces first, evidence tiers, variant view, six investment-philosophy lenses, IRR hurdle (≥15%), action price, quantified action triggers.
- **us-value-investing** (Day1Global): the four-dimension quality score (returns, balance sheet, cash conversion, moat) → memo quality score, which sets the margin of safety.
- **AI Equity Analyst prompts** (Gary Mishuris): source hierarchy and citation discipline, Porter five forces with 10-year trend, competitive-advantage size, Fisher points, management plan-vs-delivery, hidden risks, Schilit forensic score, devil's advocate, thesis checker.
- **Anthropic financial-services skills** (ic-memo, thesis-tracker, dcf-model): balanced memo structure, ranked risks with mitigants, falsifiable thesis with update log, DCF/sensitivity discipline, valuation reconciliation.
- **This repo's notes** (`investment_skills.md`, `valuation_skill.md`) and the original industry deep-dive (now `skills/us-industry-deepdive`): industry KPI cheat sheet and model-by-industry map (expanded into the sector playbooks), forward-FCF/incremental-margin principle, expectation-gap / profit-pool / chokepoint analysis.

*Research tooling only; not investment advice.*
