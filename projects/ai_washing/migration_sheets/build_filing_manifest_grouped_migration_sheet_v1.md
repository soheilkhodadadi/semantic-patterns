# Build Filing Manifest Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.build_filing_manifest`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/build_filing_manifest.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `build_filing_manifest`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused root `ai_washing` regressions

## Caller Groups

### Group 1: Data Expansion Edge

- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`

### Group 2: Direct Validation Edge

- `tests/test_sentence_table_pilot.py`
- `projects/ai_washing/tests/test_build_filing_manifest_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority still depends on:
- `semantic_ai_washing.labeling.ff12_mapping`

That dependency is accepted for this round and can become a later fresh-authority
candidate if the follow-on scan remains clean.
