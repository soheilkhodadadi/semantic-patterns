# Migration Round BQ: AI-Washing Build Expanded Sentence Pool Seed V1

## Purpose

Seed the canonical member-owned sentence-pool expansion authority for Queue V17.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/build_expanded_sentence_pool.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`

Direct caller moved:
- `tests/test_iteration2_parallel.py`

New member-local test:
- `projects/ai_washing/tests/test_build_expanded_sentence_pool_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/build_expanded_sentence_pool_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_build_expanded_sentence_pool_member.py`
- `tests/test_iteration2_parallel.py -k "build_expanded_sentence_pool"`

Result:
- `4 passed, 17 deselected`
