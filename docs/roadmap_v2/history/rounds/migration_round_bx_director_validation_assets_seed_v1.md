# Migration Round BX: Director Validation Assets Seed V1

## Scope

Batch 2 from Queue V19.

Authority:
- `semantic_director.validation_assets`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct validation-asset caller bundle onto the new authority

## Pre-Scan Result

The `validation_assets` boundary stayed clean enough to auto-run under Queue V19.

What made it clean:
- direct caller pressure is concentrated in the focused validation-asset test
  bundle
- the package value is real without forcing a wider control-runtime extraction
- the newly canonical IRR boundary benchmark surface makes the asset registry
  meaningfully cleaner than it was before Queue V19 began

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_validation_assets.py`
- `tests/test_director_validation_assets.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/validation_assets.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/tasks/validation_assets.py`

Migrated callers:
- `tests/test_director_validation_assets.py`

New package-local test:
- `packages/director/tests/test_validation_assets.py`
