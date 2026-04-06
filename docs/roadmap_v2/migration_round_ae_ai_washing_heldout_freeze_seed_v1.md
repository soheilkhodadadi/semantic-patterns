# Migration Round AE: AI-Washing Held-Out Freeze Seed V1

## Scope

Batch 2 from Queue V4.

Authority:
- `ai_washing_member.labeling.freeze_heldout_v2`

Batch:
- seed canonical member authority
- keep the root labeling path as a compatibility shim
- migrate the direct held-out workflow test onto the new authority

## Pre-Scan Result

The held-out freeze boundary stayed clean enough to auto-run under Queue V4.

What made it clean:
- it depends only on member-owned labeling helpers
- direct caller pressure is narrow and test-led
- no Atlas-facing, package-crossing, or high-blast-radius dependency edge showed up
- it is a coherent follow-on to the held-out sampler authority from Batch 1

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_freeze_heldout_v2_member.py`
- `tests/test_heldout_v2_workflow.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/freeze_heldout_v2.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/freeze_heldout_v2.py`

Migrated callers:
- `tests/test_heldout_v2_workflow.py`

New member-local test:
- `projects/ai_washing/tests/test_freeze_heldout_v2_member.py`
