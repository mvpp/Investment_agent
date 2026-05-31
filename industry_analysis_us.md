---
name: us-industry-deepdive
description: Top-down, investment-oriented industry deep-dive for US equities, built around the life cycle and forcing an Expectation-Gap and Profit-Pool field after every dimension. Use whenever the user says things like "analyze this industry/sector", "do an industry deep dive", "is this sector worth investing in", "who makes the money in this value chain", "where is the profit pool", "where's the chokepoint", "has the supply cycle turned", "is the expectation already priced in", "consensus vs variant view", "moat", or "smile curve" — including loose asks like "how's the semis sector" or "is biotech investable". Covers stage diagnosis (penetration-based), profit-pool migration, chokepoint analysis, the capacity-cycle second derivative, stage-mapped valuation, US policy and investability filters, and a tracking dashboard. Forms an "industry → single name" funnel with us-value-investing and tech-earnings-deepdive; pair with macro-liquidity and us-market-sentiment when macro/policy is a Key Force.
---

# US Equity Industry Deep-Dive — Investment-Oriented Framework

## Purpose and Design Philosophy

This serves a self-funded investor in US equities who plays for expectation gaps and second-order transmission rather than consensus narratives. The goal is not an "industry health checkup" — it is to answer four questions that convert directly into a bet:

1. **Is the industry's strength or weakness already in the price?** Where the industry objectively sits in its life cycle produces no alpha; the **gap** between your judgment and what the market has already priced in does.
2. **The industry is growing — but whose pocket does the money end up in?** Who captures the profit and how that is migrating (polysilicon → inverters → nobody profitable; Intel + Microsoft taking the whole pie while OEMs get scraps) usually decides which link to buy more than the industry growth rate does.
3. **Which link in the value chain is the binding constraint?** Pricing power and excess returns tend to lock onto the chokepoint that is hardest to substitute, slowest to add capacity, and most concentrated.
4. **Where am I in the cycle?** The tradeable signal lives in the second derivative (capex/D&A, capacity under construction vs in service, the utilization inflection) — not in the directional "tight supply → shakeout" story.

**Core principles:**
- **Price the expectation, not the present.** Every dimension answers: what is consensus, where do I differ, and is that difference already priced?
- **Trace where the surplus lands.** Every dimension answers: which link captures the profit/surplus, and how is that migrating?
- **Roughly right beats precisely wrong.** Give ranges and explicit definitions for market size and penetration; don't fake precision.
- **Make conclusions falsifiable.** Attach "if X happens, the conclusion must be revised" to every judgment.
- **Hold the granularity fixed.** Lock the industry-boundary definition up front; never silently switch the unit of analysis mid-stream.

---

## End-to-End Flow

```
Step 0: Clarify intent (anchor the purpose: stock-picking / venture / career)
Step 1: Define the industry boundary (horizontal granularity + vertical value chain)
Step 2: Life-cycle diagnosis (penetration — lock the denominator first)
Step 3: Stage-specific core dimensions (3A feasibility / 3B scalability / 3C defensibility / 3D profitability)
        ★ Force an [Expectation-Gap] and [Profit-Pool] field after EACH dimension
Step 4: Profit-pool migration (surplus capture + smile curve + migration direction)
Step 5: Chokepoint analysis (find the binding constraint)
Step 6: Second derivative of the capacity cycle (cyclical/manufacturing/resource sectors mandatory)
Step 7: Substitution and disruption threat (a live threat at EVERY stage)
Step 8: Valuation logic (stage-mapped methods + reverse DCF to extract the implied expectation)
Step 9: PEST + US policy endogeneity + investability filter
Step 10: Expectation-gap synthesis (consensus vs variant view)
Step 11: Tracking dashboard (high-frequency verification + action triggers)
```

---

## Step 0: Clarify Intent

Before starting, ask exactly one question (skip if already stated):

> "Are you analyzing this industry mainly for: **stock-picking, choosing a venture/startup space, or a career move** — or something else?"

Different purposes shift the output emphasis (see "Output Format"). Stock-picking is the default.

---

## Step 1: Define the Industry Boundary

