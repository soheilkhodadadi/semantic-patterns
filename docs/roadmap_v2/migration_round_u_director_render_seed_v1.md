# Migration Round U: Director Render Seed V1

## Scope

Fresh-authority round under Protocol V2.

Authority:

- `semantic_director.render`

Batch:

- seed the canonical package implementation
- retain the legacy shim
- migrate the direct `director` caller family
- migrate the direct validation edge

## Changes

### Canonical Package Authority

- `packages/director/src/semantic_director/render.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/director/core/render.py`

### Direct Caller Migration

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_roadmap_model.py`

### Package Tests

- `packages/director/tests/test_render.py`

## Gate

Planned validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- package tests for `semantic_director`
- focused root `director` regressions
- package build smoke for `semantic-director`

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
