# Migration Round BR: AI-Washing Combine Expanded Sentence Pool Batches Seed V1

## Purpose

Seed the canonical member-owned cumulative sentence-pool combine authority for Queue V17.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/combine_expanded_sentence_pool_batches.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/combine_expanded_sentence_pool_batches.py`

Direct caller moved:
- `tests/test_iteration2_parallel.py`

New member-local test:
- `projects/ai_washing/tests/test_combine_expanded_sentence_pool_batches_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/combine_expanded_sentence_pool_batches_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_combine_expanded_sentence_pool_batches_member.py`
- `tests/test_iteration2_parallel.py -k "combine_expanded_sentence_pool_batches"`

Result:
- `2 passed, 19 deselected`
