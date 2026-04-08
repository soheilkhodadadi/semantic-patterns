# Held-out V3

This folder is the rebuilt primary benchmark lane for the current revised
rubric.

## Files

- `held_out_sentences_v3_candidate_pool.csv`
  - normalized repo-local candidate pool
  - built from the recovered historical v2 review source
  - invalid rows excluded
  - historical candidate and assistive columns preserved under `legacy_*`
- `held_out_sentences_v3_review_sheet.csv`
  - active human review sheet
  - current canonical `label` remains blank until reviewed
  - current `assistive_*` columns are reserved for fresh API-assisted prelabels
- `held_out_sentences_v3_review_slice40.csv`
  - first small working slice for bounded review / smoke tests
- `held_out_sentences_v3.csv`
  - future frozen benchmark asset
  - should only be created after the review sheet is fully reviewed

## Rules

- `held_out_v3` is benchmark-only.
- Do not merge it into training.
- Preserve historical assistive outputs only as `legacy_*` context.
- Use fresh current-rubric assistive prelabels for the live review sheet.
