---
name: earnings-normalization
description: Rebuild a company's true recurring earnings from GAAP filings — Core revenue, Core EPS, Core FCF and owner earnings — by finding, classifying and tax-effecting non-recurring items in the P&L and cash-flow statement, then scoring accounting aggressiveness. Use whenever a company reports only GAAP (e.g. META) and the user wants "real", "normalized", "underlying", "adjusted", "clean" or "core" EPS, when GAAP is distorted by one-time tax charges, legal accruals, impairments, restructuring, investment gains or depreciation-life changes, when auditing a company's own non-GAAP numbers, or for quality-of-earnings / forensic accounting work. Also triggers on 调整后EPS, 核心利润, 经常性利润, 一次性项目, 非经常性损益, 真实盈利, 盈利质量, non-GAAP, QoE. Feeds the investment-memo and sector-valuation skills.
---

# Earnings Normalization — GAAP → Core Earnings

Goal: answer "what does this business earn in a normal year at its current scale?" — the number a long-term owner should capitalize. Many US companies (META is the classic case) publish only GAAP, and GAAP for a single period can be badly distorted: Meta's Q3-2025 GAAP EPS was $1.05 because of a one-time $15.9B non-cash tax charge; excluding it, EPS was $7.25. Valuing the company on $1.05 would be absurd — but so would blindly accepting every "one-time" label management offers.

## Principles (why each matters)

1. **Normalize, don't sanitize.** The target is a sustainable number, not the highest defensible one. If you only ever remove costs, you are building a sell-side "adjusted EPS", not an owner's view.
2. **Burden of proof is on removal.** Keep an item unless the filing supports that it won't recur. Costs that keep coming back under different names are recurring.
3. **Symmetry.** Remove one-off gains (investment marks, asset sales, reserve releases, tax benefits) as readily as one-off losses. Gains are the items management never mentions.
4. **SBC is a real cost.** It is compensation paid in shares, and the dilution is permanent. Never add it back (the only exception is a one-time IPO catch-up).
5. **Investment spending is not non-recurring.** Discretionary losses (an AR/VR segment, moonshots) stay in Core EPS; show "Core EPS ex investment segments" separately as an SOTP input.
6. **Every adjustment carries a source, an event_id and an explicit tax treatment.** If you can't cite the filing note or the CFO's words, it doesn't go in. One economic event appears in the income statement, cash-flow statement, footnotes and release — book it once. No default tax rate: research deductibility item by item.
7. **Start from the right numerator and prove it.** Use the diluted EPS numerator from the EPS note (earnings attributable to common after preferred dividends, NCI, two-class and if-converted effects), and tie it to reported diluted EPS before adjusting anything.
8. **Earnings and cash must reconcile.** Normalize the cash-flow statement too: Core FCF exposes what the accrual numbers hide.

## Workflow

Script and reference paths are relative to this skill's directory.

### Step 1 — Read the filings and build the data sheet
- Fetch and read the 10-K, 10-Qs, earnings releases (8-K EX-99.1) and every 8-K after the period end yourself, following `references/reading-filings.md`: where each document lives, how to get exact statement tables (R pages via `FilingSummary.xml`), precision and cross-footing rules, and the data-sheet checklist (5 fiscal years + 8 quarters + TTM, the EPS-note numerator, every debt line incl. the revolver, off-balance-sheet receivable sales, splits, ETR per period). No script does this — parsed XBRL feeds pick wrong tags often enough to corrupt the bridge.
- Many one-offs (legal accruals, discrete tax items, refunds) are not tagged at all and live only in notes, releases and the call. Get the call transcript via web search; never rely on memory for figures.
- **Release out, 10-Q/10-K not yet filed** (common for 2–6 weeks after quarter end). Build the latest period from the 8-K Ex-99.1:
  - P&L and balance sheet come from the release; the new quarter = release full-year (or YTD) − the prior 10-Q YTD.
  - Cash flow is often missing from releases. If so, estimate quarter CFO = Δ(cash + short-term investments) + capex + dividends + buybacks − net debt raised − other financing (disclosed items only), and SBC / D&A from the prior run-rate. Mark every such number `(E)` and say "pending 10-K" in the memo.
  - Notes (tax, legal, estimate changes) aren't in the release: use management's quantified items from the release and call; list the note checks to redo when the filing lands (Update mode).
  - If the call is the same day and no transcript exists yet, use the release's prepared commentary and say the call wasn't reviewed.
- Restate per-share history across stock splits and label columns by **fiscal** period before comparing with other sources.
- Spikes in the data sheet are your first candidate list (a G&A line that triples, an ETR far from its norm). The tax line is **total** tax: size the discrete item from the tax note and remove only that, not the whole line.

### Step 2 — Sweep for candidates
Read `references/adjustment-catalog.md` §1 (search map) and walk §2–§9: revenue, operating costs, non-operating, tax, share count, investment segments, estimate changes, cash-flow-only items. Start with what management quantified, then hunt for what it didn't (gains, estimate changes, cash-tax timing).

