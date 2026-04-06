# Task Graph Grouped Migration Sheet V1

## Authority

- canonical authority: `semantic_director.task_graph`
- legacy compatibility shim:
  - `src/semantic_ai_washing/director/core/task_graph.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `task_graph`
- lane: `director`
- compatibility strategy: legacy shim retained
- validation gate: package tests + focused root `director` regressions + package build

## Caller Groups

### Group 1: Readiness Edge

- `src/semantic_ai_washing/director/core/readiness.py`

### Group 2: Planning and Optimization Edge

- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/optimizer.py`

### Group 3: Review Edge

- `src/semantic_ai_washing/director/core/review.py`

### Group 4: Direct Validation Edge

- `tests/test_director_roadmap_model.py`
- `packages/director/tests/test_task_graph.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- package build gate: complete
