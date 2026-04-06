# Run Historical Backfill Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.run_historical_backfill`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/run_historical_backfill.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `run_historical_backfill`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused restartable-jobs regression bundle

## Caller Groups

### Group 1: Direct Validation Edge

- `tests/test_restartable_jobs.py`
- `projects/ai_washing/tests/test_run_historical_backfill_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority now depends on the canonical member-owned active-window materialization surface:
- `ai_washing_member.data.materialize_active_window_sentences`

That dependency order is accepted for Queue V18.
