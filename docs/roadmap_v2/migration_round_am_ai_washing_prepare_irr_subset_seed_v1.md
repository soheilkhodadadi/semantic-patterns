# Migration Round AM: AI-Washing Prepare IRR Subset Seed V1

## Scope

Batch 1 from Queue V7.

Authority:
- `ai_washing_member.labeling.prepare_irr_subset`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct IRR workflow caller bundle onto the new authority

## Pre-Scan Result

The `prepare_irr_subset` boundary stayed clean enough to auto-run under Queue V7.

What made it clean:
- the implementation is current-stage and already depends only on member-owned
  labeling helpers
- direct caller pressure is concentrated in the IRR-phase regression bundle
- roadmap-model command strings can stay on the compatibility path for now
- it naturally sets up `adjudicate_irr_labels` as the next clean follow-on

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_prepare_irr_subset_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/prepare_irr_subset.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/prepare_irr_subset.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_prepare_irr_subset_member.py`
