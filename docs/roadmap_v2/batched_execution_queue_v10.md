# Batched Execution Queue V10

## Purpose

This queue starts after Queue V9 completed cleanly.

It keeps Protocol V2 as the migration spine while moving one coherent labeling
workflow pair in `ai_washing` before rotating into the stronger downstream
`director` planning boundary.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle in `ai_washing` because the review-sheet workflow is the
  cleanest active follow-on after Queue V9
- keep the first two rounds in one labeling workflow family
- close the cycle in `director` with the planner authority
- keep the separate hygiene queue isolated

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.initialize_review_sheet`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V9
- direct caller pressure is concentrated in one workflow family
- naturally opens `merge_labeling_batches` as the adjacent follow-on round

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate direct workflow callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Status:
- complete

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 2

Authority:
- `ai_washing_member.labeling.merge_labeling_batches`

Lane:
- `ai_washing`

Why next:
- direct workflow follow-on after `initialize_review_sheet`
- keeps the labeling workflow in one member-owned lane
- same regression bundle can still cover the round

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate direct workflow callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Status:
- planned

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `semantic_director.planner`

Lane:
- `director`

Why next:
- strongest clean `director` rotation after the labeling workflow pair
- now sits downstream of canonical `cost`, `llm`, `roadmap_model`, and `task_graph`
- closes the cycle with a meaningful package-owned planning boundary move

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- planned

Fallback if pre-scan gets messy:
- replace with a smaller `director` planning/runtime round

## Current recommendation

Next in Queue V10:

1. Batch 1 complete:
   - `ai_washing_member.labeling.initialize_review_sheet`
2. Batch 2 planned:
   - `ai_washing_member.labeling.merge_labeling_batches`
3. Batch 3 planned:
   - `semantic_director.planner`
