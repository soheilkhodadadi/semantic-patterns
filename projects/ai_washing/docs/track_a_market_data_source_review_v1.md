# AI-Washing Track A Market-Data Source Review V1

## Purpose

This note records the recommended WRDS/CRSP/Compustat data posture for the first
capital-market lane in Track A.

It answers:
1. which dataset family we should use for a first filing-date market-reaction test
2. whether daily or monthly data are the right first choice
3. whether the merged CRSP/Compustat products can simplify controls handling
4. where event dates should come from

## Local WRDS reference files reviewed

Observed under `/Users/soheilkhodadadi/DataWork/WRDS`:
- `CRSP_Compustat_Merged_Database_Guide.pdf`
- `Security Daily.pdf`
- `Fundamentals Annual.pdf`
- `CRSP Stock Monthly with Compustat Fundamentals Annual.pdf`
- `Compustat Fundamentals Annual with CRSP Stock Monthly.pdf`

## External sources reviewed

Official/primary sources:
- CRSP/Compustat Merged Database overview:
  https://www.crsp.org/research/crsp-compustat-merged-database/
- Accounting Horizons filing-event methodology example (uses CRSP Daily Stock
  File for filing-date event returns):
  https://aaahq.org/portals/0/newsroom/sec%20filings%20article%20-%20ah%20dec%202017.pdf

Nearby design analog reviewed locally:
- `paper/literature/AI_Washing_Mar2026.pdf`
  - uses short-run CAR and longer-horizon abnormal returns around earnings-call
    dates, not 10-K filing dates

## Main design choice

### 1. Use daily data for the first filing-date event study

For a first serious filing-date market-reaction test, the correct first choice
is **daily** data.

Reason:
- filing-date event windows are short-horizon events
- the usual first specification is a small trading-day window such as:
  - `[-1, +1]`
  - `[-2, +2]`
  - or a three-day CAR centered on day 0
- monthly data are too coarse for that question

The Accounting Horizons filing-event example explicitly computes abnormal filing
returns from the **CRSP Daily Stock File** over a `[-2, +2]` event window.

### 2. Monthly data are still useful later, but not for the first event window

Monthly data can still be useful for:
- longer-horizon BHAR robustness
- post-event drift summaries
- reduced-cost exploratory checks

But they should be treated as secondary, not as the main event-study input.

## Recommended WRDS dataset pairing

### First-choice pairing

For the first Track A market-reaction lane, use:

1. **Security Daily (`ccmsecd`)**
- for daily security returns and daily event-window market variables

2. **Fundamentals Annual (`ccmfunda`)**
- for annual controls and firm fundamentals

Why this pairing is the cleanest:
- `ccmsecd` gives the daily granularity needed for filing-date CARs
- `ccmfunda` gives the control layer without forcing us through a monthly-return
  table we do not need for the first event study
- both live inside the merged CCM family, which reduces identifier drift

### Second-choice / optional supplementary files

Potential later supplements:
- `ccmmsffunda`
  - CRSP Stock Monthly with Compustat Fundamentals Annual
  - useful for monthly long-horizon return checks
- `ccmfundaprice`
  - Compustat Fundamentals Annual with CRSP Stock Monthly
  - useful if we want a fundamentals-first convenience extract with linked
    monthly price fields

These are helpful, but not the first file to build the short-window event-study
lane.

## Event-date source decision

### 3. Use SEC filing dates, not WRDS dates, as the canonical event date

The event date for the filing-date study should come from the SEC source:
- indexed SEC filenames already contain the filing date
- the refresh index and extracted sentence tables preserve enough metadata to
  recover it deterministically

Recommended rule:
- event date = SEC filing date parsed from the EDGAR filename
- returns = WRDS/CRSP daily returns around that date
- controls = WRDS/CCM annual fundamentals

This is safer than trying to infer filing dates from market-data products.

## What the local AI-washing literature analog implies

The reviewed local paper `AI_Washing_Mar2026.pdf` is useful as a design analog,
but not a drop-in blueprint:
- it studies short-run and long-run abnormal returns
- but around **earnings-call dates**, not 10-K filing dates

Takeaway:
- keep the general return-design logic
- do not copy the event definition blindly

## Recommended first implementation

### First serious test

Build a filing-date event-study lane with:
- event date: SEC 10-K filing date
- return source: `ccmsecd`
- control source: `ccmfunda`
- first windows:
  - `[-1, +1]`
  - `[-2, +2]`

Expected first dependent variables:
- market-adjusted CAR
- optionally factor-adjusted CAR if we decide the added complexity is worth it

### What not to do first

Do not start by trying to solve all of the following at once:
- daily event windows
- long-run drift
- analyst reactions
- valuation levels
- financing events

That is too much for the first Track A capital-market lane.

## Immediate next tasks

1. Create an event-ready filing table with explicit `filing_date` per firm-year
   filing.
2. Decide the first abnormal-return specification:
   - market-adjusted CAR
   - or factor-adjusted CAR
3. Define the minimum variable pull from `ccmsecd` and `ccmfunda`.
4. Treat monthly return files as optional later robustness inputs, not the main
   event-study backbone.

## Bottom line

For the first filing-date market-reaction test:
- use **daily** CRSP/CCM data, not monthly
- use **`ccmsecd` + `ccmfunda`** as the main pair
- use the **SEC filing date** as the event anchor
- keep monthly merged files for later long-horizon robustness, not for the core
  event window
