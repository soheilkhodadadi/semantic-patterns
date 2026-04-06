# Batched Execution Queue V1

## Purpose

This is the first ordered execution queue for the restructure. It converts the
current migration evidence into a practical sequence we can execute without
re-deciding the whole roadmap every round.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- avoid mixed authority moves
- avoid mixing shared-package extraction and project-member extraction in one
  code batch
- rotate lanes before one lane dominates the whole restructure

## Queue structure

Each queued batch has:
- authority
- lane
- why it is next
- expected batch shape
- default gate
- fallback if the pre-scan gets messy

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.data.build_filing_manifest`

Lane:
- `ai_washing`

Why next:
- best remaining fresh authority in the project-member lane
- lane rotation is now desirable after three successful `director` rounds
- small enough to seed cleanly

Expected batch shape:
- seed canonical member-owned implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
  - `tests/test_sentence_table_pilot.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing` member test for the seeded authority
- `tests/test_sentence_table_pilot.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_w_ai_washing_build_filing_manifest_seed_v1.md`

Fallback if pre-scan gets messy:
- defer authority seed
- take one established-authority `ai_washing` cleanup batch instead

### Batch 2

Authority:
- `semantic_director.config`

Lane:
- `director`

Why next:
- strong direct caller pressure
- smaller and safer than `readiness`
- good follow-on after the recent `director` package wins
- next active batch after Batch 1

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/director/cli.py`
  - `src/semantic_ai_washing/director/core/review.py`
  - `tests/test_director_core.py`
  - `tests/test_director_roadmap_model.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director` package tests
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_x_director_config_seed_v1.md`

Fallback if pre-scan gets messy:
- take `readiness` only if its caller map remains cleaner

### Batch 3

Authority:
- `semantic_director.readiness`

Lane:
- `director`

Why next:
- high leverage
- now naturally downstream of canonical `task_graph`
- keeps the `director` package shape coherent
- next active batch after Batch 2

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate:
  - `src/semantic_ai_washing/director/core/optimizer.py`
  - `src/semantic_ai_washing/director/core/review.py`
  - `tests/test_director_roadmap_model.py`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director` package tests
- `tests/test_director_review.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_y_director_readiness_seed_v1.md`

Fallback if pre-scan gets messy:
- defer and move to `ai_washing` Batch 4 sooner

### Batch 4

Authority:
- `ai_washing` industry mapping surface

Provisional candidate:
- `semantic_ai_washing.labeling.ff12_mapping`

Lane:
- `ai_washing`

Why next:
- logical follow-on after `build_filing_manifest`
- would reduce a key root-owned dependency in the `ai_washing` data lane

Expected batch shape:
- requires a fresh pre-scan before execution
- do not auto-start without that pre-scan

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- relevant `ai_washing` member tests
- likely:
  - `tests/test_sentence_table_pilot.py`
  - `tests/test_labeling_phase1.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_z_ai_washing_ff12_mapping_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with an established-authority `ai_washing` cleanup batch under the
  newly-seeded `build_filing_manifest` authority

## Second-tier backlog

These are good candidates, but not first in line:

### `director.branching`
- promising
- meaningful control-plane surface
- likely better after `config`

### `director.snapshot` and `director.state`
- good package candidates
- likely best after `config` and `readiness`

### `ai_washing` member packaging seed
- important
- should wait until one more or two more member-owned authorities are stable

## Operating rhythm

Use this queue in cycles:

1. execute the next batch
2. execute the next batch
3. execute the next batch
4. checkpoint

Do not let the queue become rigid.
If a pre-scan shows that the next batch is messier than expected:
- skip to the fallback
- record why
- keep the cycle moving

## Current recommendation

Current queue state:

1. Batches 1-4 complete
2. current queue exhausted
3. next step is a fresh queue reset, not an automatic Batch 5 carryover

Next execution move:

1. run a fresh authority comparison for the next cycle
2. build `batched_execution_queue_v2.md`
3. auto-run the next batch only after that queue reset stays clean
