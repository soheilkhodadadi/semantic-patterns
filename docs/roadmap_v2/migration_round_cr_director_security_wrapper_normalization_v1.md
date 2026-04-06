# Migration Round CR

## Queue

Queue V26

## Batch

`semantic_director.security_wrapper_normalization`

## Purpose

Move the director-facing security contract from the root compatibility shim
into a package-owned module without changing its user-facing behavior.

## Expected surfaces

Canonical package target:
- `semantic_director.security`

Compatibility shim update:
- `src/semantic_ai_washing/director/core/security.py`

## Gate

Required gate:
- `make doctor`
- targeted Ruff
- targeted `py_compile`
- focused package and root security/cli tests
- `git diff --check`

## Outcome

Completed cleanly.

Validated with:
- `make doctor`
- targeted Ruff on changed package module, root shim, package test, and queue docs
- `python -m py_compile` on changed package module and root shim
- focused pytest bundle
  - `packages/director/tests/test_security.py`
  - `packages/director/tests/test_cli.py`
  - `tests/test_labcore_security.py`
  - `tests/test_director_core.py`
  - `tests/test_director_cli.py`
- result: `33 passed`
