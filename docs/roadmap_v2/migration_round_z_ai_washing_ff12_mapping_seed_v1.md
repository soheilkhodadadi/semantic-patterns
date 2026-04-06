# Migration Round Z: AI-Washing FF12 Mapping Seed V1

## Scope

Batch 4 from the ordered execution queue.

Authority:

- `ai_washing_member.labeling.ff12_mapping`

Batch:

- pre-scan the provisional authority candidate
- seed the canonical member-owned implementation
- retain the legacy shim
- migrate the direct production callers
- migrate the direct validation edge

## Pre-Scan Result

The Batch 4 pre-scan stayed clean enough to auto-run under Protocol V2.

What made it clean:

- the authority is small and self-contained
- there are only two real production callers
- the existing integration gate already exercises both callers
- no mixed lane or mixed authority move was required

## Changes

### Canonical Member Authority

- `projects/ai_washing/src/ai_washing_member/labeling/ff12_mapping.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/labeling/ff12_mapping.py`

### Direct Caller Migration

- `projects/ai_washing/src/ai_washing_member/data/build_filing_manifest.py`
- `src/semantic_ai_washing/labeling/build_labeling_sample.py`

### Direct Validation Edge

- `projects/ai_washing/tests/test_ff12_mapping_member.py`
- `tests/test_labeling_phase1.py`
- `tests/test_sentence_table_pilot.py`
- `tests/test_iteration2_parallel.py`

## Completed Validation Gate

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- pytest bundle:
  - `projects/ai_washing/tests/test_ff12_mapping_member.py`
  - `tests/test_labeling_phase1.py`
  - `tests/test_sentence_table_pilot.py`
  - `tests/test_iteration2_parallel.py`
- `git diff --check`

Validation result:

- passed cleanly
- no additional compatibility fix was required during the gate

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
