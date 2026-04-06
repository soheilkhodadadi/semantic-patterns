# Branching Grouped Migration Sheet V1

## Authority

- canonical authority: `semantic_director.branching`
- legacy compatibility shim:
  - `src/semantic_ai_washing/director/core/branching.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `branching`
- lane: `director`
- compatibility strategy: legacy shim retained
- validation gate: package tests + focused root `director` regressions + package build

## Caller Groups

### Group 1: CLI Edge

- `src/semantic_ai_washing/director/cli.py`

### Group 2: Review Edge

- `src/semantic_ai_washing/director/core/review.py`

### Group 3: Direct Validation Edge

- `packages/director/tests/test_branching.py`
- `tests/test_director_cli.py`
- `tests/test_director_review.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- package build gate: complete
