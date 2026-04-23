# Full-Sample WRDS Raw Pull Progress V1

## Purpose

This note records the broad-sample WRDS raw-data pull that was run in parallel
with the provisional `conf49` API-A tranche.

The goal was to avoid waiting for the classifier merge before pulling the slow
capital-market inputs that depend mainly on firm identity and year coverage.

## Backbone used

Source narrative backbone used for this raw pull:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/processed/aggregates/firm_year_narrative_measures_prelim_clean_2016_2025_refresh_v1.parquet`

Crosswalk:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/externals/crosswalks/cik_gvkey_ever_speaker_2016_2025_refresh_v1.csv`

Derived broader WRDS bridge:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/full_sample_wrds_backbone_v1.csv`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/full_sample_wrds_backbone_v1.json`

## Broad-sample WRDS backbone summary

Coverage:
- firm-year rows: `13,777`
- years: `2016-2025`
- unique firms (`cik`): `5,084`
- unique linked `gvkey`: `4,332`
- matched `permno` rows: `10,564`
- matched `permno` rate: `76.68%`
- unique linked `permno`: `3,704`

Bridge statuses:
- `matched`: `10,552`
- `matched_via_ccm_lookup_fallback`: `12`
- `no_valid_link`: `3,213`

Interpretation:
- this `13,777`-row backbone is an observed AI-talking firm-year surface, not yet the fully expanded annual ever-speaker panel
- with `5,084` unique firms across `10` years, a simple full ever-speaker scaffold would be `50,840` firm-year rows before later market-link attrition
- this is still enough linked coverage to start the broader market-data lane now
- the unresolved tail should stay as an audit tail rather than a blocker

Important implication:
- the raw WRDS pulls remain reusable because they were keyed on the linked `gvkey` / `permno` universe, not on each currently observed speaker-year row
- after the API-backed hybrid panel rebuild, the next scaffold step should be to expand the annual panel to zero-talk years for every ever-speaker firm and then merge the already-pulled raw WRDS layers across that fuller grid

## Raw WRDS pulls completed

Outputs:
- fundamentals annual raw:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/wrds_comp_funda_full_sample_v1.parquet`
- CRSP monthly stock raw:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/wrds_crsp_msf_full_sample_v1.parquet`
- CRSP monthly market index raw:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/wrds_crsp_msi_full_sample_v1.parquet`
- pull report:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/wrds_full_sample_raw_pull_v1.json`

Raw pull counts:
- `comp.funda` rows: `35,054`
- `comp.funda` `gvkey` coverage: `3,948`
- `crsp.msf` rows: `316,921`
- `crsp.msf` `permno` coverage: `3,652`
- `crsp.msi` rows: `120`

Query windows:
- fundamentals: `2015-01-01` to `2025-12-31`
- monthly market data: `2015-01-01` to `2026-12-31`

## Why this was the right move

This raw-data work did not need to wait for the final hybrid classifier merge.

It depends mainly on:
- firm identity
- calendar coverage
- WRDS link coverage

So pulling it now reduces later wall-clock delay when the hybrid-backed panel is
ready to rebuild.

## What this does not replace

This does not replace the filing-level daily event-study pull.

Daily filing-window returns should still be rebuilt after the broader
hybrid-backed filing panel is available, because those windows depend on the
final filing-level surface.

## Next steps

1. let the running `conf49` API-A tranche finish
2. merge shard outputs back into the deferred master sheet
3. rebuild the broader hybrid-backed filing / firm-year panel
4. derive full-sample lagged controls and market features from these raw WRDS
   pulls
5. rerun the CAR / `BHAR 6m` regression family on the expanded panel

## Update after annual scaffold rebuild

The annual ever-speaker expansion step is now done on the pre-hybrid narrative
surface.

See:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/projects/ai_washing/docs/track_a_ever_speaker_panel_rebuild_v1.md`

That means the remaining missing piece is no longer the annual scaffold itself.
It is the narrative-side hybrid refresh after the running API-A tranche closes.
