# Ever-Speaker Panel Rebuild V1

## Purpose

This note records the refreshed annual ever-speaker panel rebuild that expands
the observed `2016-2025` AI-talking firm-years into the full annual
ever-speaker scaffold.

This is the pre-hybrid version of the annual panel:
- it uses the refreshed observed narrative measures already on disk
- it keeps zero-talk years for every ever-speaker firm
- it merges the readable patent, WRDS-link, annual-controls, and annual-market
  inputs that are available now

The later post-API rebuild should replace only the narrative-side counts and
derived AI measures, not the whole panel architecture.

## Canonical outputs

Scaffold:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/processed/panel/canonical/ever_speaker_scaffold_2016_2025_prehybrid_v1.parquet`

WRDS bridge:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/ever_speaker_wrds_backbone_2016_2025_prehybrid_v1.csv`

Annual controls:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/annual_controls_ever_speaker_2016_2025_prehybrid_v1.csv`

Annual market features:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/interim/market/annual_market_features_ever_speaker_2016_2025_prehybrid_v1.csv`

Merged panel:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.parquet`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.csv`

Build report:
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/analysis/ever_speaker_panel_2016_2025_prehybrid_v1.json`

## What changed relative to the `13,777`-row backbone

The earlier `13,777`-row WRDS backbone was the observed AI-talking firm-year
surface only.

The rebuilt annual ever-speaker panel is the true full scaffold:
- firms: `5,084`
- years: `2016-2025`
- total rows: `50,840`
- positive-talk rows: `13,777`
- zero-talk rows retained: `37,063`

That means the annual panel is now aligned with the intended research design:
if a firm ever talks about AI during `2016-2025`, it remains in the annual panel
for the full sample span.

## Current coverage

Identity and links:
- rows with `gvkey`: `43,313`
- unique `gvkey`: `4,332`
- rows with `permno`: `27,750`
- unique `permno`: `3,693`

Controls and annual market:
- rows with nonmissing `ln_assets`: `31,291`
- rows with nonmissing annual return: `23,771`

Bridge statuses:
- `matched_via_ccm_lookup_fallback`: `21,072`
- `matched`: `6,678`
- `no_valid_link`: `15,563`
- `unmatched`: `7,527`

Interpretation:
- the annual panel scaffold is now correct
- market and control coverage are partial but already useful
- the unresolved tail is now a normal market-link / Compustat coverage issue,
  not a panel-construction issue

## Current limitation

This panel is still **pre-hybrid**.

It is built from:
- `binary_relevance_then_as_v1` for `2016-2024`
- `prelim_selected_model_v1` for `2025`

So this panel is the canonical annual scaffold and raw-merge base, but not yet
the final narrative surface for the paper.

## Next step

After the running `conf49` API-A tranche finishes:
1. merge the shard outputs back into the deferred master sheet
2. rebuild the broader narrative measures on the hybrid-backed labels
3. rerun this annual panel build on the hybrid-backed narrative measures
4. rerun the filing-level and annual empirical outputs on that rebuilt panel
