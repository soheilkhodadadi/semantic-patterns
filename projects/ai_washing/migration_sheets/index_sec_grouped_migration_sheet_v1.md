# AI-Washing SEC Index Grouped Migration Sheet V1

## Purpose

This note records the grouped migration shape used for the member-owned SEC
index surface.

## Canonical member-owned authority

Current member-owned SEC index surface:
- `projects/ai_washing/src/ai_washing_member/data/index_sec_filings.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/data/index_sec_filings.py`

## Grouped caller families

### Family A: extraction callers
- `build_expanded_sentence_pool.py`
- `extract_sentence_table.py`
- `reextract_tranche_slice.py`

### Family B: manifest and window callers
- `build_filing_manifest.py`
- `materialize_active_window_sentences.py`
- `run_historical_backfill.py`

## Shared validation gate

- `projects/ai_washing/tests/test_index_sec_member.py`
- `tests/test_source_index_contract.py`
- `tests/test_preliminary_phase3.py`
- `tests/test_extract_sentence_table_segmentation.py`
- `tests/test_sentence_table_pilot.py`
- `tests/test_iteration2_parallel.py`
- `tests/test_restartable_jobs.py`

## Status

This grouped migration batch has now completed successfully through:
- `docs/roadmap_v2/history/rounds/migration_round_o_ai_washing_index_sec_batch_v1.md`
