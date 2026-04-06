# Migration Round AH: AI-Washing Freeze Split Registry Seed V1

## Scope

Batch 2 from Queue V5.

Authority:
- `ai_washing_member.labeling.freeze_split_registry`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct validation caller bundle onto the new authority

## Pre-Scan Result

The `freeze_split_registry` boundary stayed clean enough to auto-run under Queue V5.

What made it clean:
- the implementation is clearly current-stage and already depends on
  member-owned labeling helpers
- direct caller pressure is concentrated in the dedicated split-freeze test bundle
- the workflow command string in `tests/test_director_roadmap_model.py` can stay
  on the root compatibility path for now
- the validation story is strong and localized

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_freeze_split_registry_member.py`
- `tests/test_split_freeze_publishers.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/freeze_split_registry.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/freeze_split_registry.py`

Migrated callers:
- `tests/test_split_freeze_publishers.py`

New member-local test:
- `projects/ai_washing/tests/test_freeze_split_registry_member.py`
