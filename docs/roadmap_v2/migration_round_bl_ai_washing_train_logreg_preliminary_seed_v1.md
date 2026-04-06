# Migration Round BL: AI-Washing Train Logreg Preliminary Seed V1

## Purpose

Seed the canonical member-owned wave-1 logreg training authority for Queue V15.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/classification/train_logreg_preliminary.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/classification/train_logreg_preliminary.py`

Direct caller moved:
- `tests/test_preliminary_benchmarking.py`

New member-local test:
- `projects/ai_washing/tests/test_train_logreg_preliminary_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/train_logreg_preliminary_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_train_logreg_preliminary_member.py`
- `tests/test_preliminary_benchmarking.py -k "train_wave1_models_hash_backend"`

Result:
- `1 passed, 3 deselected`
