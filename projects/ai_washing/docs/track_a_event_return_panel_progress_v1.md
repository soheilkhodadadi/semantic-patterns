# AI-Washing Track A Event-Return Panel Progress V1

## What is now implemented

The first market-return build is now live in code:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/build_event_return_windows.py`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/compute_filing_car.py`

These scripts extend the existing filing-level scaffold and WRDS bridge into:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/filing_event_returns_daily_v1.parquet`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_event_returns_daily_v1.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/processed/panel/filing_event_panel_v1.parquet`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/filing_event_panel_v1.json`

## Important WRDS schema correction

The conceptual design notes used `ccmsecd` / `ccmfunda` as shorthand for the
merged daily and annual market-data products.

In this WRDS environment, the actual implementation path is:

- firm-level daily returns: `crsp.dsf`
- daily market return: `crsp.dsi`
- annual fundamentals: `comp.funda`
- link tables: `crsp_a_ccm.ccmxpf_lnkhist` and `crsp_a_ccm.ccm_lookup`

This is a schema-resolution correction, not a change in design logic.

## Current real-output status

### Daily return window table

Current output summary:

- matched filings pulled into return windows: `54`
- unique `permno`: `14`
- daily return rows: `12,789`
- anchor failures: `0`
- exact filing-date trading anchors: `54`
- shifted-to-next-trading-day anchors: `0`

Window completeness:

- `CAR[-1,+1]`: `54`
- `CAR[-2,+2]`: `54`
- `BHAR 1m`: `54`
- `BHAR 3m`: `53`
- `BHAR 6m`: `52`
- `BHAR 12m`: `39`

### Filing-level event panel

Current output summary:

- filing rows: `54`
- nonmissing `car_m1_p1`: `54`
- nonmissing `car_m2_p2`: `54`
- nonmissing `bhar_6m`: `52`
- filing dates covered: `2021-01-21` to `2024-11-01`

The panel already includes:

- `car_m1_p1`
- `car_m2_p2`
- `bhar_1m`
- `bhar_3m`
- `bhar_6m`
- `bhar_12m`
- filing-level AI narrative shares and counts
- WRDS-link metadata

## Interpretation

This is enough to stop treating the event-study lane as planning only.

We now have:

1. filing-level event dates
2. filing-level AI narrative measures
3. WRDS-linked `permno`
4. daily return windows
5. first short-run CARs and longer-horizon BHARs

## Immediate next steps

1. attach annual controls from `comp.funda`
2. define the first regression-ready event sample
3. keep the unresolved `11` filing rows outside the first event panel
4. add factor-adjusted robustness only after the market-adjusted panel is used

## Bottom line

The event-study lane now has a usable first filing-level return panel.
