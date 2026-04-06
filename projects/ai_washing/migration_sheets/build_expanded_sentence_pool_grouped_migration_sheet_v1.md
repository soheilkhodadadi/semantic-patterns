# Build Expanded Sentence Pool Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.build_expanded_sentence_pool`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `build_expanded_sentence_pool`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused Iteration 2 regression bundle

## Caller Groups

### Group 1: Direct Validation Edge

- `tests/test_iteration2_parallel.py`
- `projects/ai_washing/tests/test_build_expanded_sentence_pool_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority depends on already-canonical member data surfaces:
- `ai_washing_member.data.build_filing_manifest`
- `ai_washing_member.data.extract_sentence_table`
- `ai_washing_member.data.index_sec_filings`

That dependency shape is accepted for Queue V17.
