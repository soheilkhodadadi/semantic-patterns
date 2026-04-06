# Migration Round CI

## Queue

Queue V23

## Batch

`hygiene.script_inventory_deprecation_rules`

## Purpose

Update the package-owned script inventory generator so six historical data
utilities are no longer treated as current canonical front-door entrypoints.

## Surfaces updated

Source-of-truth generator:
- `packages/director/src/semantic_director/script_inventory.py`

Focused tests:
- `tests/test_director_script_inventory.py`
- `packages/director/tests/test_script_inventory.py`

## Result

The generator now classifies these six modules as transitional script
deprecation candidates instead of canonical current implementations:
- `semantic_ai_washing.data.clean_compustat`
- `semantic_ai_washing.data.clean_crsp`
- `semantic_ai_washing.data.clean_sec`
- `semantic_ai_washing.data.download_compustat`
- `semantic_ai_washing.data.download_crsp`
- `semantic_ai_washing.data.download_sec`

## Gate

Required gate:
- targeted Ruff
- targeted `py_compile`
- focused script-inventory tests
- `git diff --check`
