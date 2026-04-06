# Batched Execution Queue V17

## Purpose

This queue starts after Queue V16 completed cleanly.

It rotates into the active `ai_washing` data lane by moving the sentence-pool expansion and QA workflow inside the member-owned surface.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose Queue V17 authorities only from `active_migration_candidate` data surfaces in the triage registry
- use `tests/test_iteration2_parallel.py` as the shared root gate for this queue where possible

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.data.build_expanded_sentence_pool`

Lane:
- `ai_washing`

Why next:
- strongest clean opener from the remaining active data surfaces
- opens the sentence-pool expansion lane with strong direct caller pressure
- reuses the existing Iteration 2 sentence-pool regression bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_build_expanded_sentence_pool_member.py`
- `tests/test_iteration2_parallel.py -k "build_expanded_sentence_pool"`
- `git diff --check`

Status:
- planned

### Batch 2

Authority:
- `ai_washing_member.data.combine_expanded_sentence_pool_batches`

Lane:
- `ai_washing`

Why next:
- direct follow-on after expansion batch generation in the same sentence-pool workflow
- shares the same Iteration 2 regression bundle
- keeps Queue V17 inside one coherent expansion/output-combination lane

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_combine_expanded_sentence_pool_batches_member.py`
- `tests/test_iteration2_parallel.py -k "combine_expanded_sentence_pool_batches"`
- `git diff --check`

Status:
- planned

### Batch 3

Authority:
- `ai_washing_member.data.benchmark_segmentation_modes`

Lane:
- `ai_washing`

Why next:
- closes the sentence-pool data queue with a bounded QA/segmentation authority tied to the same extraction family
- keeps Queue V17 in one data lane instead of widening to active-window backfill immediately
- leaves the broader materialization/backfill lane for Queue V18

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_segmentation_modes_member.py`
- `git diff --check`

Status:
- planned

## Queue status

Queue V17 is in progress:

1. Batch 1:
   - `ai_washing_member.data.build_expanded_sentence_pool`
2. Batch 2:
   - `ai_washing_member.data.combine_expanded_sentence_pool_batches`
3. Batch 3:
   - `ai_washing_member.data.benchmark_segmentation_modes`
