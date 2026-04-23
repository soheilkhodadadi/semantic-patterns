# AI-Washing Track A Event-Ready Panel Spec V1

## Purpose

This note defines the first concrete data product for the capital-market lane:
an event-ready filing panel that can support:
- filing-date event-study regressions
- post-filing drift tests
- ChatGPT interaction designs

It translates the design note into an implementation scaffold tied to the
current repo structure.

## First implementation target

Build one filing-level panel where each row is:
- one firm
- one 10-K filing
- one SEC filing date
- one linked market-identifier spine
- one set of AI narrative and credibility measures
- one set of lagged annual controls

That table should be sufficient to generate:
- daily event windows
- `CAR[-1,+1]`
- `CAR[-2,+2]`
- first cross-sectional filing-date regressions

## Why this panel comes first

The current panel code under:
- `src/semantic_ai_washing/aggregation/build_panel.py`

is a firm-year merge scaffold.

That is useful, but it is not enough for the first market-reaction lane because
the event study is filing-date based, not only firm-year based.

So the next panel should be filing-level first, then optionally aggregated back
to firm-year later.

## Canonical input families

### 1. SEC filing-event backbone

Source:
- refreshed SEC filing index / manifest outputs
- extracted sentence tables and classification outputs

Required fields:
- `cik`
- `company_name`
- `filing_year`
- `filing_date`
- `accession_number` or other filing-level unique ID
- `source_file`
- `form_type`

Canonical event date:
- SEC 10-K filing date parsed from EDGAR metadata

Do not infer event dates from WRDS.

### 2. Filing-level AI measurement layer

Source:
- provisional hybrid classifier outputs
- narrative-measure build outputs
- patent-backed credibility / mismatch outputs

Required fields:
- filing-level AI sentence counts:
  - `n_actionable`
  - `n_speculative`
  - `n_irrelevant`
  - `n_ai_total`
- filing-level shares:
  - `share_actionable`
  - `share_speculative`
  - `share_irrelevant`
- filing-level posture flags:
  - `any_actionable`
  - `first_actionable_intro`
  - `post_chatgpt`
- credibility / mismatch measures:
  - `ai_patent_stock`
  - `ai_patent_flow`
  - `disclosure_patent_mismatch`
  - `credible_ai_disclosure`

### 3. Market-identifier link layer

Source:
- WRDS / CCM identifier bridge
- existing firm-identity review outputs
- current local bridge candidate:
  - `data/externals/crosswalks/cik_gvkey_active_annual_allyears_2021_2024_v3.csv`

Required fields:
- `cik`
- `gvkey`
- `permno`
- `permco` if available
- link validity dates if available

Preferred matching spine:
- `cik -> gvkey -> permno`

If multiple securities exist:
- prefer the primary common-equity security
- record the selection rule explicitly in the output QC

### 4. Daily return layer

Primary source:
- actual implementation in this WRDS environment:
  - `crsp.dsf` for firm-level daily returns
  - `crsp.dsi` for market return benchmarks

Required fields:
- `permno`
- `date`
- `ret`
- `prc`
- `shrout`
- `vol`
- delisting return if available through the selected extract

Derived fields:
- `mktcap`
- event-time index relative to filing date
- event-window flags

### 5. Annual controls layer

Primary source:
- actual implementation in this WRDS environment:
  - `comp.funda`

Required fields:
- `gvkey`
- `fyear`
- `datadate`
- `at`
- `sale`
- `ni`
- `ib`
- `che`
- `dltt`
- `capx`
- `xrd`
- `emp`

