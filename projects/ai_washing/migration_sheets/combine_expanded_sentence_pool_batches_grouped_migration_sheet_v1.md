# Combine Expanded Sentence Pool Batches Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.combine_expanded_sentence_pool_batches`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/combine_expanded_sentence_pool_batches.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `combine_expanded_sentence_pool_batches`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused Iteration 2 regression bundle

## Caller Groups

### Group 1: Direct Validation Edge

- `tests/test_iteration2_parallel.py`
- `projects/ai_washing/tests/test_combine_expanded_sentence_pool_batches_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority is a bounded cumulative-output combiner for the member-owned
sentence-pool expansion lane. It does not open the broader active-window/backfill
lane.
