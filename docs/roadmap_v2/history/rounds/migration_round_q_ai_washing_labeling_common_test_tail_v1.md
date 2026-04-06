# Migration Round Q: AI-Washing Labeling Common Test Tail V1

## Purpose

This round applies the V2 fast-safe protocol to the remaining direct test
callers that were still importing the legacy `semantic_ai_washing.labeling.common`
shim even though the member-owned authority was already established.

## Authority in force

Canonical member-owned authority remains:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`

Legacy compatibility remains available at:
- `src/semantic_ai_washing/labeling/common.py`

No new authority move was required in this round.

## Caller families migrated in this round

### Family A: phase-1 labeling tests
- `tests/test_labeling_phase1.py`

### Family B: labeling batch tests
- `tests/test_labeling_batch.py`

### Family C: table fallback tests
- `tests/test_load_table_fallback.py`

## Validation gate

Passed:
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `tests/test_labeling_phase1.py`
  - `tests/test_labeling_batch.py`
  - `tests/test_load_table_fallback.py`
  - `projects/ai_washing/tests/test_labeling_common_member.py`
- result: `18 passed`
- `git diff --check`

## Outcome

This round confirms that Protocol V2 is useful not only for new authority
seeding, but also for cleanup work under an already-established member-owned
surface.

It also deliberately avoids inventing a fake fourth family. The clean next move
here was three direct test families plus continued compatibility coverage.

## Spillover check

No Atlas- or NDA-derived code or structure entered this batch.
