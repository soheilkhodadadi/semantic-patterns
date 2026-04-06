# Fresh Authority Comparison V20

## Purpose

Choose the Queue V17 opener from the active `ai_washing` data surfaces in the root-surface triage registry.

## Candidates compared

1. `ai_washing_member.data.build_expanded_sentence_pool`
2. `ai_washing_member.data.materialize_active_window_sentences`

## Candidate A: `ai_washing_member.data.build_expanded_sentence_pool`

Why it is attractive:
- it opens a clean active sentence-pool expansion lane from the triage registry
- it pairs naturally with `combine_expanded_sentence_pool_batches` and the sentence-pool QA/segmentation surfaces
- it has strong direct regression pressure in `tests/test_iteration2_parallel.py`
- its upstream dependencies are already canonical under `ai_washing_member.data`

Risk shape:
- medium
- one active `ai_washing` data lane
- clear direct caller pressure with bounded local artifacts

## Candidate B: `ai_washing_member.data.materialize_active_window_sentences`

Why it is attractive:
- it is a central active-window sentence-table authority with strong downstream importance
- it pairs naturally with `run_historical_backfill`
- it has coverage in `tests/test_preliminary_phase3.py` and `tests/test_restartable_jobs.py`

Risk shape:
- medium-high
- broader lane surface than the expansion opener
- better suited after the sentence-pool expansion lane is moved, when the queue can focus on active-window/backfill behavior directly

## Decision

Chosen Queue V17 opener:
- `ai_washing_member.data.build_expanded_sentence_pool`

## Why this wins now

It gives Queue V17 a cleaner data-lane shape:

1. `build_expanded_sentence_pool`
2. `combine_expanded_sentence_pool_batches`
3. `benchmark_segmentation_modes`

That opens the active sentence-pool expansion and QA lane without mixing it immediately with the broader active-window/backfill lane.
