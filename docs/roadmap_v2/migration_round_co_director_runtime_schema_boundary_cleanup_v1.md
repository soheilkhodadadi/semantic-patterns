# Migration Round CO

## Queue

Queue V25

## Batch

`semantic_director.runtime_schema_boundary_cleanup`

## Purpose

Switch package-owned `director` modules from root compatibility imports to
direct canonical imports where the equivalents are already stable and exact.

## Expected surfaces

Canonical runtime helper target:
- `semantic_labcore.runtime`

Canonical schema target:
- `semantic_director.schemas`

## Gate

Required gate:
- `make doctor`
- targeted Ruff
- targeted `py_compile`
- focused package and root `director` tests
- `git diff --check`

## Outcome

Completed cleanly.

Validated with:
- `make doctor`
- targeted Ruff on changed package modules and queue docs
- `python -m py_compile` on changed package modules
- focused pytest bundle
  - `packages/director/tests/test_decision.py`
  - `packages/director/tests/test_documents.py`
  - `packages/director/tests/test_sensors.py`
  - `packages/director/tests/test_script_inventory.py`
  - `packages/director/tests/test_atlas.py`
  - `packages/director/tests/test_iteration_log.py`
  - `packages/director/tests/test_validation_assets.py`
  - `packages/director/tests/test_cli.py`
  - `tests/test_director_cli.py`
  - `tests/test_director_sensors.py`
  - `tests/test_director_script_inventory.py`
  - `tests/test_director_validation_assets.py`
- result: `32 passed`
