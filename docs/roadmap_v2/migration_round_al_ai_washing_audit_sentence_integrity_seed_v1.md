# Migration Round AL: AI-Washing Audit Sentence Integrity Seed V1

## Scope

Batch 3 from Queue V6.

Authority:
- `ai_washing_member.labeling.audit_sentence_integrity`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate the direct IRR workflow caller bundle onto the new authority

## Pre-Scan Result

The `audit_sentence_integrity` boundary stayed clean enough to auto-run under
Queue V6.

What made it clean:
- direct caller pressure is concentrated in the IRR-phase regression bundle
- the implementation is compact and current-stage
- its only cross-lane dependency is the already-canonical
  `semantic_director.sensors` fragment-rate helper
- roadmap-model command strings can stay on the compatibility path for now

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_audit_sentence_integrity_member.py`
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/audit_sentence_integrity.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/audit_sentence_integrity.py`

Migrated callers:
- `tests/test_irr_phase2.py`

New member-local test:
- `projects/ai_washing/tests/test_audit_sentence_integrity_member.py`
