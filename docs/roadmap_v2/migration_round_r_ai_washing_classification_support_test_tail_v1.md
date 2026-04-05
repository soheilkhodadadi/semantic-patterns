# Migration Round R: AI-Washing Classification Support Test Tail V1

## Purpose

This round applies the V2 fast-safe protocol to the remaining direct root test
callers for the already-established member-owned classification support surface.

## Authority in force

Canonical member-owned authority remains:
- `projects/ai_washing/src/ai_washing_member/classification/preliminary_pipeline.py`
- `projects/ai_washing/src/ai_washing_member/classification/model_runtime.py`

Legacy compatibility remains available at:
- `src/semantic_ai_washing/classification/preliminary_pipeline.py`
- `src/semantic_ai_washing/classification/model_runtime.py`

No new authority move was required in this round.

## Caller families migrated in this round

### Family A: direct preliminary pipeline tests
- `tests/test_preliminary_pipeline.py`

### Family B: direct classification benchmarking tests
- `tests/test_preliminary_benchmarking.py`

## Validation gate

Passed:
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `tests/test_preliminary_pipeline.py`
  - `tests/test_preliminary_benchmarking.py`
  - `projects/ai_washing/tests/test_classification_support_member.py`
- result: `7 passed`
- `git diff --check`

Observed warning profile:
- existing sklearn `UndefinedMetricWarning` lines in benchmarking
- gate still passed cleanly

## Outcome

This round confirms that the member-owned classification support authority is
now close to exhausting its remaining direct legacy-root test tail.

It is a good V2 follow-on batch because:
- the authority was already stable
- the remaining direct callers were still coherent
- the gate was narrow and trustworthy

## Spillover check

No Atlas- or NDA-derived code or structure entered this batch.
