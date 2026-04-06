# Migration Round AB: Director State Seed V1

## Scope

Batch 2 from Queue V3.

Authority:

- `semantic_director.state`

Batch:

- pre-scan the queued authority
- seed the canonical package implementation
- retain the legacy shim
- migrate the runtime caller
- migrate the direct validation edge

## Pre-Scan Result

The `state` boundary stayed clean enough to auto-run under Queue V3.

What made it clean:

- no Atlas adapter dependency
- direct runtime leverage in `cli`
- simple dependency shape through `semantic_labcore.runtime`
- clear focused validation edge in `tests/test_director_core.py`

## Changes

### Canonical Package Authority

- `packages/director/src/semantic_director/state.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/director/core/state.py`

### Direct Caller Migration

- `src/semantic_ai_washing/director/cli.py`

### Direct Validation Edge

- `tests/test_director_core.py`
- `packages/director/tests/test_state.py`

## Gate

Completed validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `packages/director` package tests
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Validation result:

- passed cleanly
- no additional compatibility fix was required during the gate

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
