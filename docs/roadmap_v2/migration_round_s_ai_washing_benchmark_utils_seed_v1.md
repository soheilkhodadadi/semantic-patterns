# Migration Round S: AI-Washing Benchmark Utils Seed V1

## Purpose

This round opens the next fresh `ai_washing` member-owned authority under
Protocol V2 and applies an authority-seed batch on top of it.

## Fresh authority selected

New member-owned benchmark utility surface:
- `projects/ai_washing/src/ai_washing_member/classification/benchmark_utils.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/classification/benchmark_utils.py`

## Caller families migrated in this round

### Family A: benchmark matrix callers
- `src/semantic_ai_washing/classification/benchmark_preliminary_models.py`

### Family B: held-out evaluation callers
- `src/semantic_ai_washing/classification/evaluate_preliminary_heldout.py`

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `projects/ai_washing/tests/test_benchmark_utils_member.py`
  - `tests/test_preliminary_benchmarking.py`
  - `tests/test_preliminary_phase3.py`
- result: `8 passed`
- `git diff --check`

Observed warning profile:
- existing sklearn `UndefinedMetricWarning` lines in benchmarking
- gate still passed cleanly

## Outcome

This round is intended to be the first fresh-authority acceleration after the
established-authority cleanup batches.

It passed cleanly and gives us:
- one fresh member-owned authority move
- two direct production caller families migrated in the same round
- one shared regression gate

## Spillover check

No Atlas- or NDA-derived code or structure entered this batch.
