# Reading SEC Filings Directly

Fetch and read the filings yourself (web fetch, or `curl` for a raw copy). Don't rely on a pre-parsed data feed: XBRL tag choices vary by company and period, and a parser that picks the wrong tag (a revolver booked outside "current portion of long-term debt", a share count tagged in thousands, a 53-week year labelled as the next fiscal year) produces confident wrong numbers. Scripts in this bundle are for calculation only (`core_eps.py`, `valuation.py`); every input number comes from a filing you read, with its URL in the workpaper.

## 1. Finding the documents

| Need | Where |
|---|---|
| Filing list (any form) | `https://data.sec.gov/submissions/CIK<10-digit CIK>.json` — every recent filing with form, date, accession and primary document; download it with `curl` and read it locally (web fetch truncates and summarizes JSON). Or the HTML list: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=<TICKER or CIK>&type=<form>&dateb=&owner=include&count=40` |
| Documents in one filing | `https://www.sec.gov/Archives/edgar/data/<CIK>/<accession without dashes>/` (directory) or `.../<accession>-index.html` (has a Type column: 10-Q, EX-99.1, EX-10.x) |
| Earnings release | The EX-99.1 document of the Item 2.02 8-K (often named `earningsrelease…htm` or `ex991…htm`) |
| Capital raises and their final terms | **424B2/424B5** prospectus supplements (final size, price, conversion rates; a later 424B5 or 8-K reports the underwriters' over-allotment exercise), S-3/S-3ASR shelf registrations, FWP term sheets. 8-Ks often announce the deal but not the final numbers |
| Governance, pay, share classes | DEF 14A proxy (pay, related parties, voting); DEF 14C / PRE 14C (actions approved by written consent, e.g. a new share class); Form 4 (insider trades) |
| Exact statement tables | XBRL viewer pages `R1.htm, R2.htm, …` in the filing directory. Numbering differs by company and filing — open `FilingSummary.xml` in the same directory first; it maps each R page to its name (balance sheet, income statement, cash flow, each note and its "Details" table). The table is at the top of each R page; the long XBRL definitions below it are boilerplate — read the table only |
| Narrative notes (tax, legal, debt, restructuring, segments) | The main 10-K/10-Q `.htm`, or the note's R page. Ask for the specific note, not the whole document |
| Call transcript | Web search ("<company> Q3 2026 earnings call transcript"). If none is indexed yet: the IR site's webcast/prepared remarks, or an Item 7.01 8-K presentation. Otherwise say "call not reviewed" in the memo |
| Older history (cycle base rate, 10–15 yrs) | Older 10-Ks' R pages; 10-K "Selected financial data" (pre-2021 filings); S-1/Form 10 for pre-IPO years |

**How to fetch.** Prefer `curl -s -A "<name> <contact email>" <url> -o file` and read the saved file: it is exact, while web fetch may summarize long pages and JSON. SEC asks for a contact in the user agent; if your environment blocks that, a descriptive agent without an email (e.g. `"research-agent"`) usually works — on a 403, retry with the other form. Use web fetch for short pages (R pages, releases) when curl isn't available.

## 2. Precision rules (fetch tools can summarize)

Long pages may come back summarized rather than verbatim. For every number that enters a calculation:
- Get it **verbatim with its row label and column header** (period end date, 3 vs 9 months, units). Prefer the small R page over the full document.
- **Cross-foot before using it:** segments sum to the total; quarters sum to the fiscal year; assets = liabilities + equity; the EPS numerator ÷ diluted shares = reported diluted EPS (±$0.01); the cash-flow statement's ending cash = the balance sheet's.
- If a number can't be confirmed verbatim, re-fetch the smaller page or the saved file. Never fill a gap from memory or a data aggregator; mark an estimate `(E)` and say how it was made.
- Record the URL next to each number in the workpaper.

## 3. What to collect (the data sheet)

Build one workpaper table: 5 fiscal years + the last 8 quarters + TTM. Label columns by **fiscal** period as the cover page states it (52/53-week companies: a year ending 2026-01-03 is fiscal 2025).

**P&L:** revenue · gross profit · each opex line · operating income · interest expense · other income (expense) · pretax income · tax expense (and ETR — flag periods outside 5–35% or far from the multi-year norm; those hold discrete items) · net income · NCI · net income to common · **diluted EPS numerator from the EPS note** (after preferred dividends, earnings allocated to participating securities/unvested restricted stock under the two-class method, if-converted effects) · weighted diluted shares · reported diluted EPS.

**One-off candidates (5 years):** restructuring/reorganization · impairments · legal and environmental charges and recoveries · gains/losses on asset or business sales · investment marks · debt extinguishment · acquisition/integration costs · refunds or recoveries of earlier-period costs · discrete tax items (tax-rate reconciliation).

**Cash flow:** CFO · capex · finance-lease principal · D&A · SBC · acquisitions · buybacks · dividends · cash taxes paid and cash interest paid (supplemental disclosure).

**Balance sheet:** cash and short-term investments · **every debt line** — revolver/short-term borrowings, commercial paper, current portion, long-term notes and term loans, finance leases (read the debt note: the face of the balance sheet often merges or omits the revolver, and quarter-end balances can differ from the average drawn) · operating leases · NCI · preferred · contract liabilities (customer advances) · receivables · inventory · pension deficit.

**Off-balance-sheet and debt-like items:** search the 10-K/10-Q for "sold", "factoring", "receivable purchase agreement", "securitization", "supply chain finance", "guarantee". Receivables sold without recourse lift CFO and hide debt — add the outstanding balance to net debt and reverse the period's CFO benefit (catalog §9). Also legal and environmental contingencies with estimates.

**Shares and capital actions:** shares outstanding on the latest cover page · splits or stock dividends (equity note, 8-Ks, DEF 14C) — restate all per-share history; if announced but not yet effective, keep pre-split figures and note the ratio and date · every filing after the period end: 8-Ks (items 1.01, 2.03, 3.02, 5.02, 7.01, 8.01) **and** 424B prospectuses for final deal sizes and over-allotments. Each becomes a `capital_actions` row in the valuation input.

## 4. Deriving periods

- 10-Qs give the quarter and year-to-date for the P&L, but **cash flow is year-to-date only**: Q2 = 6M − Q1; Q3 = 9M − 6M; Q4 = FY − 9M. Mark derived quarters `*`.
- Q4 EPS and Q4 diluted shares cannot be derived by subtraction (share counts are averages and anti-dilution differs between loss and profit periods). Take them from the Q4 earnings release.
- TTM = latest 9M (or 6M/3M) + prior FY − prior-year comparable YTD. Tie each quarter to its own EPS note. Add the four reported EPS values for trailing GAAP EPS, and add the four unrounded quarterly Core EPS values for trailing Core EPS. Restate all quarters to the same split basis. Record trailing earnings to common as a separate flow and the valuation share count as a dated balance.
- **Release out, 10-Q/10-K not yet filed** (2–6 weeks after quarter end): the newest quarter exists only in the 8-K EX-99.1. Use it, and follow the earnings-normalization "release out" steps (cash-flow estimates marked `(E)`, note checks deferred to Update mode).
