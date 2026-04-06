# Migration Round P: AI-Washing Sentence Table Batch V1

## Purpose

This round seeds the next member-owned `ai_washing` data authority surface and
uses it for the first four-family larger-batch experiment.

## Canonical authority moved in this round

New member-owned sentence-table surface:
- `projects/ai_washing/src/ai_washing_member/data/extract_sentence_table.py`

Member-local support exports:
- `projects/ai_washing/src/ai_washing_member/data/__init__.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/data/extract_sentence_table.py`

## Caller families migrated in the same batch

### Family A: expansion pipeline callers
- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`

### Family B: active-window materialization callers
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

### Family C: segmentation benchmark callers
- `src/semantic_ai_washing/data/benchmark_segmentation_modes.py`

### Family D: direct contract and segmentation import callers
- `tests/test_extract_sentence_table_segmentation.py`
- `tests/test_sentence_table_pilot.py`

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `projects/ai_washing/tests/test_extract_sentence_table_member.py`
  - `tests/test_extract_sentence_table_segmentation.py`
  - `tests/test_sentence_table_pilot.py`
  - `tests/test_preliminary_phase3.py`
  - `tests/test_iteration2_parallel.py`
  - `tests/test_restartable_jobs.py`
- result: `37 passed`
- `git diff --check`

## Outcome

This larger batch passed cleanly.

It is the first successful example in this repo of:
- one authority move
- four tightly related caller families in one project lane
- one shared regression gate
- one clean commit

The fourth family here is the direct validation/import edge, not a separate
production subsystem. That distinction keeps the batch aggressive but still
bounded.

## Spillover check

No Atlas- or NDA-derived code or structure entered this batch.
