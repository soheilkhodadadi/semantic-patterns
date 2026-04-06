# Migration Round W: AI-Washing Build Filing Manifest Seed V1

## Scope

Batch 1 from the ordered execution queue.

Authority:

- `ai_washing_member.data.build_filing_manifest`

Batch:

- seed the canonical member-owned implementation
- retain the legacy shim
- migrate the planned direct caller family
- migrate the direct validation edge

## Changes

### Canonical Member Authority

- `projects/ai_washing/src/ai_washing_member/data/build_filing_manifest.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/data/build_filing_manifest.py`

### Direct Caller Migration

- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
- `tests/test_sentence_table_pilot.py`

### Member Test

- `projects/ai_washing/tests/test_build_filing_manifest_member.py`

## Gate

Planned validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `projects/ai_washing/tests/test_build_filing_manifest_member.py`
- `tests/test_sentence_table_pilot.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
