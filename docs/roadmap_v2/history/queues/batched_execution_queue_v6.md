# Batched Execution Queue V6

## Purpose

This queue starts after Queue V5 completed cleanly.

It keeps Protocol V2 as the migration spine while treating legacy/template
cleanup as a separate bounded queue rather than mixing it into authority moves.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle in `ai_washing` for balance after Queue V5 closed in `director`
- keep legacy/template cleanup scheduled separately

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.publish_rubric_freeze`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V5
- directly follows the split-freeze workflow that just moved
- has a localized regression surface with one obvious compatibility edge

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `tests/test_split_freeze_publishers.py`
  - any direct member-local test coverage needed for the new authority

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_publish_rubric_freeze_member.py`
- `tests/test_split_freeze_publishers.py`
- `tests/test_irr_phase2.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_aj_ai_washing_publish_rubric_freeze_seed_v1.md`

Fallback if pre-scan gets messy:
- rotate early to Batch 2

### Batch 2

Authority:
- `semantic_director.snapshot`

Lane:
- `director`

Why next:
- strongest clean lane rotation after the `ai_washing` opener
- high leverage in `cli` and the core snapshot/test bundle
- package boundary value is real even with Atlas-adjacent wiring

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
- complete via `docs/roadmap_v2/history/rounds/migration_round_ak_director_snapshot_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with a smaller `director` cost/runtime round

### Batch 3

Authority:
- `ai_washing_member.labeling.audit_sentence_integrity`

Lane:
- `ai_washing`

Why next:
- natural follow-on after `semantic_director.sensors` is now canonical
- bounded workflow utility with a direct regression bundle
- closes the cycle back in the flagship project lane

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate direct `ai_washing` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

Status:
- complete via `docs/roadmap_v2/history/rounds/migration_round_al_ai_washing_audit_sentence_integrity_seed_v1.md`

Fallback if pre-scan gets messy:
- replace with a smaller `ai_washing` labeling/reporting round


## Current recommendation

Next in Queue V6:

1. Batch 1 complete:
   - `ai_washing_member.labeling.publish_rubric_freeze`
2. Batch 2 complete:
   - `semantic_director.snapshot`
3. Batch 3 complete:
   - `ai_washing_member.labeling.audit_sentence_integrity`
