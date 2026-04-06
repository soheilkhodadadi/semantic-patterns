# Migration Round O: AI-Washing SEC Index Batch V1

## Purpose

This round seeds the next member-owned `ai_washing` data authority surface and
uses it for the second larger-but-still-bounded batch experiment.

## Canonical authority moved in this round

New member-owned data/index surface:
- `projects/ai_washing/src/ai_washing_member/data/index_sec_filings.py`

Member-local export surface:
- `projects/ai_washing/src/ai_washing_member/data/__init__.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/data/index_sec_filings.py`

## Caller families migrated in the same batch

### Family A: extraction callers
- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
- `src/semantic_ai_washing/data/extract_sentence_table.py`
- `src/semantic_ai_washing/data/reextract_tranche_slice.py`

### Family B: manifest and window callers
- `src/semantic_ai_washing/data/build_filing_manifest.py`
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`
- `src/semantic_ai_washing/data/run_historical_backfill.py`

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `projects/ai_washing/tests/test_index_sec_member.py`
  - `tests/test_source_index_contract.py`
  - `tests/test_preliminary_phase3.py`
  - `tests/test_extract_sentence_table_segmentation.py`
  - `tests/test_sentence_table_pilot.py`
  - `tests/test_iteration2_parallel.py`
  - `tests/test_restartable_jobs.py`
- result: `40 passed`
- `git diff --check`

## Outcome

This larger batch passed cleanly.

It is the second successful example in this repo of:
- one authority move
- two adjacent caller families
- one shared regression gate
- one clean commit

It strengthens the case for larger bounded batches under one established
project-member authority.

## Spillover check

No Atlas- or NDA-derived code or structure entered this batch.
