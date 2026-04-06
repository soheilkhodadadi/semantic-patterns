# Migration Round AC: AI-Washing Build Labeling Batch Seed V1

## Scope

Batch 3 from Queue V3.

Authority:

- `ai_washing_member.labeling.build_labeling_batch`

Batch:

- pre-scan the queued authority
- seed the canonical member-owned implementation
- retain the legacy shim
- migrate the direct validation callers

## Pre-Scan Result

The `build_labeling_batch` boundary stayed clean enough to auto-run under Queue
V2.

What made it clean:

- mostly self-contained logic
- depends only on member-owned `labeling.common`
- direct caller pressure is test-led rather than spread across multiple runtime
  modules
- root command-string references can stay stable through the compatibility shim

## Changes

### Canonical Member Authority

- `projects/ai_washing/src/ai_washing_member/labeling/build_labeling_batch.py`

### Legacy Compatibility Shim

- `src/semantic_ai_washing/labeling/build_labeling_batch.py`

### Direct Validation Caller Migration

- `tests/test_labeling_batch.py`
- `tests/test_iteration2_parallel.py`
- `projects/ai_washing/tests/test_build_labeling_batch_member.py`

## Gate

Completed validation gate:

- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `projects/ai_washing` member tests
- `tests/test_labeling_batch.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Validation result:

- passed cleanly
- no additional compatibility fix was required during the gate

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this migration round.
