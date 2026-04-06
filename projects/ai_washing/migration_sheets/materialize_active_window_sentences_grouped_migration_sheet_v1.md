# Materialize Active Window Sentences Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.materialize_active_window_sentences`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `materialize_active_window_sentences`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused Phase 3 materialization regression bundle

## Caller Groups

### Group 1: Direct Validation Edge

- `tests/test_preliminary_phase3.py`
- `projects/ai_washing/tests/test_materialize_active_window_sentences_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority depends on already-canonical member data surfaces:
- `ai_washing_member.data.extract_sentence_table`
- `ai_washing_member.data.index_sec_filings`

That dependency shape is accepted for Queue V18.