### Step 3 — Classify with the recurrence test
Classes: **R0** one-off (remove) · **R1** lumpy-recurring (replace with 5-yr run-rate) · **R2** recurring (keep) · **R3** cyclical (replace with mid-cycle) · **TAX** discrete tax item · **EST** estimate change (disclose). Use the test in catalog §10: seen in ≥2 of 5 years → R1; caused by the business model → R2; moves with a macro variable → R3.
For every R0/R1/R3 item record the evidence: quarters reviewed (aim for 8+), similar events found, and a one-line assessment. Check the sector overlays in catalog §12 (banks, insurers, REITs, commodity producers, retailers, drug developers) — some "unusual" items are ordinary business there.

### Step 4 — Quantify and tax-effect
For R1/R3 items the tax applies to the net adjustment (charge − run-rate); if the filing gives the tax on the gross charge, enter it as `gross_tax_effect`. For each item set a `tax_basis` — `filing_specific` (the company disclosed the tax effect), `jurisdiction_specific` (researched rate for where it's deductible), `normalized_estimate` (analyst estimate — say so), `not_deductible` or `no_tax_effect` (zero tax) — and give `tax_rate` or the explicit `tax_effect`. Government fines and goodwill impairments are usually non-deductible. Discrete tax items are already after-tax (class TAX).

### Step 5 — Core revenue
Core revenue = reported − one-off revenue items. Also report organic, constant-currency growth when M&A or FX matter.

### Step 6 — Core cash flow
Core CFO = CFO ex one-off cash items (settlements paid, cash-tax timing benefits, working-capital anomalies). Then:
- Core FCF = Core CFO − capex − **finance-lease principal** (data-center-heavy companies fund a lot of capex via leases).
- Core FCF after SBC.
- Owner earnings = Core CFO − maintenance capex − lease principal − SBC (maintenance capex ≈ D&A adjusted for life changes, or the Greenwald split in catalog §9). In heavy capex cycles, this gap between total-capex FCF and owner earnings *is* the debate — show both.

### Step 7 — Run the bridge
Write the input JSON (schema in `scripts/core_eps.py` docstring; worked example `examples/core_eps_input.json` — META Q3-25) and run `python3 scripts/core_eps.py input.json --require-evidence`. Run it for TTM and, where useful, FY. [Evidence and TTM input format](references/evidence.md)
- **Errors stop the calculation** (exit code 2, no core number): GAAP numerator / diluted shares not tying to reported diluted EPS within $0.02; missing or duplicate `event_id`; missing source; missing tax basis or rate; non-deductible items carrying tax; R0/R1/R3 without recurrence evidence; SBC removed; a switch between profit and loss without a supported Core denominator (EPS-note basic shares for a loss, or recomputed shares and method). Fix the input; never work around them.
- Link each revenue adjustment to its operating adjustment using the same `event_id`, or document why EBIT, tax and earnings are unaffected in `no_earnings_effect_reason`. Set `has_nci` from the filing. For a company with non-controlling interests, allocate every applicable item using its after-tax `nci_fraction` (zero for a parent-only event). The bridge retains consolidated EBIT and tax and allocates the numerator to common shareholders.
- **Warnings** go into the memo as a sentence each (estimated discrete tax items included): implied tax rates outside 0–60%, fewer than 8 quarters reviewed, "one-offs" with repeated similar events, one-directional adjustments, sector-overlay flags, abnormal core tax rate, low cash conversion.
- For TTM, supply four consecutive quarterly bridges in chronological order. Tie each quarterly GAAP EPS to the filing, then sum the four unrounded Core EPS results. Record total Core earnings to common and valuation shares separately.

### Step 8 — Forensic pass
Read `references/forensic-checklist.md`; score accounting aggressiveness 1–10 with the 2–3 facts that drove it.

### Step 9 — Earning power
- **Core EPS TTM** (fact-based) and **Core EPS FY+1** (built from guidance/consensus — first check the consensus basis. For a GAAP-only reporter, data providers' "adjusted/normalized" EPS has undisclosed exclusions: compare the provider's GAAP and adjusted fields; if they match, consensus is GAAP; if not, mark the basis ⚠ and compare to your core number only directionally).
- **Incremental margin** = Δcore EBIT / Δcore revenue over 4–8 quarters: a better guide to steady-state margins than the current margin for scaling businesses.
- Optional **steady-state EPS** (what earnings would be with growth spend cut to maintenance) — label it a scenario, never a fact.

## Output (feeds memo §4 — keep it to this)

1. Bridge table from `core_eps.py` (GAAP → Core NI → Core EPS, each line with class and source).
2. GAAP vs Core metrics table (revenue, op margin, ETR, EPS) + Core FCF after SBC per share.
3. Three to five bullets: biggest adjustment and why; what was **not** adjusted and why (SBC, investment segment, legal run-rate); estimate-change uplift; accounting score x/10; cash conversion.
4. Confidence: High / Medium / Low, plus any figure marked ⚠ verify.

Mark derived numbers `(E)` and inferences `(I)`. If a figure can't be confirmed in a primary source, say so instead of guessing.

## Common mistakes
- Treating management's adjusted EPS as the answer instead of an input.
- Removing restructuring every year ("recurring non-recurring").
- Ignoring gains in other income because they raise GAAP EPS.
- Forgetting the tax effect, or tax-effecting non-deductible fines.
- Using total-capex FCF in a capex boom without separating maintenance from growth (and vice versa: calling all capex "growth").
- Comparing Core EPS to a GAAP-basis consensus and calling it a beat.
