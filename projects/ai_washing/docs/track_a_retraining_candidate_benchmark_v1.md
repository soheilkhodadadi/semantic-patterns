# AI-Washing Track A Retraining Candidate Benchmark V1

## Purpose

This note records the first local retraining experiment after the revised
boundary tranche was pushed back into `labels_master`.

The purpose is narrow:
- retrain the current binary relevance then A/S model on the revised labels
- compare the old and new binary models on the same revised benchmark surfaces
- decide whether the revised tranche is strong enough to promote

## Inputs

Revised labels backbone:
- `data/labels/v1/labels_master_boundary_revised_v1.parquet`

Frozen split registry:
- `data/metadata/splits/split_registry_v1.csv`

Regenerated IRR boundary benchmark:
- `data/validation/irr_boundary_benchmark_v1.csv`

Baseline binary model:
- `artifacts/models/binary_relevance_then_as_v1/metadata.json`

Retrained binary candidate:
- `artifacts/models/binary_relevance_then_as_boundary_v2/metadata.json`

Benchmark outputs:
- `reports/evaluation/model_benchmark_matrix_boundary_baseline_v1.json`
- `reports/evaluation/model_benchmark_matrix_boundary_candidate_v1.json`

## Important constraint

The frozen `held_out_v2` CSV is still missing:
- `data/validation/held_out_sentences_v2.csv`

So this experiment is valid as a revised-surface secondary benchmark only.

It is not a fresh publication-grade held-out rerun.

## Secondary benchmark surfaces

1. revised frozen validation split derived from `split_registry_v1`
2. regenerated IRR boundary benchmark from `adjudication.parquet`

## Result

The retrained binary candidate underperformed the existing binary baseline on
both secondary surfaces.

### Binary baseline: `binary_relevance_then_as_v1`

IRR boundary benchmark:
- accuracy: `0.7917`
- macro F1: `0.7841`
- binary relevance accuracy: `0.8833`
- conditional A/S accuracy: `0.8286`

Frozen validation split:
- accuracy: `0.7838`
- macro F1: `0.6521`
- binary relevance accuracy: `0.8919`
- conditional A/S accuracy: `0.6905`

### Retrained candidate: `binary_relevance_then_as_boundary_v2`

IRR boundary benchmark:
- accuracy: `0.7833`
- macro F1: `0.7754`
- binary relevance accuracy: `0.8833`
- conditional A/S accuracy: `0.8143`

Frozen validation split:
- accuracy: `0.7748`
- macro F1: `0.6346`
- binary relevance accuracy: `0.9009`
- conditional A/S accuracy: `0.6429`

### Candidate minus baseline

IRR boundary benchmark:
- accuracy: `-0.0083`
- macro F1: `-0.0087`
- binary relevance accuracy: `0.0000`
- conditional A/S accuracy: `-0.0143`

Frozen validation split:
- accuracy: `-0.0090`
- macro F1: `-0.0175`
- binary relevance accuracy: `+0.0090`
- conditional A/S accuracy: `-0.0476`

## Interpretation

This tranche did not improve the live model.

What happened is coherent:
- the revised tranche slightly strengthened binary relevance behavior
- but it weakened the actionable/speculative head
- the A/S degradation is larger than any relevance gain

That means the current tranche is too small or too imbalanced to improve the
two-stage model by itself.

## Additional comparison

The multiclass logistic baseline remains competitive and, on the IRR boundary
benchmark, still looks stronger than the binary model:
- `mpnet_logreg_prelim_v1` IRR macro F1: `0.7972`
- `mpnet_logreg_prelim_v1` IRR conditional A/S accuracy: `0.8714`

So the current evidence does not support narrowing the search space to the
binary model alone.

## Decision

Do not promote `binary_relevance_then_as_boundary_v2`.

Keep `binary_relevance_then_as_v1` as the live local binary baseline.

## Next step

1. expand the revised-rubric training tranche with more reviewed A/S boundary
   rows
2. prefer train-split additions over more validation relabeling
3. rerun both:
   - the binary relevance then A/S candidate
   - the multiclass logreg candidate
4. restore or regenerate `held_out_v2` before claiming any final accuracy gain
