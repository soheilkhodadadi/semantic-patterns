# Migration Round BU: AI-Washing Run Historical Backfill Seed V1

## Purpose

Seed the canonical member-owned historical backfill authority for Queue V18.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/run_historical_backfill.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/run_historical_backfill.py`

Direct caller moved:
- `tests/test_restartable_jobs.py`

New member-local test:
- `projects/ai_washing/tests/test_run_historical_backfill_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/run_historical_backfill_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_run_historical_backfill_member.py`
- `tests/test_restartable_jobs.py -k "run_backfill"`

Result:
- `3 passed, 1 deselected`
