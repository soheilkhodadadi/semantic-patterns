# Migration Round CS

## Queue

Queue V26

## Batch

`semantic_director.runtime_wrapper_normalization`

## Purpose

Move the director-facing command-execution wrapper from the root compatibility
shim into a package-owned module without changing its timeout wording contract.

## Expected surfaces

Canonical package target:
- `semantic_director.runtime`

Compatibility shim update:
- `src/semantic_ai_washing/director/core/utils.py`

## Gate

Required gate:
- targeted Ruff
- targeted `py_compile`
- focused package and root runtime/gates tests
- `git diff --check`

## Outcome

Completed cleanly.

Validated with:
- targeted Ruff on changed package module, root shim, package test, and queue docs
- `python -m py_compile` on changed package module and root shim
- focused pytest bundle
  - `packages/director/tests/test_runtime.py`
  - `packages/director/tests/test_gates.py`
  - `tests/test_labcore_runtime.py`
  - `tests/test_director_core.py`
- result: `22 passed`
