# AI-Washing Track A WRDS Bridge Progress V1

## What is implemented

The filing-level WRDS bridge scaffold is now live:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/build_wrds_gvkey_permno_bridge.py`

It consumes:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/filing_event_spine_v1.csv`

And produces:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/filing_wrds_bridge_v1.csv`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_wrds_bridge_v1.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_wrds_bridge_unmatched_v1.csv`

## Current match status

Current filing-level bridge result:

- total filings: `65`
- matched via `ccmxpf_lnkhist`: `49`
- matched via `crsp.ccm_lookup` fallback: `5`
- total matched: `54`
- current unresolved tail: `11`

Coverage:

- filing-level match rate: `54 / 65 = 83.1%`
- unique `permno`: `14`
- unique `permco`: `14`

## Interpretation of the unresolved tail

The remaining `11` unresolved rows are no longer a generic identifier problem.
They are all `no_valid_link` rows.

That means:

1. the filings already have `cik` and `gvkey`
2. the WRDS bridge logic is working
3. the issue is the absence of a valid CRSP security link on the filing date

The unresolved rows currently concentrate in three identities:

- `gvkey 061409` / `CIK 0000949039`
- `gvkey 003814` / `CIK 0000787250`
- `gvkey 146539` / `CIK 0001128189`

## What WRDS diagnostics showed

Direct WRDS checks now confirm:

- host reachability is fine
- `psql` connectivity is fine
- `crsp_a_ccm.ccmxpf_lnkhist` exists and is queryable
- `crsp_a_ccm.ccm_lookup` exists and is queryable

The `ccm_lookup` fallback was useful for recovering the rows where the local
filing spine still lacked `gvkey`.

## Practical meaning for the event-study lane

This is now good enough to proceed with the first event-window pull scaffold.

The next step should be:

1. build the `permno` event pull scaffold for the matched filings
2. keep the unresolved `11` rows in a separate audit tail
3. decide later whether to:
   - drop them from the first event-study sample
   - or try a more specialized recovery pass for delisting / nonstandard link cases

## Useful supplemental source

The local fallback file remains useful for diagnostics:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/external/cik_ticker_list.csv`

It helped confirm likely identity for the previously missing-`gvkey` rows, but
it should remain a fallback / audit aid rather than the primary WRDS bridge.
