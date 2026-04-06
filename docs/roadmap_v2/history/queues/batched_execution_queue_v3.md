# Batched Execution Queue V3

## Naming note

This file is the canonical Queue V3 record for the three-round cycle executed
in commits `6cfb7fe`, `205f010`, and `c6791cf`.

An earlier working draft was temporarily tracked as
`batched_execution_queue_v2.md` during execution. Keep this file as the
authoritative reference for that cycle.

## Purpose

This queue resets execution after the first cycle completed through Batch 4.

It keeps Protocol V2 as the per-round safety spine while using the newest
evidence about:

- lane health
- package maturity
- where the next leverage is strongest

## Planning assumptions

- keep Protocol V2 as the per-round gate
- keep one authority and one lane per code batch
- allow one stronger lane to take two fresh-authority rounds per cycle
- rotate back to the flagship `ai_washing` lane by Batch 3

## Immediate execution queue

### Batch 1

Authority:
- `semantic_director.branching`

Lane:
- `director`

Why next:
- strongest clean fresh authority after Queue V1 closed
- direct runtime leverage in `cli` and `review`
- low dependency complexity

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/director/cli.py`
  - `src/semantic_ai_washing/director/core/review.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director` package tests
- `tests/test_director_cli.py`
- `tests/test_director_review.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_aa_director_branching_seed_v1.md`

Fallback if pre-scan gets messy:
- defer to `semantic_director.state`

### Batch 2

Authority:
- `semantic_director.state`

Lane:
- `director`

Why next:
- still inside the stronger lane
- direct runtime leverage in `cli`
- cleaner than `snapshot`, which touches Atlas adapters

Expected batch shape:
- requires a fresh pre-scan before execution
- do not auto-start without that pre-scan

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director` package tests
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_ab_director_state_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `ai_washing_member.labeling.build_labeling_batch`

Lane:
- `ai_washing`

Why next:
- strongest reasonable lane-rotation authority after the two `director` rounds
- meaningful flagship member-owned surface
- validation story already exists

Expected batch shape:
- requires a fresh pre-scan before execution
- do not auto-start without that pre-scan

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing` member tests
- `tests/test_labeling_batch.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_ac_ai_washing_build_labeling_batch_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with an established-authority `ai_washing` cleanup batch

## Current recommendation

Start here:

1. Batches 1-3 complete:
   - `semantic_director.branching`
   - `semantic_director.state`
   - `ai_washing_member.labeling.build_labeling_batch`
2. Queue V3 exhausted
3. next step is a fresh queue reset, not an automatic Batch 4 carryover
