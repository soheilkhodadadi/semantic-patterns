# Migration Round AN: AI-Washing Adjudication Seed V1

## Scope

Batch 2 from Queue V7.

Authority:
- `ai_washing_member.labeling.adjudicate_irr_labels`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct IRR workflow caller bundle onto the new authority

## Pre-Scan Result

The `adjudicate_irr_labels` boundary stayed clean enough to auto-run under Queue V7.

What made it clean:
- it is a direct follow-on to `prepare_irr_subset` in the same current-stage workflow
- direct caller pressure is concentrated in the IRR-phase regression bundle
- roadmap-model command strings can stay on the compatibility path for now
- its dependencies stay inside member-owned helpers plus standard local I/O

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_adjudicate_irr_labels_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/adjudicate_irr_labels.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/adjudicate_irr_labels.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_adjudicate_irr_labels_member.py`
