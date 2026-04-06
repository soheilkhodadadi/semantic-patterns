# Migration Round AP: AI-Washing Compute IRR Metrics Seed V1

## Scope

Batch 1 from Queue V8.

Authority:
- `ai_washing_member.labeling.compute_irr_metrics`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct IRR workflow caller bundle onto the new authority

## Pre-Scan Result

The `compute_irr_metrics` boundary stayed clean enough to auto-run under Queue V8.

What made it clean:
- it directly follows the subset and adjudication authorities that just moved
- the implementation already depends only on member-owned labeling helpers plus local report inputs
- direct caller pressure is concentrated in the IRR-phase regression bundle
- roadmap-model command strings can stay on the compatibility path for now

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_compute_irr_metrics_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/compute_irr_metrics.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/compute_irr_metrics.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_compute_irr_metrics_member.py`
