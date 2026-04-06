# Render Grouped Migration Sheet V1

## Authority

- canonical authority: `semantic_director.render`
- legacy compatibility shim:
  - `src/semantic_ai_washing/director/core/render.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `render`
- lane: `director`
- compatibility strategy: legacy shim retained
- validation gate: package tests + focused root `director` regressions + package build

## Caller Groups

### Group 1: CLI Runtime Edge

- `src/semantic_ai_washing/director/cli.py`

### Group 2: Optimization Edge

- `src/semantic_ai_washing/director/core/optimizer.py`

### Group 3: Review and Reporting Edge

- `src/semantic_ai_washing/director/core/review.py`

### Group 4: Direct Validation Edge

- `tests/test_director_roadmap_model.py`
- `packages/director/tests/test_render.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- package build gate: pending in this round until validation completes