**Horizontal (granularity):** State which level you're analyzing — sector / industry group / sub-industry.
- Primary reference: **GICS** (S&P/MSCI), 11 sectors → 25 industry groups → 74 industries → 163 sub-industries.
- Cross-check: **NAICS** (US government / Census economic data) and **ICB** where relevant.

**Vertical (value chain):** List the main links — `raw materials → components → finished product → distribution → end user` — and flag the link(s) in focus. **This chain is the base map for Step 4 (profit pool) and Step 5 (chokepoint); draw it cleanly.**

**Output:** One sentence locking it down — "This analysis defines the industry as … (includes which links / excludes which)." This definition does not change for the rest of the report.

---

## Step 2: Life-Cycle Diagnosis (Penetration as the Axis)

Use **penetration**, not elapsed time or the slope of the growth rate, to call the stage.

**⚠️ Denominator discipline (the most error-prone and most load-bearing step — solve it first):** penetration = adopted units / total addressable units, and **the choice of denominator can flip the conclusion.**
- EV penetration on "annual new-vehicle sales" vs "the installed vehicle base" differs by an order of magnitude — "growth stage vs mature stage" reverses outright.
- **Requirement:** Write out explicitly "penetration here = ___ / ___" and justify the denominator. That denominator IS the TAM basis you'll use in Step 8; the two must match.

| Stage | Penetration band (rule of thumb, adjust by industry) | Core traits | What to judge here |
|-------|------|------|------|
| Introduction | < 5% | Business model unproven, few players, losses common | Real demand or pseudo-demand? |
| Growth | 5% – 50% | Accelerating adoption, rapid scaling, active funding | How much room left, can the growth rate hold? |
| Maturity | > 50%, growth into single digits | Structure consolidating, price war or oligopoly | Moat + structure + profit split |
| Decline | Penetration peaked and rolling over | Substituted or shrinking demand | Substitution threat, second-curve potential |

**Non-linearity reminder:** real life cycles aren't a clean S-curve. Three paths — ① death in the introduction stage (pseudo-demand); ② a second growth curve in maturity that re-enters growth; ③ "stable-state cyclicality" in maturity (banks, spirits/staples). State which path applies.

**Expectation-gap anchor:** what stage is the market currently *pricing* this industry as? (Paying growth multiples for a mature industry, or vice versa, is itself the source of the opportunity/risk.)

---

## Step 3: Stage-Specific Core Dimensions

Focus per Step 2. **After EACH dimension, append the two mandatory fields below.**

### ★ The Two Mandatory Fields (apply to every one of 3A–3D)

