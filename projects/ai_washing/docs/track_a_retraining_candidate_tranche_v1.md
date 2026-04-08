# AI-Washing Track A Retraining Candidate Tranche V1

## Purpose

This note records the first label-backed retraining tranche created after the
reviewed A/S boundary benchmark stabilized.

The goal is to move from rubric calibration into a controlled training update
without contaminating benchmark-only rows.

## Upstream decision

Selected playbook:
- `director/playbooks/prompt_boundary_benchmark`

Outcome:
- completed on the fixed `16`-row slice
- completed again on the reviewed `34`-row boundary pack
- Variant A and Variant B both matched the reviewed labels exactly on the
  larger pack

Interpretation:
- prompt-only or rubric-only calibration is no longer the main source of gain
- the next controlled move is a small retraining tranche under the revised
  rubric

## Inputs

Training backbone:
- `data/labels/v1/labels_master.parquet`

Frozen split registry:
- `data/metadata/splits/split_registry_v1.csv`

Reviewed boundary pack:
- `reports/final/ai_washing_classifier_boundary_review_pack_v1.csv`

Generated tranche builder:
- `src/semantic_ai_washing/classification/build_retraining_candidate_tranche.py`

## Selection rule

Only reviewed rows that already overlap the tracked `labels_master` backbone are
eligible for retraining.

Rows that come only from the held-out error pack remain benchmark-only.

This keeps the training update low blast radius and avoids leaking benchmark
rows back into the training set.

## Outputs

Tranche review file:
- `reports/final/ai_washing_classifier_retraining_candidate_tranche_v1.csv`

Summary:
- `reports/final/ai_washing_classifier_retraining_candidate_tranche_v1.json`

Revised labels master:
- `data/labels/v1/labels_master_boundary_revised_v1.parquet`
- `data/labels/v1/labels_master_boundary_revised_v1_review.csv`

## Execution result

Reviewed boundary rows:
- `34`

Training-eligible overlap rows:
- `12`

Benchmark-only rows:
- `22`

Ambiguous overlap rows:
- `0`

Actual label updates:
- `8`

Eligible split counts:
- `train`: `9`
- `validation`: `3`

Label-update split counts:
- `train`: `5`
- `validation`: `3`

## Interpretation

This is the right tranche size.

It is small enough to stay controlled, but large enough to test whether the
revised rubric can move the live model once the labels are pushed back into the
training backbone.

The important point is that only `12` of the `34` reviewed rows legitimately
feed retraining. The other `22` remain benchmark-only and should stay out of
the updated training asset.

## Evaluation constraint

The local retraining step can proceed immediately.

The full `held_out_v2` rerun is currently blocked by a missing frozen benchmark
CSV:
- `data/validation/held_out_sentences_v2.csv`

The freeze report still exists:
- `reports/validation/held_out_sentences_v2_freeze.json`

So the benchmark state is known, but the frozen `177`-row CSV is not currently
recoverable from the repository tree.

That means the honest near-term comparison surfaces are:
- the revised frozen validation split derived from `split_registry_v1`
- the regenerated IRR boundary benchmark from `adjudication.parquet`

## Next step

1. retrain `binary_relevance_then_as` on
   `labels_master_boundary_revised_v1.parquet`
2. compare the current model and the retrained model on the revised frozen
   validation split and the IRR boundary benchmark
3. restore or regenerate `held_out_v2` before claiming a fresh publication-grade
   held-out result
