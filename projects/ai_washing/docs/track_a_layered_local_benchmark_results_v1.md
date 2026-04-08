# Track A Layered Local Benchmark Results V1

## Purpose

Record the first composite local benchmark that combines:
- `binary_relevance_then_as_v1` for relevance gating
- `mpnet_logreg_prelim_v1` for `Actionable` / `Speculative` resolution

This is the first direct test of the layered local design on the rebuilt
`held_out_v3` benchmark.

## Inputs

- Primary benchmark:
  - `data/validation/held_out_v3/held_out_sentences_v3.csv`
- Secondary benchmarks:
  - `data/validation/irr_boundary_benchmark_v1.csv`
  - derived frozen validation split from:
    - `data/labels/v1/labels_master_boundary_revised_v1.parquet`
    - `data/metadata/splits/split_registry_v1.csv`
- Benchmark matrix:
  - `reports/evaluation/model_benchmark_matrix_heldout_v3_layered_v1.json`
  - `reports/evaluation/model_benchmark_matrix_heldout_v3_layered_v1.md`

## Candidate

Layered candidate:
- `layered_binary_relevance_logreg_as_v1`

Logic:
1. use the binary model's `Irrelevant` vs `Non-Irrelevant` probabilities
2. use the logreg model only to split `Actionable` vs `Speculative`
3. renormalize the logreg `Actionable` / `Speculative` mass within the
   `Non-Irrelevant` mass from the binary model

## Results

### `held_out_v3`

- `binary_relevance_then_as_v1`
  - accuracy: `0.6836`
  - macro F1: `0.6326`
  - binary relevance accuracy: `0.7853`
  - conditional A/S accuracy: `0.7556`
- `mpnet_logreg_prelim_v1`
  - accuracy: `0.6667`
  - macro F1: `0.6224`
  - binary relevance accuracy: `0.7684`
  - conditional A/S accuracy: `0.7667`
- `layered_binary_relevance_logreg_as_v1`
  - accuracy: `0.6893`
  - macro F1: `0.6371`
  - binary relevance accuracy: `0.7853`
  - conditional A/S accuracy: `0.7778`

### `irr_boundary_benchmark`

- `binary_relevance_then_as_v1`
  - accuracy: `0.7917`
  - macro F1: `0.7841`
  - conditional A/S accuracy: `0.8286`
- `mpnet_logreg_prelim_v1`
  - accuracy: `0.8000`
  - macro F1: `0.7972`
  - conditional A/S accuracy: `0.8714`
- `layered_binary_relevance_logreg_as_v1`
  - accuracy: `0.8083`
  - macro F1: `0.8043`
  - conditional A/S accuracy: `0.8714`

### `frozen_validation_split`

- `binary_relevance_then_as_v1`
  - accuracy: `0.7838`
  - macro F1: `0.6521`
- `mpnet_logreg_prelim_v1`
  - accuracy: `0.7658`
  - macro F1: `0.6689`
- `layered_binary_relevance_logreg_as_v1`
  - accuracy: `0.7658`
  - macro F1: `0.6476`

## Interpretation

The layered local design is directionally correct.

It improves the primary `held_out_v3` benchmark relative to the current binary
baseline:
- accuracy: `+0.0056`
- macro F1: `+0.0045`
- conditional A/S accuracy: `+0.0222`

It is also the strongest candidate on the IRR boundary benchmark.

But it still fails the minimum primary gate:
- required accuracy: `0.70`
- achieved accuracy: `0.6893`
- required macro F1: `0.65`
- achieved macro F1: `0.6371`

So this is not yet promotion-ready as a pure local winner.

## Decision

Do not promote the layered local candidate as the final publication model yet.

Use this result as evidence that:
1. the layered architecture is better than any single current local model
2. the remaining gap is small enough that a selective-defer layer is now the
   most defensible next intervention

## Next step

Proceed to offline selective-defer simulation using:
- the layered local candidate as the base local model
- the reviewed `held_out_v3` benchmark as the evaluation surface
- the assistive API labels as the first automated escalation signal
