# Batched Execution Queue V7

## Purpose

This queue starts after Queue V6 completed cleanly.

It keeps Protocol V2 as the migration spine while using the next current-stage
IRR workflow cluster in `ai_washing` before rotating into a small downstream
`director` package boundary cleanup.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle in `ai_washing` because the IRR workflow surfaces are current
  and tightly clustered
- rotate into `director` for the cycle close rather than stretching a third
  `ai_washing` authority into the same queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.prepare_irr_subset`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V6
- directly follows the newly canonical IRR audit workflow
- localized regression bundle with one obvious compatibility edge

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `tests/test_irr_phase2.py`
  - any direct member-local test coverage needed for the new authority

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_am_ai_washing_prepare_irr_subset_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 2

Authority:
- `ai_washing_member.labeling.adjudicate_irr_labels`

Lane:
- `ai_washing`

Why next:
- natural follow-on after `prepare_irr_subset`
- keeps the IRR handoff workflow in one member-owned lane
- same focused regression bundle can still cover the round

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate direct IRR workflow callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_an_ai_washing_adjudication_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `semantic_director.gates`

Lane:
- `director`

Why next:
- compact `director` boundary that closes the cycle cleanly
- prepares the future `executor` move without forcing it into this queue
- good fit for a package-boundary cleanup after two flagship-project rounds

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_core.py`
- package build smoke
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/migration_round_ao_director_gates_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with a smaller `director` runtime/control round

## Current recommendation

Next in Queue V7:

1. Batch 1 complete:
   - `ai_washing_member.labeling.prepare_irr_subset`
2. Batch 2 complete:
   - `ai_washing_member.labeling.adjudicate_irr_labels`
3. Batch 3 complete:
   - `semantic_director.gates`


Queue V7 is now complete.
