# Track A Held-Out v3 Benchmark Results v1

## Freeze status

- Frozen benchmark: `data/validation/held_out_v3/held_out_sentences_v3.csv`
- Freeze report: `reports/final/ai_washing_heldout_v3_freeze_v1.json`
- Rows: `177`

Label counts:

- `Irrelevant`: `87`
- `Actionable`: `66`
- `Speculative`: `24`

## Assistive prelabel quality

Reviewed sheet:

- `data/validation/held_out_v3/held_out_sentences_v3_review_sheet_labelled.csv`

Assistive score outputs:

- `reports/final/ai_washing_heldout_v3_assistive_score_v1.json`
- `projects/ai_washing/docs/track_a_heldout_v3_assistive_score_v1.md`

Important validation:

- the labelled review sheet preserved the original `assistive_label`,
  `assistive_confidence`, and `assistive_rationale` columns exactly relative to
  the generated assistive review sheet
- so the assistive score is a real comparison, not an artifact of later edits

Observed score:

- overall agreement: `177 / 177`
- `Actionable/Speculative` agreement: `90 / 90`

This means the final reviewed `held_out_v3` labels fully agreed with the
`gpt-5-mini` assistive labels on this benchmark.

## Local model benchmark

Benchmark matrix:

- `reports/evaluation/model_benchmark_matrix_heldout_v3_v1.json`
- `reports/evaluation/model_benchmark_matrix_heldout_v3_v1.md`
- `artifacts/models/prelim_selected_model_heldout_v3_v1.json`

Per-model reports:

- `reports/evaluation/models_heldout_v3_v1/mpnet_prelim_v1.json`
- `reports/evaluation/models_heldout_v3_v1/mpnet_logreg_prelim_v1.json`
- `reports/evaluation/models_heldout_v3_v1/binary_relevance_then_as_v1.json`

Runtime posture:

- skipped candidate: `legacy_two_stage_mpnet_rules`
- reason: the legacy path still routes through the old `core.classify` runtime,
  which is not the path we want to promote for publication benchmarking

Benchmark outcome:

- status: `no_winner`
- reason: no modern local candidate cleared the minimum gate on `held_out_v3`

`held_out_v3` results:

- `binary_relevance_then_as_v1`
  - accuracy: `0.6836`
  - macro F1: `0.6326`
  - binary relevance accuracy: `0.7853`
  - A/S conditional accuracy: `0.7556`
- `mpnet_logreg_prelim_v1`
  - accuracy: `0.6667`
  - macro F1: `0.6224`
  - binary relevance accuracy: `0.7684`
  - A/S conditional accuracy: `0.7667`
- `mpnet_prelim_v1`
  - accuracy: `0.6215`
  - macro F1: `0.5825`
  - binary relevance accuracy: `0.7401`
  - A/S conditional accuracy: `0.7556`

Secondary signal:

- on `irr_boundary_benchmark`, `mpnet_logreg_prelim_v1` is strongest
  - accuracy: `0.8000`
  - macro F1: `0.7972`
  - A/S conditional accuracy: `0.8714`

## Interpretation

The current evidence supports a layered local design more than a single-model
promotion:

1. `binary_relevance_then_as_v1` is strongest on overall `held_out_v3` accuracy
   and binary relevance
2. `mpnet_logreg_prelim_v1` is stronger on the harder A/S and IRR surfaces
3. no single local model is publication-ready on the rebuilt benchmark

## Next step

The next benchmark should be the local layered design:

1. binary relevance gate from `binary_relevance_then_as_v1`
2. local A/S resolution from `mpnet_logreg_prelim_v1`
3. compare that layered local result against:
   - `held_out_v3`
   - `irr_boundary_benchmark`
   - `frozen_validation_split`

Only after that should we decide whether retraining alone is enough or whether
to open the selective-defer API lane.