> **[Expectation-Gap]** (rooted in Rappaport & Mauboussin, *Expectations Investing*)
> 1. On this dimension, what is **the market consensus**? (Reverse it out from sell-side consensus, forward multiples, and the assumptions implied by the leader's stock price.)
> 2. **My judgment** vs consensus — direction (more bullish/bearish) and magnitude of the difference.
> 3. Is that difference **already priced in**? (If priced, being right yields no alpha; only the un-priced gap is the opportunity.)
> 4. **Falsifier:** what data, if it appears, proves *me* wrong rather than the market?

> **[Profit-Pool]** (rooted in Gadiesh & Gilbert, HBR 1998; smile curve, Stan Shih)
> 1. Across the links in this dimension, **who captures the profit/surplus**? (Not who has the biggest revenue — who takes the profit.)
> 2. How is that split **migrating**? (Concentrating up/down-stream or onto a chokepoint, or getting commoditized until no one profits?)
> 3. Where does my link of interest sit on the **smile curve** (the high-margin R&D/brand ends, or the low-margin manufacturing middle)?

---

### 3A: Feasibility (mandatory in the introduction stage)

**Demand side:** Real demand vs pseudo-demand? Will users pay? Price sensitivity?
**Supply side (unit economics):**
1. Can it be sold: CAC, conversion, retention
2. Can it make money: is gross margin positive and expandable; LTV > 3 × CAC?
3. Can it scale-replicate: does the model copy to more users/geographies?

**Verdict:** feasible / conditionally feasible (requires X) / not feasible (why).

> **[Expectation-Gap]:** Is the market treating this as "the next big story" or as pseudo-demand? Has capital already flooded in and maxed out valuations?
> **[Profit-Pool]:** Even if demand holds, which link will the future profit settle in? Where does today's subsidy/burn ultimately flow (users? distribution? upstream)?

---

### 3B: Scalability (mandatory in the growth stage)

**Three market-size lenses:** TAM (theoretical total) ⊃ SAM (currently serviceable) ⊃ SOM (realistically winnable in 3–5 yrs).
- ⚠️ The TAM basis must match the Step 2 penetration denominator. Beware the "TAM mirage" — a claimed trillion-dollar market where SAM is a tenth of that.

**Two sizing methods:**
- Top-down: total market × penetration assumption
- Bottom-up: price × unit count (more credible — prefer it)

**3–5 year forecast:** anchor on the history of an analogous mature market (e.g. benchmark against the equivalent US/European industry) + policy targets + public-company guidance, and give **high/base/low scenarios.**

> **[Expectation-Gap]:** What CAGR does sell-side/market consensus carry? Is my base case above or below it? What growth rate does the leader's stock price imply (cross-check with reverse DCF)?
> **[Profit-Pool]:** The market is growing, but which link's P&L does the incremental revenue land in? When analogous industries scaled historically, did manufacturing deflate while brand captured, or did one component chokepoint take it all?

---

### 3C: Defensibility (mandatory in the maturity stage)

**Two moat sources:** ① resource monopoly (licenses, scarce inputs, data, patents); ② competitive advantage (barriers built through market behavior).

**Four competitive-advantage moats:**

| Type | Mechanism | Quantifiable evidence | Erosion signals |
|------|-----------|----------------------|-----------------|
| Intangibles | Brand / patents / licenses | Premium pricing, renewal rate | Generics, patent cliff, license deregulation |
| Switching costs | High migration cost | Retention, NDR | One-click migration tools, standardization |
| Network effects | Users attract users | One/two-sided active growth | Rise of multi-homing |
| Cost advantage | Scale / process / location | Unit cost vs peers | New tech route bypasses incumbent scale |

**Moat width:** wide (multiple stacked barriers) / narrow (single barrier, catchable in 3–5 yrs) / none (commoditized, price is the only axis).

> **[Expectation-Gap]:** Is the market paying a "perpetual" premium for a moat that's actually eroding (or vice versa)? Is the moat duration implied by the multiple reasonable?
> **[Profit-Pool]:** Is the link the moat sits on actually the fattest-profit link? Or is the barrier in link A while the profit gets taken by link B (the chokepoint)?

---

### 3D: Profitability (mandatory in the maturity stage)

**Horizontal structure (capacity cycle):** ① tight supply → high profit attracts entrants; ② capacity surge → price war; ③ capacity shakeout → weak players exit; ④ structure improves → oligopoly earns excess returns. **A directional call isn't enough — pair it with Step 6 to locate exactly where in the cycle you are.**

**Vertical structure (profit split):** Porter's five forces × bargaining power.
- Bargaining **willingness** (motive: customer relationship, brand position) + bargaining **ability** (means: concentration, scarcity of substitutes).

**Financial verification:** gross margin (pricing power), AR/AP turnover (ability to fund off up/down-stream), ROE / ROIC (capital efficiency).

> **[Expectation-Gap]:** Does the market's read on which part of the cycle we're in match mine? Is it capitalizing peak-cycle earnings as if perpetual?
> **[Profit-Pool]:** Five-forces analysis IS profit-pool attribution — write out explicitly "of every $100 of end value on this chain, R&D / manufacturing / brand / distribution each take how much," and state the trend.

---

## Step 4: Profit-Pool Migration

**Core question:** the industry is growing — who takes the money, and which way is the split migrating?

Aggregate the scattered [Profit-Pool] fields from Step 3 into one **full-chain profit map.**

**4.1 Profit Pool Snapshot**
Walk the value chain from Step 1 and estimate, per link, "share of profit pool vs share of revenue." Links where profit share ≫ revenue share are the value captors.

| Link | Revenue share | Profit-pool share | Avg gross margin | Smile-curve position | Who's here |
|------|--------------|-------------------|------------------|---------------------|------------|
| Raw materials | | | | | |
| Core components | | | | | |
| Manufacturing/assembly | | | | | |
| Brand/integration | | | | | |
| Distribution/services | | | | | |

**4.2 Migration direction (the crux)**
- Which link is profit concentrating into? (3–5 yr gross-margin trend + concentration change)
- What force is driving the migration? (tech shift, standardization, capacity additions, policy, new entrants)
- **Call where the profit pool lands over the next 3 years** — this usually decides which link to buy more than the industry growth rate does.

**4.3 Canonical migration playbooks (for analogy cross-check)**
- Solar: profit first in polysilicon → shifts to inverters/balance-of-system → main chain commoditized until no one is profitable
- PC: Intel + Microsoft (the two ends) take it all, OEMs (the manufacturing middle) get scraps
- Smartphone: Apple (brand + ecosystem) + TSMC (chokepoint manufacturing) capture the vast majority of the pool
- Cloud: hyperscalers + the accelerator chokepoint (Nvidia) capture, while server OEMs run thin

**Conclusion sentence:** answer in one line — "The money in this industry is in ___ today and migrates to ___ in 3 years, because ___."

---

## Step 5: Chokepoint Analysis

**Core question:** which link is the binding constraint? Pricing power and excess returns tend to lock there.

**5.1 Find the chokepoint**
Per link, ask: which is **hardest to substitute, slowest to add capacity, most concentrated**? Typical forms:
- Sole/oligopoly supply (CoWoS advanced packaging, ASML lithography, photoresist, specialty gases like helium/neon)
- Physical/geographic chokepoints (Strait of Hormuz / Panama Canal-type throats)
- Certification/credential barriers (medical-device clearance, automotive-grade qualification, airworthiness)
- Control of data or standards

**5.2 Chokepoint strength**
| Dimension | Question | Strong / Mid / Weak |
|-----------|----------|---------------------|
| Irreplaceability | Any alternative? Switching cost/time? | |
| Capacity elasticity | How fast can it ramp when tight? (longer build = more valuable chokepoint) | |
| Concentration | What's CR3? | |
| Margin capture | Does the chokepoint actually convert the premium into profit (vs ceding it downstream)? | |

**5.3 Chokepoint × profit-pool cross-check**
- Ideal bet: the link that is **chokepoint ∩ profit-pool captor.**
- Watch for mismatch: a chokepoint with no pricing power (squeezed by a large downstream customer), or profit that exists while the chokepoint is being dismantled (new capacity/new tech route incoming).

---

## Step 6: Second Derivative of the Capacity Cycle (mandatory for cyclical / manufacturing / resource sectors)

**Core question:** not "is the cycle good right now" but "where am I in the cycle and when does it turn." The tradeable signal is the second derivative.

**6.1 Supply-side second derivative (most important)**
- **Capex / D&A ratio:** > 1.5 means the whole industry is adding capacity (a supply shock is coming); < 1 means it's contracting (supply shakeout, profit inflection near).
- **Capacity under construction / in service:** sizes the supply increment over the next 1–2 years.
- **Utilization inflection:** the turn from down to up (or vice versa) is an earlier reversal signal than price.
- **Inflection in the industry's capex growth rate** (the second derivative of capex): often leads price by 2–4 quarters.

**6.2 Demand-side verification**
- Inventory cycle: channel days-of-inventory (active restock / passive restock / active destock / passive destock — locate the four-quadrant position).
- Orders: book-to-bill, backlog trend.

**6.3 Cycle-location conclusion**
Write it out: "Supply-side capex/D&A = ___, utilization direction = ___, inventory in the ___ quadrant → currently at the ___ part of the cycle (bottom reversal / mid-upswing / top / downswing)."

> The biggest way to lose money in a cyclical: capitalizing peak earnings × a high P/E at the top of the cycle. This step directly hedges that error.

---

## Step 7: Substitution and Disruption Threat (a live threat at EVERY stage)

Substitution is **not a decline-stage-only** question — disruption most often kills *growth-stage* industries (the thing being adopted is itself leapfrogged).

At every stage, ask:
- Is there a maturing substitute tech/approach that could leapfrog the current industry?
- When does the cost/performance curve of the substitute cross this industry's?
- Is my link a beneficiary or a victim of the disruption?

---

## Step 8: Valuation Logic

**Different stages require different rulers.**

| Stage | Primary method | Don't use | Why |
|-------|----------------|-----------|-----|
| Introduction | Reverse DCF, EV/Sales, option-style scenarios | P/E | No stable earnings |
| Growth | DCF, EV/EBITDA, PEG | Static P/E | Growth is the value driver |
| Maturity | P/E, EV/EBITDA, DCF | — | Earnings stable |
| Cyclical | Normalized earnings × mid-cycle P/E, P/B | Peak earnings × P/E | Avoid the peak-cycle valuation trap |
| Asset-heavy | Replacement cost, NAV | — | Assets are the anchor |

**Reverse DCF (mandatory — to extract the market's expectation):**
- Back out the growth/margin assumptions implied by the current price.
- Hold that implied assumption against each [Expectation-Gap] from Step 3: **is the market-implied growth above or below my base case?** This step directly produces the core of the investment conclusion.

Multiple = f(odds: how good the fundamentals are, probability: confidence the expectation is realized). Give ranges, not fake point estimates. (For sector multiple reference, Damodaran's NYU datasets are a good free anchor.)

---

## Step 9: PEST + US Policy Endogeneity + Investability Filter

**9.1 PEST** (Political / Economic / Social / Technological) — flag specifically which external factors are currently **catalysts** (accelerating) or **suppressors** (impeding).

**9.2 US policy endogeneity**
- In several US sectors, policy is not "one box in PEST" — it is **THE structuring force**: CHIPS Act and BIS export controls for semis; the IRA for clean energy and (via Medicare drug-price negotiation) for biopharma; defense appropriations / NDAA for defense; FDA pathways for pharma/medtech; FTC/DOJ antitrust and M&A-approval risk for big tech; tariffs / Section 301 for China-exposed supply chains; FERC/EPA for utilities and energy.
- Distinguish explicitly: is policy an **exogenous shock** to this industry, or an **endogenous pricing mechanism**? If the latter, break policy out as a standalone Key Force.
- When macro/liquidity is a Key Force, pair with `macro-liquidity` and `us-market-sentiment`.

**9.3 Investability filter**
An attractive industry ≠ an investable one. Run one more filter:
- **Share-class structure:** dual/multi-class super-voting (founder-controlled names) — external shareholders have weak real control; weigh the governance discount.
- **Index inclusion/exclusion flows:** S&P 500 add/drop, Russell reconstitution — passive flows can dominate price action around the event.
- **Liquidity & float:** ADV, bid-ask, short-borrow availability and cost; for your size, how many days to build/exit without material market impact.
- **Domicile/structure for foreign-domiciled names:** ADR vs ordinary; PFIC risk on certain foreign issuers (a US-tax-resident concern) — flag, don't assume.
- **Accounting quality:** restatement history, aggressive revenue recognition, related-party transactions.

---

## Step 10: Expectation-Gap Synthesis (the soul of the report)

If your conclusion is identical to consensus, the analysis added no value. Compress the [Expectation-Gap] fields from Step 3 into one statement:

> **Consensus believes ___. We believe ___. They're wrong / missing something because ___. The gap should close via ___ (catalyst + timing).**

Must answer:
1. What assumption does current pricing imply? (Triangulate: reverse-DCF implied growth + distribution of sell-side ratings + forward multiple.)
2. Why is that assumption wrong/incomplete? What's the evidence chain?
3. Is the gap already converging? How much un-priced room is left?
4. **Falsifier:** what signal would tell you that *you* are the one who's wrong?

---

## Step 11: Tracking Dashboard (high-frequency verification + action triggers)

Analysis is the start; sustained tracking is what validates the call. Design a high-frequency indicator set:

| Type | Indicator | Source | Frequency |
|------|-----------|--------|-----------|
| Volume | Units/shipments/orders/user growth | Trade associations (SEMI, SIA, etc.), Census, card-spend (Earnest/Second Measure), app data (Sensor Tower) | Monthly/HF |
| Price | Factory price/input cost/retail price | Company filings, BLS PPI/CPI, industry price trackers (TrendForce, S&P Global Platts) | Weekly/Monthly |
| Profit | Gross/net margin trend | 10-Q/10-K | Quarterly |
| Inventory | Channel days-of-inventory | Filings, industry data | Monthly/Quarterly |
| Supply | Capex/D&A, utilization (the second-derivative core) | Filings, Fed industrial-capacity data | Quarterly |
| Expectation | ISM PMI, sector sentiment surveys, sell-side revision breadth | ISM, FRED, Visible Alpha | Monthly |

**Action Triggers (turn tracking into action):**

| Signal (must be specific and quantifiable) | Action | Size |
|--------------------------------------------|--------|------|
| If [profit-pool migration confirmed / penetration crosses X%] | Add to that link | X% |
| If [chokepoint is dismantled / second derivative turns to oversupply] | Trim/exit | X% |
| If [the gap gets priced in, margin of safety gone] | Take profit | X% |

"If the sector weakens" doesn't pass; "if industry capex/D&A exceeds 2x for two consecutive quarters and module price breaks below $X/W" does.

---

## Output Format

Adjust emphasis by the Step 0 purpose:
- **Stock-picking** (default): life cycle + profit-pool migration + chokepoint + second derivative + expectation gap + valuation + tracking
- **Venture space**: feasibility + market size + moat-building path + where the profit pool lands
- **Career move**: life cycle + industry outlook + profit pool (which link's companies make the most → which type of employer to target)
- **Full industry report**: cover all dimensions

### Report Template

```
# [Industry]: [one-line investment thesis = your expectation-gap conclusion]

## Executive Summary / TL;DR
- [Conclusion + conviction]: long which link / avoid which link / PASS
- [Life-cycle stage + penetration basis]
- [Profit pool is in ___ today, migrating to ___ in 3 yrs]
- [Core chokepoint = ___]
- [Cycle location = ___] (cyclical sectors)
- [Expectation gap = market thinks ___, we think ___]
- [Valuation: market-implied growth vs my base case]

## 1. Industry definition and boundary (with value-chain map)
## 2. Life-cycle diagnosis (penetration basis + stage + non-linear path)
## 3. [Stage-specific] core dimensions
   each dimension appends: [Expectation-Gap] + [Profit-Pool]
## 4. Profit-pool migration map (full-chain split + direction + conclusion line)
## 5. Chokepoint analysis (strength table + chokepoint × profit-pool cross-check)
## 6. Second derivative of the capacity cycle (cycle-location conclusion)  ← cyclical/manufacturing/resource
## 7. Substitution and disruption threat
## 8. Valuation logic (stage-mapped methods + reverse-DCF implied expectation)
## 9. PEST + US policy endogeneity + investability filter
## 10. Expectation-gap synthesis (consensus vs variant view + falsifier)
## 11. Tracking dashboard + action triggers

## Conclusion and risk flags
- The link most worth betting on (chokepoint ∩ profit-pool ∩ un-priced gap)
- Three failure paths (pre-mortem: if I'm wrong in 2 years, most likely because ___)
- Action price and entry pacing

## Evidence sources (tiered: primary / facts / opinion)
## ⚠️ Disclaimer: based on public information and model inference, for research only, not investment advice.
```

---

## Operating Principles

1. **Price the expectation, not the present.** A correct call with no expectation gap produces no alpha. The [Expectation-Gap] field on each dimension is not optional.
2. **Trace where the surplus lands.** The [Profit-Pool] field on each dimension is not optional; the best buy is usually the link that is "chokepoint ∩ profit-pool captor ∩ un-priced gap."
3. **Keep granularity consistent.** The Step 1 industry boundary, the Step 2 penetration denominator, and the Step 8 TAM basis must agree across all three.
4. **Second derivative first.** For cyclicals, read capex/D&A and the utilization inflection; don't capitalize peak earnings × a high P/E.
5. **Make conclusions falsifiable.** Attach "if X happens, the conclusion must be revised" to every core judgment.
6. **Roughly right beats precisely wrong.** Give reasonable ranges for size, penetration, and profit-pool shares.
7. **Stay dynamic.** Industries evolve; the analysis is a starting point, validated by the Step 11 high-frequency indicators.

## Synergy With Other Skills

- **us-value-investing / tech-earnings-deepdive:** once this skill pins down the link worth betting on, use the single-name skills to pick and cross-check a security within that link (industry → single-name funnel).
- **macro-liquidity / us-market-sentiment:** pair in Step 9 when policy/macro is a Key Force.
