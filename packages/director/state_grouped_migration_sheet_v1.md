# State Grouped Migration Sheet V1

## Authority

- canonical authority: `semantic_director.state`
- legacy compatibility shim:
  - `src/semantic_ai_washing/director/core/state.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `state`
- lane: `director`
- compatibility strategy: legacy shim retained
- validation gate: package tests + focused root `director` regressions + package build

## Caller Groups

### Group 1: CLI Edge

- `src/semantic_ai_washing/director/cli.py`

### Group 2: Direct Validation Edge

- `tests/test_director_core.py`
- `packages/director/tests/test_state.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- package build gate: complete
