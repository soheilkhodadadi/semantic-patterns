# Migration Round AS: AI-Washing Publish Preliminary Results Readiness Seed V1

## Scope

Batch 1 from Queue V9.

Authority:
- `ai_washing_member.labeling.publish_preliminary_results_readiness`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct preliminary-results workflow caller bundle onto the new authority

## Pre-Scan Result

The `publish_preliminary_results_readiness` boundary stayed clean enough to auto-run under Queue V9.

What made it clean:
- it directly follows the newly canonical IRR metrics and disagreement diagnostic authorities
- the implementation already depends only on member-owned labeling helpers plus local report artifacts
- direct caller pressure is concentrated in `tests/test_irr_phase2.py`
- roadmap-model command strings can stay on the compatibility path for now

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_publish_preliminary_results_readiness_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/publish_preliminary_results_readiness.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/publish_preliminary_results_readiness.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_publish_preliminary_results_readiness_member.py`
