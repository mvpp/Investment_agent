---
name: sector-valuation
description: Value a stock with a model matched to its industry and business model instead of generic P/E or P/S — SaaS (CAC, LTV, NRR, payback), ad platforms (users × ARPU, capex/D&A wave, SOTP), marketplaces (GMV × take rate), semis (mid-cycle), oil & gas (proved reserves, PV-10, NAV, breakevens), mining (AISC, NAV), banks (P/TBV vs ROTCE), insurers, REITs (NAV, AFFO), utilities (rate base), pharma/biotech (rNPV, patent cliffs), retail/restaurants (unit economics), industrials, telecom, holdcos. Estimates undisclosed KPIs by triangulating filings, peers and benchmarks, then runs DCF, reverse DCF, SOTP, scenarios, IRR and action price with a bundled calculator. Use whenever the user asks for a valuation, fair value, target price, intrinsic value, DCF, reverse DCF, SOTP, "what is it worth", "is it cheap", "what does the price imply", or "which valuation method fits this company". Also 估值, 目标价, 内在价值, 合理价值, 反向DCF, 分部估值, 估值模型, 单位经济模型. Works with earnings-normalization (core earnings input) and investment-memo.
---

# Sector Valuation — value the business the way its cash is actually made

Generic multiples treat a SaaS company, an oil producer and a bank as interchangeable streams of "earnings". They aren't. A SaaS company's value lives in customer lifetime economics; an E&P's in finite reserves at a price deck; a bank's in sustainable ROTCE against cost of equity. This skill picks the model whose inputs are the real drivers, estimates those drivers when the company doesn't disclose them, and produces a target price you can defend line by line.

## Workflow

Script and reference paths are relative to this skill's directory.

### Step 1 — Classify the business model
Identify the business model of each material segment (a company can need two playbooks → SOTP). Then read **only** the matching playbook:

| Business model | Read |
|---|---|
| Software/SaaS, consumer subscription, ad platforms, marketplaces/e-commerce, semis, hardware, AI infrastructure | `references/sectors/tech.md` |
| Banks, insurers, asset managers, brokers, payments, stablecoins/crypto | `references/sectors/financials.md` |
| E&P, midstream, refiners, majors, oilfield services, mining, chemicals | `references/sectors/energy-materials.md` |
| Pharma, biotech, medtech, tools, managed care, providers | `references/sectors/healthcare.md` |
| Retail, restaurants, staples, autos/EVs, industrials, aerospace & defense, airlines, space/early-stage | `references/sectors/consumer-industrial.md` |
| REITs, utilities, telecom/cable, towers, conglomerates/holdcos | `references/sectors/real-assets-telecom.md` |

Always read `references/valuation-core.md` (method selection, discount rate, DCF discipline, justified multiples, reverse DCF, SOTP, scenarios/target/action price, EV bridge).

### Step 2 — Build the value-driver tree
Value ← FCF ← (volume × price − unit cost) − reinvestment, translated into this business's terms (e.g. SaaS: customers × ARPA × GM × lifetime − CAC; E&P: reserves × (price − LOE − F&D)). Pick the **3–5 KPIs that move value most** — these become the scenario levers and the monitoring dashboard. If the investment memo already named Key Forces, the KPIs should be how those forces show up in numbers.

### Step 3 — Get the KPIs (disclosed → derived → benchmarked)
For each KPI: use disclosure if it exists; otherwise derive from filings or triangulate with peers, surveys and alternative data per `references/estimating-undisclosed-kpis.md`. Report a range with a confidence grade (A/B/C) and label `(E)`. Benchmarks are sanity bounds — they reject impossible estimates; they don't replace company evidence.

### Step 4 — Base year = core numbers, pro-forma balance sheet
Start from **core** revenue/EBIT/EPS/FCF from the earnings-normalization skill, never a GAAP period distorted by one-offs. If that hasn't been done, do at least a quick pass for discrete tax items, legal accruals, impairments and investment gains first. For the EV bridge and share count, use post-period figures: 8-Ks after the quarter end (new debt, equity issuance, mandatory converts, splits) — valuation-core §8.

