# Migration Round AJ: AI-Washing Publish Rubric Freeze Seed V1

## Scope

Batch 1 from Queue V6.

Authority:
- `ai_washing_member.labeling.publish_rubric_freeze`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct validation caller bundle onto the new authority

## Pre-Scan Result

The `publish_rubric_freeze` boundary stayed clean enough to auto-run under Queue V6.

What made it clean:
- the implementation is clearly current-stage and already depends on member-owned
  labeling helpers
- direct caller pressure is concentrated in `tests/test_split_freeze_publishers.py`
- the roadmap-model command string can remain on the root compatibility path for now
- the validation story is strong and localized

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_publish_rubric_freeze_member.py`
- `tests/test_split_freeze_publishers.py`
- `tests/test_irr_phase2.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/publish_rubric_freeze.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/publish_rubric_freeze.py`

Migrated callers:
- `tests/test_split_freeze_publishers.py`

New member-local test:
- `projects/ai_washing/tests/test_publish_rubric_freeze_member.py`
