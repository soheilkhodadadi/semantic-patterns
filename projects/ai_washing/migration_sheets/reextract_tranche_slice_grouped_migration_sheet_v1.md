# Reextract Tranche Slice Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.reextract_tranche_slice`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/reextract_tranche_slice.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `reextract_tranche_slice`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused sentence-table pilot regression bundle

## Caller Groups

### Group 1: Direct Validation Edge

- `tests/test_sentence_table_pilot.py`
- `projects/ai_washing/tests/test_reextract_tranche_slice_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority stays intentionally narrow:
- it rebuilds tranche calibration rows directly from raw SEC filings
- it does not open any dormant acquisition or template data utilities
