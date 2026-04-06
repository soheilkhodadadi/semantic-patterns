# Batched Execution Queue V15

## Purpose

This queue starts after Queue V14 completed cleanly.

It uses the triage registry to move the remaining wave-1 preliminary model-selection workflow inside the member-owned `ai_washing` lane.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose Queue V15 authorities only from `active_migration_candidate` surfaces in the triage registry
- use `tests/test_preliminary_benchmarking.py` as the shared root gate for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.classification.train_binary_relevance_then_as`

Lane:
- `ai_washing`

Why next:
- strongest clean opener from the remaining active classification surfaces
- upstream wave-1 training authority for the current benchmark matrix path
- direct caller pressure already exists in the shared preliminary benchmarking bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_train_binary_relevance_then_as_member.py`
- `tests/test_preliminary_benchmarking.py -k "train_wave1_models_hash_backend"`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `ai_washing_member.classification.train_logreg_preliminary`

Lane:
- `ai_washing`

Why next:
- direct follow-on after the binary training authority in the same wave-1 model-selection lane
- shares the same benchmarking test helper and root gate
- keeps Queue V15 upstream before the benchmark matrix authority moves

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_train_logreg_preliminary_member.py`
- `tests/test_preliminary_benchmarking.py -k "train_wave1_models_hash_backend"`
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `ai_washing_member.classification.benchmark_preliminary_models`

Lane:
- `ai_washing`

Why next:
- closes the wave-1 model-selection lane with the benchmark matrix authority
- reuses the same preliminary benchmarking root gate instead of opening publication/report reconciliation in the same queue
- leaves the downstream publication/report surfaces for a later follow-on queue

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_preliminary_models_member.py`
- `tests/test_preliminary_benchmarking.py`
- `git diff --check`

Status:
- planned

## Queue status

Queue V15 is in progress:

1. Batch 1:
   - `ai_washing_member.classification.train_binary_relevance_then_as`
2. Batch 2:
   - `ai_washing_member.classification.train_logreg_preliminary`
3. Batch 3:
   - `ai_washing_member.classification.benchmark_preliminary_models`