Derived controls:
- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`

Use lagged controls where the event-study regression is interpreted as a market
response to filing content.

## Proposed output tables

### Table A. Filing event spine

Path:
- `data/interim/market/filing_event_spine_v1.csv`

Unit:
- one row per filing

Columns:
- `filing_id`
- `cik`
- `filing_date`
- `filing_year`
- `source_file`
- `form_type`
- `gvkey`
- `permno`
- `permco`
- `post_chatgpt`

Purpose:
- canonical merge key for all later market-event outputs

### Table B. Filing narrative measures

Path:
- `data/interim/market/filing_ai_measures_v1.csv`

Unit:
- one row per filing

Columns:
- `filing_id`
- AI narrative counts / shares
- credibility / mismatch measures
- any first-introduction flags

Purpose:
- keeps the measurement layer separate from the return layer

### Table C. Daily return window table

Path:
- `data/interim/market/filing_event_returns_daily_v1.parquet`

Unit:
- one row per filing-date x trading-date observation

Columns:
- `filing_id`
- `permno`
- `date`
- `event_day`
- `ret`
- `mktcap`
- event-window membership flags:
  - `in_window_m1_p1`
  - `in_window_m2_p2`

Purpose:
- reusable base for CAR construction and later robustness

### Table D. Filing event-study panel

Path:
- `data/processed/panel/filing_event_panel_v1.parquet`

Unit:
- one row per filing

Columns:
- event spine keys
- filing narrative measures
- lagged annual controls
- short-window outcomes:
  - `car_m1_p1`
  - `car_m2_p2`

Purpose:
- first regression-ready event-study table

### Table E. Drift / long-run panel

Path:
- `data/processed/panel/filing_drift_panel_v1.parquet`

Unit:
- one row per filing

Columns:
- filing-level narrative measures
- event-date identifiers
- long-run outcomes:
  - `bhar_1m`
  - `bhar_3m`
  - `bhar_6m`
  - `bhar_12m`

Purpose:
- second-lane lazy-prices / shareholder-consequence analysis

## Minimal variable contract

### Core IDs

- `filing_id`
- `cik`
- `gvkey`
- `permno`
- `filing_date`
- `filing_year`

### Core AI variables

- `n_actionable`
- `n_speculative`
- `n_irrelevant`
- `n_ai_total`
- `share_actionable`
- `share_speculative`
- `credible_ai_disclosure`
- `disclosure_patent_mismatch`
- `post_chatgpt`

### Core controls

- `ln_assets_lag`
- `leverage_lag`
- `cash_lag`
- `rd_intensity_lag`
- `roa_lag`
- `sales_growth_lag`

### Core outcomes

- `car_m1_p1`
- `car_m2_p2`
- later:
  - `bhar_3m`
  - `bhar_6m`
  - `bhar_12m`

## First-pass specification families

### Spec 1. Filing-date reaction

Dependent variable:
- `car_m1_p1`

Main regressors:
- `credible_ai_disclosure`
- `disclosure_patent_mismatch`
- `share_actionable`
- `post_chatgpt`
- mismatch x post-ChatGPT

Controls:
- lagged size
- lagged leverage
- lagged profitability
- year fixed effects
- industry fixed effects if coverage is stable enough

### Spec 2. Alternative event window

Dependent variable:
- `car_m2_p2`

Use as a robustness check, not a separate headline.

### Spec 3. Drift lane

Dependent variable:
- `bhar_6m` or `bhar_12m`

Main regressors:
- `disclosure_patent_mismatch`
- credible vs mismatch portfolio sort
- post-ChatGPT interactions

## Existing repo pieces to reuse

Use directly:
- `src/semantic_ai_washing/data/pull_compustat_controls.py`
- `src/semantic_ai_washing/data/clean_crsp.py`
- `src/semantic_ai_washing/data/clean_compustat.py`
- `src/semantic_ai_washing/aggregation/build_panel.py`

Interpretation:
- the current control and merge scripts are useful starting points
- but the event-study lane needs new filing-level market tables, not just a
  firm-year merge

## Recommended implementation order

### Step 1. Build filing event spine

New output:
- `data/interim/market/filing_event_spine_v1.csv`

Checks:
- one row per filing
- no duplicated `filing_id`
- valid `filing_date`
- linked `permno` coverage summary

### Step 2. Attach filing-level AI measures

New output:
- `data/interim/market/filing_ai_measures_v1.csv`

Checks:
- filing-level sentence counts reconcile to classified sentence tables
- mismatch measure definition is explicit and versioned

### Step 3. Build daily event-return window table

New output:
- `data/interim/market/filing_event_returns_daily_v1.parquet`

Checks:
- each filing has the expected number of trading days in the requested window
- missing-return cases are counted and reported

### Step 4. Compute CAR table

New output:
- `data/processed/panel/filing_event_panel_v1.parquet`

Checks:
- CAR construction is deterministic
- market-adjusted version is saved first
- factor-adjusted version can be a second output, not a prerequisite

### Step 5. Add drift table

New output:
- `data/processed/panel/filing_drift_panel_v1.parquet`

Checks:
- horizon definitions are explicit
- overlapping-event handling is documented

## Immediate coding implication

The clean next code additions should be a small event-study family under:
- `src/semantic_ai_washing/analysis/`

Suggested first scripts:
- `build_filing_event_spine.py`
- `build_filing_ai_measures.py`
- `build_event_return_windows.py`
- `compute_filing_car.py`

That is cleaner than overloading the current annual panel builder.

## Bottom line

The next concrete economics asset should be:
- a filing-level event-ready panel, not a generic firm-year merge

That panel should combine:
- SEC filing dates
- hybrid AI narrative measures
- patent-backed credibility / mismatch
- WRDS daily returns
- lagged annual controls

Once that exists, the first serious event-study result becomes a straightforward
implementation task rather than a conceptual plan.
