# Migration Round BV: AI-Washing Reextract Tranche Slice Seed V1

## Purpose

Seed the canonical member-owned tranche reextraction authority for Queue V18.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/data/reextract_tranche_slice.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/data/reextract_tranche_slice.py`

Direct caller moved:
- `tests/test_sentence_table_pilot.py`

New member-local test:
- `projects/ai_washing/tests/test_reextract_tranche_slice_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/reextract_tranche_slice_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_reextract_tranche_slice_member.py`
- `tests/test_sentence_table_pilot.py -k "reextract_tranche_slice"`

Result:
- `3 passed, 8 deselected`
