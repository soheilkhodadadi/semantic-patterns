# Migration Round BW: AI-Washing Build IRR Boundary Benchmark Seed V1

## Purpose

Seed the canonical member-owned IRR boundary benchmark authority for Queue V19.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/labeling/build_irr_boundary_benchmark.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/build_irr_boundary_benchmark.py`

New member-local test:
- `projects/ai_washing/tests/test_build_irr_boundary_benchmark_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/build_irr_boundary_benchmark_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_build_irr_boundary_benchmark_member.py`

Result:
- `1 passed`
