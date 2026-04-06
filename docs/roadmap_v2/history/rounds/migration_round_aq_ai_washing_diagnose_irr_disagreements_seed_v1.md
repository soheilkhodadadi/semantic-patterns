# Migration Round AQ: AI-Washing Diagnose IRR Disagreements Seed V1

## Scope

Batch 2 from Queue V8.

Authority:
- `ai_washing_member.labeling.diagnose_irr_disagreements`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct IRR workflow caller bundle onto the new authority

## Pre-Scan Result

The `diagnose_irr_disagreements` boundary stayed clean enough to auto-run under Queue V8.

What made it clean:
- it directly follows the newly canonical IRR metrics authority
- the implementation already depends on member-owned labeling helpers and local IRR artifacts only
- direct caller pressure is concentrated in the IRR-phase regression bundle
- roadmap-model command strings can stay on the compatibility path for now

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_diagnose_irr_disagreements_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/diagnose_irr_disagreements.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/diagnose_irr_disagreements.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_diagnose_irr_disagreements_member.py`
