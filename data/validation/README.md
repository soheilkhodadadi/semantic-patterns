# Validation Assets

This directory holds benchmark assets and recovery sources for classifier
evaluation.

## Current repo-local benchmark assets

- `irr_boundary_benchmark_v1.csv`
  - current diagnostic boundary benchmark
  - `120` rows
  - built from the adjudication chain in `data/labels/v1`
  - use for hard-case diagnostic evaluation, not as the sole publication-grade
    held-out benchmark

## Recovery sources

- `recovery_sources/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv`
  - recovered from external storage and staged into the repo to preserve the
    benchmark rebuild path
  - `180` rows before exclusions
  - `177` effective rows after excluding the three invalid sentence IDs listed
    in `reports/validation/held_out_sentences_v2_freeze.json`
  - this file is a candidate review sheet only
  - it is not a frozen benchmark because the final `label` column is blank

## Current primary benchmark rebuild lane

- `held_out_v3/held_out_sentences_v3_candidate_pool.csv`
  - normalized `177`-row candidate pool
  - invalid rows excluded
  - historical candidate and assistive fields preserved as `legacy_*`
- `held_out_v3/held_out_sentences_v3_review_sheet.csv`
  - active human review sheet for the rebuilt publication benchmark
- `held_out_v3/held_out_sentences_v3_review_slice40.csv`
  - first bounded review slice
- `held_out_v3/held_out_sentences_v3.csv`
  - future frozen benchmark output
  - currently not created because review is still pending

Supporting runtime artifacts:
- `reports/final/ai_washing_heldout_v3_preparation_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_progress_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_dry_run_v1.json`
- `reports/final/ai_washing_heldout_v3_freeze_v1.json`
- `director/config/api_assistive_policy_heldout_v3.yaml`

## Historical registry caveat

The older registry files under `reports/validation/` reference historical
assets such as:

- `data/validation/held_out_sentences.csv`
- `data/validation/held_out_sentences_v2.csv`

Those files are not present in the current checkout. Treat the older registry
JSON files as historical evidence, not as the live source of truth.

Use `reports/final/ai_washing_validation_asset_registry_v3.json` as the
current live asset map.