### Step 5 — Run the primary method with the calculator
`scripts/valuation.py` does the arithmetic so numbers tie. Each subcommand takes a JSON file (templates in `examples/`):

| Command | Use for |
|---|---|
| `python3 scripts/valuation.py dcf in.json` | FCFF DCF with growth/margin fade; reinvestment by **capex/D&A vintages** (`capex_pct` + `ebitda_margin` + `asset_life` — use this for capex booms: it produces the depreciation wave; `examples/dcf_capex.json`), sales-to-capital (scalar or path), or a reinvestment-rate path; value-consistent terminal value; 5×5 WACC × terminal-g **and** WACC × terminal-margin sensitivity grids (`margin_step`, default 2pts; `"margin_grid": false` to skip); `excess_customer_advances` for advance-funded businesses; warnings |
| `... reverse in.json` | Market-implied revenue CAGR (`"solve": "growth"`; use capex or sales-to-capital mode so growth isn't free) or terminal margin (`"solve": "margin"`; shifts your margin path, keeping its shape) |
| `... sotp in.json` | Segment value × multiple or explicit/option value, holdco discount, per-share bridge |
| `... rnpv in.json` | Drug pipeline rNPV with phase PoS defaults, launch ramp, LOE erosion, dilution |
| `... ltv in.json` | SaaS/subscription LTV, LTV/CAC, payback, implied NRR |
| `... scenarios in.json` | Per-scenario `value_today` (DCF) rolled to the horizon at cost of equity → target, expected IRR vs 15% hurdle, skew on today's values, and the header action price |

For NAV-style models (E&P, mining, REITs), compute component values (PV-10 adjusted to your deck, risked inventory, cap-rate NAV) and sum them with `sotp`.

### Step 6 — Cross-check (all three)
1. **Reverse DCF** — what growth/margin the price implies vs your base case and consensus. This gap is the variant view in numbers.
2. **Multiples** — implied multiple at your fair value vs peers and the company's own 5-yr range; every multiple justified by growth/ROIC/risk (valuation-core §4).
3. **Structural check** — implied market share or penetration at the terminal year; SOTP if segments differ; replacement/private-market value for asset-heavy names.
If methods disagree by >25%, explain which input drives the gap rather than averaging it away.

### Step 7 — Scenarios, target, action price
Bear/base/bull built by changing the Step 2 KPIs (not ±X% on price), with evidence-based probabilities. Run `scenarios` (give each scenario its DCF `value_today` and the `cost_of_equity`) for target price (default 3-yr horizon), expected IRR (long hurdle ≥15%), skew (prefer ≥2:1), and the action price = lower of fair value × (1 − MOS; 15–20% wide moat, 25–30% narrow, 35–50% cyclical/binary) and the max price that earns the hurdle.

## Output (feeds memo §2 and §5 — keep it to this)

1. One line: method + why it fits this business model.
2. KPI table: KPI | value/range | disclosed or (E) | confidence | source.
3. Core assumptions table (growth path, margin path, reinvestment, WACC, terminal g/RONIC).
4. Valuation result + 5×5 sensitivity (from the calculator).
5. Reverse DCF sentence: "At $P the market implies X% CAGR; our base case is Y%."
6. Scenario table with probabilities → target price, expected IRR, action price.
7. Football-field line: method → value range.

## Guardrails
- No naked multiples: state which earnings, which period, and the justification.
- Count SBC once (expense it, or dilute the share count — not neither).
- Terminal growth ≤ risk-free and long-run nominal GDP; reinvestment consistent with growth (g / RONIC).
- Cyclicals: mid-cycle earnings × mid-cycle multiple. Never peak × peak.
- If the conclusion flips within ±1% WACC or ±1 turn of multiple, call it low-conviction.
- Look up current prices, rates and filings; training-data figures are stale.
