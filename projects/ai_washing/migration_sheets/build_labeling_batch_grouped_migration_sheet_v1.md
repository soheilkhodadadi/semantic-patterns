# Build Labeling Batch Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.labeling.build_labeling_batch`
- legacy compatibility shim:
  - `src/semantic_ai_washing/labeling/build_labeling_batch.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `build_labeling_batch`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused root `ai_washing` regressions

## Caller Groups

### Group 1: Root Test Edge

- `tests/test_labeling_batch.py`
- `tests/test_iteration2_parallel.py`

### Group 2: Direct Validation Edge

- `projects/ai_washing/tests/test_build_labeling_batch_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete
