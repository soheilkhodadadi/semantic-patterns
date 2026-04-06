# Migration Round CL

## Queue

Queue V24

## Batch

`hygiene.script_consumer_deprecation_rules`

## Purpose

Update the package-owned script inventory generator so the flat `src/data/*`
shims for six historical data utilities are treated as explicit deprecation
consumers instead of generic transitional shims.

## Surfaces updated

Source-of-truth generator:
- `packages/director/src/semantic_director/script_inventory.py`

Focused tests:
- `tests/test_director_script_inventory.py`
- `packages/director/tests/test_script_inventory.py`

## Expected result

These six flat shim modules should remain transitional, but they should now
carry an explicit script-consumer deprecation posture:
- `data.clean_compustat`
- `data.clean_crsp`
- `data.clean_sec`
- `data.download_compustat`
- `data.download_crsp`
- `data.download_sec`

## Gate

Required gate:
- targeted Ruff
- targeted `py_compile`
- focused script-inventory tests
- `git diff --check`
