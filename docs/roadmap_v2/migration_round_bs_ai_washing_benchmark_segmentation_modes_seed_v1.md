# Migration Round BS: AI-Washing Benchmark Segmentation Modes Seed V1

## Purpose

Seed the canonical member-owned segmentation benchmark authority for Queue V17.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/benchmark_segmentation_modes.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/benchmark_segmentation_modes.py`

New member-local test:
- `projects/ai_washing/tests/test_benchmark_segmentation_modes_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/benchmark_segmentation_modes_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_segmentation_modes_member.py`

Result:
- `1 passed`
