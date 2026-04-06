# Migration Round BN: AI-Washing Publish Selected Preliminary Eval Seed V1

## Purpose

Seed the canonical member-owned selected-model publication authority for Queue V16.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/classification/publish_selected_preliminary_eval.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/classification/publish_selected_preliminary_eval.py`

Direct caller moved:
- `tests/test_preliminary_benchmarking.py`

New member-local test:
- `projects/ai_washing/tests/test_publish_selected_preliminary_eval_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/publish_selected_preliminary_eval_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_publish_selected_preliminary_eval_member.py`
- `tests/test_preliminary_benchmarking.py -k "run_benchmark_selects_winner or publish_selected_preliminary_eval"`

Result:
- `2 passed, 2 deselected`
