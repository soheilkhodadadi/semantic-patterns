# Batched Execution Queue V18

## Purpose

This queue starts after Queue V17 completed cleanly.

It rotates deeper into the active `ai_washing` data lane by moving active-window materialization, historical backfill orchestration, and tranche recalibration into the member-owned surface.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose Queue V18 authorities only from the remaining `active_migration_candidate` data surfaces in the triage registry
- use `tests/test_preliminary_phase3.py`, `tests/test_restartable_jobs.py`, and `tests/test_sentence_table_pilot.py` as the shared root gates for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.data.materialize_active_window_sentences`

Lane:
- `ai_washing`

Why next:
- strongest clean opener from the remaining active data surfaces
- upstream authority for the remaining active-window/backfill lane
- reuses the existing Phase 3 materialization regression bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_materialize_active_window_sentences_member.py`
- `tests/test_preliminary_phase3.py -k "materialize_active_window_sentences"`
- `git diff --check`

Status:
- planned

### Batch 2

Authority:
- `ai_washing_member.data.run_historical_backfill`

Lane:
- `ai_washing`

Why next:
- direct orchestration follow-on after canonical materialization
- shares the same active-window and restartable data lane
- keeps Queue V18 inside one historical indexing/materialization workflow

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_run_historical_backfill_member.py`
- `tests/test_restartable_jobs.py -k "run_backfill"`
- `git diff --check`

Status:
- planned

### Batch 3

Authority:
- `ai_washing_member.data.reextract_tranche_slice`

Lane:
- `ai_washing`

Why next:
- closes the queue with the remaining active tranche recalibration data surface
- stays in the same raw-filing extraction and cleanup lane without widening into dormant utilities
- leaves only dormant/template data surfaces for later hygiene or lower-priority migration work

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_reextract_tranche_slice_member.py`
- `tests/test_sentence_table_pilot.py -k "reextract_tranche_slice"`
- `git diff --check`

Status:
- planned

## Queue status

Queue V18 is in progress:

1. Batch 1:
   - `ai_washing_member.data.materialize_active_window_sentences`
2. Batch 2:
   - `ai_washing_member.data.run_historical_backfill`
3. Batch 3:
   - `ai_washing_member.data.reextract_tranche_slice`
