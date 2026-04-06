# Migration Round BM: AI-Washing Benchmark Preliminary Models Seed V1

## Purpose

Seed the canonical member-owned wave-1 benchmark matrix authority for Queue V15.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/classification/benchmark_preliminary_models.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/classification/benchmark_preliminary_models.py`

Direct caller moved:
- `tests/test_preliminary_benchmarking.py`

New member-local test:
- `projects/ai_washing/tests/test_benchmark_preliminary_models_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/benchmark_preliminary_models_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_preliminary_models_member.py`
- `tests/test_preliminary_benchmarking.py`

Result:
- `4 passed, 16 warnings`

Notes:
- existing sklearn metric warnings still appear in this benchmark lane
- the focused gate passed cleanly despite those warnings
