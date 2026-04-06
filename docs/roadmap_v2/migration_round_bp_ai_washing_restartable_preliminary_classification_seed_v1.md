# Migration Round BP: AI-Washing Restartable Preliminary Classification Seed V1

## Purpose

Seed the canonical member-owned restartable preliminary classification authority for Queue V16.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/classification/classify_active_window_preliminary_restartable.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/classification/classify_active_window_preliminary_restartable.py`

Direct caller moved:
- `tests/test_preliminary_classification_restartable.py`

New member-local test:
- `projects/ai_washing/tests/test_classify_active_window_preliminary_restartable_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/classify_active_window_preliminary_restartable_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_classify_active_window_preliminary_restartable_member.py`
- `tests/test_preliminary_classification_restartable.py`

Result:
- `2 passed`
