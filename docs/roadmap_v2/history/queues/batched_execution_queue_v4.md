# Batched Execution Queue V4

## Purpose

This queue resets execution after Queue V3 completed cleanly.

It keeps Protocol V2 as the per-round safety spine while rebalancing toward
the flagship `ai_washing` lane before rotating back into `director`.

## Planning assumptions

- keep Protocol V2 as the per-round gate
- keep one authority and one lane per code batch
- start this cycle in `ai_washing` to restore lane balance
- use a coherent held-out workflow pair before rotating back to `director`

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.sample_heldout_v2_candidates`

Lane:
- `ai_washing`

Why next:
- strongest fresh authority after Queue V3 closed
- already leans on member-owned classification and labeling surfaces
- has one clean runtime caller in the restartable wrapper
- validation story is strong and localized

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/labeling/sample_heldout_v2_restartable.py`
  - `tests/test_heldout_v2_workflow.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing` member tests
- `tests/test_heldout_v2_workflow.py`
- `tests/test_restartable_jobs.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_ad_ai_washing_heldout_sampler_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to `semantic_director.decision`

### Batch 2

Authority:
- `ai_washing_member.labeling.freeze_heldout_v2`

Lane:
- `ai_washing`

Why next:
- coherent follow-on in the same held-out workflow lane
- same validation bundle can carry most of the risk
- keeps the cycle efficient before a lane rotation

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `tests/test_heldout_v2_workflow.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `tests/test_heldout_v2_workflow.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_ae_ai_washing_heldout_freeze_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `semantic_director.decision`

Lane:
- `director`

Why next:
- strongest clean lane rotation after the held-out workflow pair
- useful leverage in `cli` and `executor`
- prepares a future `executor`-oriented round

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/director/cli.py`
  - `src/semantic_ai_washing/director/core/executor.py`
  - `tests/test_director_core.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director` package tests
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_af_director_decision_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with a smaller `director` policy/runtime cleanup round

## Current recommendation

Start here:

1. Batch 1 complete:
   - `ai_washing_member.labeling.sample_heldout_v2_candidates`
2. Batch 2 complete:
   - `ai_washing_member.labeling.freeze_heldout_v2`
3. Batch 3 complete:
   - `semantic_director.decision`

Queue V4 is now complete.
