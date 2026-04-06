# Batched Execution Queue V11

## Purpose

This queue starts after Queue V10 completed cleanly.

It keeps Protocol V2 as the migration spine while moving a coherent Phase 1 dataset-prep workflow in `ai_washing`.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- prefer one coherent active workflow when a shared regression bundle already exists
- use `tests/test_labeling_phase1.py` as the shared root gate for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.build_labeling_sample`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V10
- direct caller pressure is concentrated in one Phase 1 workflow test bundle
- naturally opens the downstream dedupe and QA steps

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_labeling_phase1.py`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `ai_washing_member.labeling.dedupe_labeled_sentences`

Lane:
- `ai_washing`

Why next:
- direct follow-on after sample building
- keeps the same dataset-prep workflow inside the member-owned lane
- same root regression bundle still applies

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_labeling_phase1.py`
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `ai_washing_member.labeling.qa_labeled_dataset`

Lane:
- `ai_washing`

Why next:
- closes the Phase 1 dataset-prep workflow in the same member-owned lane
- completes an end-to-end current-stage workflow family
- uses the same regression bundle without mixing in hygiene work

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_labeling_phase1.py`
- `git diff --check`

Status:
- complete

## Current recommendation

Next in Queue V11:

1. Batch 1 complete:
   - `ai_washing_member.labeling.build_labeling_sample`
2. Batch 2 complete:
   - `ai_washing_member.labeling.dedupe_labeled_sentences`
3. Batch 3 complete:
   - `ai_washing_member.labeling.qa_labeled_dataset`
