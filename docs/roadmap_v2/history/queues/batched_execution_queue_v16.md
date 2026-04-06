# Batched Execution Queue V16

## Purpose

This queue starts after Queue V15 completed cleanly.

It uses the triage registry to close the remaining active preliminary classification reporting lane inside the member-owned `ai_washing` surface before rotating into data.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose the Queue V16 opener from `active_migration_candidate` surfaces in the triage registry
- use the preliminary benchmarking and restartable bundles as the shared root gates for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.classification.publish_selected_preliminary_eval`

Lane:
- `ai_washing`

Why next:
- strongest clean opener from the remaining active preliminary classification surfaces
- direct downstream follow-on after the now-member-owned benchmark matrix authority
- direct caller pressure already exists in the preliminary benchmarking bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_publish_selected_preliminary_eval_member.py`
- `tests/test_preliminary_benchmarking.py -k "run_benchmark_selects_winner"`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `ai_washing_member.classification.reconcile_preliminary_classification_report`

Lane:
- `ai_washing`

Why next:
- direct follow-on after selected-model publish in the same preliminary reporting lane
- keeps the reporting and classification-output reconciliation path together before wrapper closeout
- can be validated with a focused member smoke test without widening the queue

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_reconcile_preliminary_classification_report_member.py`
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `ai_washing_member.classification.classify_active_window_preliminary_restartable`

Lane:
- `ai_washing`

Why next:
- closes the remaining wrapper/rerun edge of the same preliminary classification lane
- reuses the existing restartable gate instead of opening the data lane in the same queue
- leaves Queue V16 as one coherent closeout of active preliminary classification work

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_classify_active_window_preliminary_restartable_member.py`
- `tests/test_preliminary_classification_restartable.py`
- `git diff --check`

Status:
- complete

## Queue status

Queue V16 is complete:

1. Batch 1:
   - `ai_washing_member.classification.publish_selected_preliminary_eval`
2. Batch 2:
   - `ai_washing_member.classification.reconcile_preliminary_classification_report`
3. Batch 3:
   - `ai_washing_member.classification.classify_active_window_preliminary_restartable`


Recommended next move:
- start Queue V17 with a fresh-authority comparison
