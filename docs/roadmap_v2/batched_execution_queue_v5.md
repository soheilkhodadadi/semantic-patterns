# Batched Execution Queue V5

## Purpose

This queue starts after Queue V4 completed and after a quick audit confirmed
that the already-migrated authorities are active rather than template carry-forward.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle with a high-leverage `director` package boundary cleanup
- rotate into `ai_washing` for the next round
- close with a smaller `director` control-plane surface

## Immediate execution queue

### Batch 1

Authority:
- `semantic_director.sensors`

Lane:
- `director`

Why next:
- strongest fresh authority after the Queue V4 checkpoint
- removes a visible root dependency from `semantic_director.readiness`
- has a tight caller bundle in `executor`, `readiness`, and the sensor tests

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate:
  - `packages/director/src/semantic_director/readiness.py`
  - `src/semantic_ai_washing/director/core/executor.py`
  - `tests/test_director_sensors.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_sensors.py`
- `packages/director/tests/test_readiness.py`
- `tests/test_director_sensors.py`
- `tests/test_director_core.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_ag_director_sensors_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 2

### Batch 2

Authority:
- `ai_washing_member.labeling.freeze_split_registry`

Lane:
- `ai_washing`

Why next:
- strongest clean rotation after the `director` opener
- clearly current-stage and well covered by dedicated tests
- fits the held-out and labeling workflow cluster already active in the member lane

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `tests/test_split_freeze_publishers.py`
  - any direct workflow caller that stays inside the same lane boundary

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_split_freeze_publishers.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_ah_ai_washing_freeze_split_registry_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `semantic_director.playbooks`

Lane:
- `director`

Why next:
- clean control-plane follow-on after the lane rotation
- likely bounded to `cli`, `review`, and the playbook test bundle
- good fit for closing a three-round cycle

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_playbooks.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_ai_director_playbooks_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with a smaller `director` review/runtime round


## Current recommendation

Next in Queue V5:

1. Batch 1 complete:
   - `semantic_director.sensors`
2. Batch 2 complete:
   - `ai_washing_member.labeling.freeze_split_registry`
3. Batch 3 complete:
   - `semantic_director.playbooks`


Queue V5 is now complete.
