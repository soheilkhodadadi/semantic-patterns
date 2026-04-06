# Batched Execution Queue V8

## Purpose

This queue starts after Queue V7 completed cleanly.

It keeps Protocol V2 as the migration spine while continuing the current-stage
IRR reporting workflow in `ai_washing` before rotating into a higher-leverage
`director` package boundary cleanup.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle in `ai_washing` because the IRR reporting surfaces are now the
  cleanest current-stage follow-on
- close the cycle in `director` so lane balance stays healthy

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.compute_irr_metrics`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V7
- directly follows the subset and adjudication authorities that just moved
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
- complete

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 2

Authority:
- `ai_washing_member.labeling.diagnose_irr_disagreements`

Lane:
- `ai_washing`

Why next:
- natural follow-on after `compute_irr_metrics`
- keeps the IRR reporting workflow in one member-owned lane
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
- planned

Fallback if pre-scan gets messy:
- rotate early to Batch 3

### Batch 3

Authority:
- `semantic_director.executor`

Lane:
- `director`

Why next:
- strongest clean `director` rotation after the IRR reporting pair
- now sits downstream of canonical `decision`, `gates`, and `sensors`
- good fit for closing a three-round cycle with a meaningful package boundary move

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- planned

Fallback if pre-scan gets messy:
- replace with a smaller `director` control/runtime round

## Current recommendation

Next in Queue V8:

1. Batch 1 complete:
   - `ai_washing_member.labeling.compute_irr_metrics`
2. Batch 2 planned:
   - `ai_washing_member.labeling.diagnose_irr_disagreements`
3. Batch 3 planned:
   - `semantic_director.executor`
