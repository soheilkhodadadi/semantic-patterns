# Migration Round AA: Director Branching Seed V1

## Scope

Batch 1 from Queue V2.

Authority:

- `semantic_director.branching`

Batch:

- seed the canonical package implementation
- retain the legacy shim
- migrate the direct production callers
- migrate the direct validation edge

## Changes

### Canonical Package Authority

- `packages/director/src/semantic_director/branching.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/director/core/branching.py`

### Direct Caller Migration

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/review.py`

### Package Test

- `packages/director/tests/test_branching.py`

## Gate

Completed validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `packages/director` package tests
- `tests/test_director_cli.py`
- `tests/test_director_review.py`
- package build smoke
- `git diff --check`

Validation result:

- passed cleanly
- no additional compatibility fix was required during the gate

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
