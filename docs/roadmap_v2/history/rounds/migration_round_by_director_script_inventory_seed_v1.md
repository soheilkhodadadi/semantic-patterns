# Migration Round BY: Director Script Inventory Seed V1

## Scope

Batch 3 from Queue V19.

Authority:
- `semantic_director.script_inventory`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct script-inventory caller bundle onto the new authority

## Pre-Scan Result

The `script_inventory` boundary stayed clean enough to auto-run under Queue V19.

What made it clean:
- direct caller pressure is concentrated in the focused script-inventory test
  bundle
- the implementation is operational-governance focused and does not widen into
  the separate hygiene queue itself
- it closes Queue V19 with a compact package boundary after the validation-asset
  registry move

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_script_inventory.py`
- `tests/test_director_script_inventory.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/script_inventory.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/tasks/script_inventory.py`

Migrated callers:
- `tests/test_director_script_inventory.py`

New package-local test:
- `packages/director/tests/test_script_inventory.py`
