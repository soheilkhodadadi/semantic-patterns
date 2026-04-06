# Migration Round BT: AI-Washing Materialize Active Window Sentences Seed V1

## Purpose

Seed the canonical member-owned active-window materialization authority for Queue V18.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/materialize_active_window_sentences.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

Direct caller moved:
- `tests/test_preliminary_phase3.py`

New member-local test:
- `projects/ai_washing/tests/test_materialize_active_window_sentences_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/materialize_active_window_sentences_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_materialize_active_window_sentences_member.py`
- `tests/test_preliminary_phase3.py -k "materialize_active_window_sentences"`

Result:
- `2 passed, 2 deselected`
