# Migration Round X: Director Config Seed V1

## Scope

Batch 2 from the ordered execution queue.

Authority:

- `semantic_director.config`

Batch:

- seed the canonical package implementation
- retain the legacy shim
- migrate the planned direct caller family
- migrate the direct validation edge

## Changes

### Canonical Package Authority

- `packages/director/src/semantic_director/config.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/director/core/config.py`

### Direct Caller Migration

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`

### Package Test

- `packages/director/tests/test_config.py`

## Gate

Planned validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `packages/director` package tests
- `tests/test_director_cli.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
