# AI-Washing Track A Event-Study Scaffold Progress V1

## What is now implemented

The first filing-level market-event scaffold is now live in code:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/build_filing_event_spine.py`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/build_filing_ai_measures.py`

These scripts produce the first two event-ready tables described in the panel
spec:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/filing_event_spine_v1.csv`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/filing_ai_measures_v1.csv`

With reports:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_event_spine_v1.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_ai_measures_v1.json`

## Current real-output status

### Filing event spine

The scaffold successfully parsed filing-level metadata from classified SEC
filenames and built a filing event table with:

- `65` filings
- years covered: `2021` to `2024`
- forms covered:
  - `10-K`: `59`
  - `10-K-A`: `6`

### Filing AI measures

The scaffold successfully aggregated filing-level narrative counts from the
classified sentence tables:

- total classified AI-sentence rows: `148`
- `Actionable`: `40`
- `Speculative`: `45`
- `Irrelevant`: `63`
- `post_chatgpt` filings: `28`

## Current identifier-bridge status

Using the broader active-annual crosswalk:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/externals/crosswalks/cik_gvkey_active_annual_allyears_2021_2024_v3.csv`

the scaffold now links most of the filing sample:

- `crosswalk_match_count = 60 / 65`
- `crosswalk_match_rate = 92.31%`
- `unique_gvkey_count = 14`

So the event-study lane is no longer blocked on the entire `cik -> gvkey`
bridge. The remaining issue is the residual unmatched tail plus the later
`gvkey -> permno` step.

## Interpretation

This is still useful progress because it narrows the real dependency:

1. filing-level event dates are recoverable now
2. filing-level AI narrative measures are recoverable now
3. the next missing layer is completing the market-identifier bridge to WRDS
   market data

That means the next capital-market implementation task should be one of:

1. inspect and resolve the `5` unmatched filing rows
2. add a direct `gvkey -> permno` or CCM-link extraction from WRDS
3. only then build daily event-window return tables

## Validation status

- Ruff passed on the new scaffold scripts and tests
- direct module smoke validation passed
- `pytest` under the Codex shell remains unreliable and appears to hang inside
  the runner itself, so direct module-level validation was used for this step

## Bottom line

The event-study lane is no longer blocked on planning ambiguity.
The filing-level scaffold is live and mostly linked.

The next data-engineering issue is:

- closing the remaining `cik -> gvkey` gaps and adding the `permno` layer
