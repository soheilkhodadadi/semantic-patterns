# AI-Washing Track A 2025 Classification Spot Check V1

## Purpose

This note records a quick QC pass over the completed `2025` classified sentence
table before the patent rebuild and panel refresh continue.

## Source checked

- `data/processed/classifications_refresh_2025_v1/year=2025/model=prelim_selected_model_v1/classified_sentences.parquet`
- classification report:
  - `reports/classification/active_window_coverage_2025_refresh_v1.json`

## Completion status

- classification status: `passed`
- rows classified: `40,902`
- model path used:
  - selected model id: `binary_relevance_then_as_v1`
  - runtime report model id: `prelim_selected_model_v1`

## Label distribution

- `Irrelevant`: `22,831`
- `Actionable`: `12,742`
- `Speculative`: `5,329`

## Spot-check summary

### What looks good

- Many `Actionable` examples look like genuine current-use or product/deployment
  statements.
- Many `Speculative` examples look like pipeline, growth, roadmap, or
  commercialization language rather than realized capability.
- Many `Irrelevant` examples correctly capture risk, compliance, regulatory, or
  generic AI-market language.

### What still looks risky

- Some very long rows remain, including a clear header-style artifact:
  - sentence id `caecc3e0a2e6b5ae`
- Some borderline rows look plausible under more than one label depending on how
  sharply the rubric distinguishes:
  - current deployment vs future-facing commercialization
  - relevant vs generic AI-risk/compliance language
  - product mention vs broad strategic narrative
- Some rows are long, list-heavy, or clause-heavy enough that sentence
  segmentation quality should still be treated as an open QC concern even after
  cleanup.

## Interpretation

The `2025` classification output looks usable enough to continue the data-refresh
lane, but it is **not** strong enough to treat the current classifier as final
for the paper rerun.

The spot check supports the same conclusion already implied by the held-out
metrics:
- the refreshed `2025` coverage lane is complete
- the classifier-upgrade lane still needs to happen before final empirical
  reruns

## Next use of this note

Use this QC note as the handoff into:
- the patent rebuild on `2014-2025` with application timing
- the classifier-upgrade diagnostic plan
