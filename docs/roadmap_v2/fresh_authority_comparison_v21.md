# Fresh Authority Comparison V21

## Purpose

Choose the Queue V18 opener from the remaining active `ai_washing` data surfaces in the root-surface triage registry.

## Candidates compared

1. `ai_washing_member.data.materialize_active_window_sentences`
2. `ai_washing_member.data.run_historical_backfill`

## Candidate A: `ai_washing_member.data.materialize_active_window_sentences`

Why it is attractive:
- it is the upstream active-window sentence-table authority for the remaining live data lane
- it has strong direct regression pressure in `tests/test_preliminary_phase3.py`
- it is a cleaner opener because the backfill workflow depends on its materialization contract
- it keeps Queue V18 focused on canonical sentence-table generation before restartable orchestration

Risk shape:
- medium
- one active `ai_washing` data lane
- clear direct caller pressure with bounded yearly output reuse behavior

## Candidate B: `ai_washing_member.data.run_historical_backfill`

Why it is attractive:
- it is a meaningful restartable historical indexing and materialization workflow
- it has focused regression pressure in `tests/test_restartable_jobs.py`
- it would close a real long-running orchestration surface

Risk shape:
- medium-high
- depends directly on the materialization authority staying stable
- better suited after the active-window materialization boundary is canonical

## Decision

Chosen Queue V18 opener:
- `ai_washing_member.data.materialize_active_window_sentences`

## Why this wins now

It gives Queue V18 a cleaner data-lane shape:

1. `materialize_active_window_sentences`
2. `run_historical_backfill`
3. `reextract_tranche_slice`

That keeps the queue inside one active data lane while respecting dependency order:
- canonical materialization first
- historical orchestration second
- tranche recalibration third
