# Roadmap Model Grouped Migration Sheet V1

## Authority

- canonical authority: `semantic_director.roadmap_model`
- legacy compatibility shim:
  - `src/semantic_ai_washing/director/core/roadmap_model.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `roadmap_model`
- lane: `director`
- compatibility strategy: legacy shim retained
- validation gate: package tests + focused root `director` regressions

## Caller Groups

### Group 1: Runtime Entrypoints

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/adapters/documents.py`

### Group 2: Planning and Graph

- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/task_graph.py`

### Group 3: Review and Optimization

- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/review.py`

### Group 4: Direct Validation Edge

- `tests/test_director_roadmap_model.py`
- `packages/director/tests/test_roadmap_model.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- package build gate: pending in this round until validation completes
