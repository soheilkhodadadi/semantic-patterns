# Migration Round Y: Director Readiness Seed V1

## Scope

Batch 3 from the ordered execution queue.

Authority:

- `semantic_director.readiness`

Batch:

- seed the canonical package implementation
- retain the legacy shim
- migrate the planned direct caller family
- migrate the direct validation edge

## Changes

### Canonical Package Authority

- `packages/director/src/semantic_director/readiness.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/director/core/readiness.py`

### Direct Caller Migration

- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_roadmap_model.py`

### Package Test

- `packages/director/tests/test_readiness.py`

## Gate

Completed validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `packages/director` package tests
- `tests/test_director_review.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

Validation result:

- passed after one contained import-loop fix in
  `src/semantic_ai_washing/director/__init__.py`
- the fix narrowed the compatibility export surface to
  `semantic_director.schemas`, which removed a circular import during
  `semantic_director` package import

## Known Dependency Note

This authority still depends on:
- `semantic_ai_washing.director.core.sensors`

That dependency is accepted for this round and should be revisited in a later
fresh-authority comparison.

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
