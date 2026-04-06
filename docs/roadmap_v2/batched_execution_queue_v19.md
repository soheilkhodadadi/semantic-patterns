# Batched Execution Queue V19

## Purpose

This queue starts after Queue V18 completed cleanly.

It closes the last active `ai_washing` labeling benchmark edge, then rotates
into the `director` validation and script-governance lane.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- choose the `ai_washing` opener from the remaining `active_migration_candidate`
  labeling surface in the triage registry
- use focused local gates rather than widening back into dormant classification
  or data surfaces

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.build_irr_boundary_benchmark`

Lane:
- `ai_washing`

Why next:
- last active labeling migration candidate from the triage registry
- closes the current IRR boundary benchmark publication edge
- leaves only wrappers or dormant surfaces in the root labeling lane

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_build_irr_boundary_benchmark_member.py`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `semantic_director.validation_assets`

Lane:
- `director`

Why next:
- validation asset registry becomes cleaner once the IRR boundary benchmark is
  canonical
- real test pressure already exists in the focused validation-asset regression
  bundle
- stays in the same validation/reporting governance lane as the queue closes

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_validation_assets.py`
- `tests/test_director_validation_assets.py`
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `semantic_director.script_inventory`

Lane:
- `director`

Why next:
- compact governance follow-on after validation asset registry
- focused, low-blast-radius package boundary with a strong existing root test
- helps make the repo transition more legible without mixing in the separate
  hygiene queue

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_script_inventory.py`
- `tests/test_director_script_inventory.py`
- `git diff --check`

Status:
- complete
