# AI-Washing Sentence Table Grouped Migration Sheet V1

## Purpose

This note records the grouped migration shape used for the member-owned
sentence-table surface.

## Canonical member-owned authority

Current member-owned sentence-table surface:
- `projects/ai_washing/src/ai_washing_member/data/extract_sentence_table.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/data/extract_sentence_table.py`

## Grouped caller families

### Family A: expansion pipeline callers
- `build_expanded_sentence_pool.py`

### Family B: active-window materialization callers
- `materialize_active_window_sentences.py`

### Family C: segmentation benchmark callers
- `benchmark_segmentation_modes.py`

### Family D: direct contract and segmentation import callers
- `tests/test_extract_sentence_table_segmentation.py`
- `tests/test_sentence_table_pilot.py`

## Shared validation gate

- `projects/ai_washing/tests/test_extract_sentence_table_member.py`
- `tests/test_extract_sentence_table_segmentation.py`
- `tests/test_sentence_table_pilot.py`
- `tests/test_preliminary_phase3.py`
- `tests/test_iteration2_parallel.py`
- `tests/test_restartable_jobs.py`

## Status

This grouped migration batch has now completed successfully through:
- `docs/roadmap_v2/history/rounds/migration_round_p_ai_washing_sentence_table_batch_v1.md`
