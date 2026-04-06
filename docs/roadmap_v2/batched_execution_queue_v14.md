# Batched Execution Queue V14

## Purpose

This queue starts after the documentation/navigation consolidation pass.

It uses the new root-surface triage registry to open the next clean active `ai_washing` workflow lane instead of selecting batches ad hoc.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose Queue V14 authorities only from `active_migration_candidate` surfaces in the triage registry
- use the preliminary classification regression bundles as the shared root gate for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.classification.train_preliminary_centroids`

Lane:
- `ai_washing`

Why next:
- strongest clean opener from the triage registry after the consolidation pass
- upstream training authority for the current preliminary classification chain
- direct caller pressure already exists in the phase-3 and benchmarking tests

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_train_preliminary_centroids_member.py`
- `tests/test_preliminary_benchmarking.py -k "train_wave1_models_hash_backend"`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `ai_washing_member.classification.classify_active_window_preliminary`

Lane:
- `ai_washing`

Why next:
- direct follow-on after centroid training in the same preliminary chain
- feeds restartable and reconciliation callers already present in the root lane
- shares the same phase-3 regression bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_classify_active_window_preliminary_member.py`
- `tests/test_preliminary_phase3.py -k "preliminary_training_eval_classification"`
- `tests/test_preliminary_classification_restartable.py`
- `git diff --check`

Status:
- planned

### Batch 3

Authority:
- `ai_washing_member.classification.evaluate_preliminary_heldout`

Lane:
- `ai_washing`

Why next:
- closes the centroid baseline chain with the held-out evaluation authority
- keeps Queue V14 inside one coherent preliminary-classification lane
- reuses the same phase-3 root gate instead of opening a broader benchmark matrix in the same queue

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_evaluate_preliminary_heldout_member.py`
- `tests/test_preliminary_phase3.py -k "preliminary_training_eval_classification"`
- `git diff --check`

Status:
- planned

## Queue status

Queue V14 is in progress:

1. Batch 1:
   - `ai_washing_member.classification.train_preliminary_centroids`
2. Batch 2:
   - `ai_washing_member.classification.classify_active_window_preliminary`
3. Batch 3:
   - `ai_washing_member.classification.evaluate_preliminary_heldout`
