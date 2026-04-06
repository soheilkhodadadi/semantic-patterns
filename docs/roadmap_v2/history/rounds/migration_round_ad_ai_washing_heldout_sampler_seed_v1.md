# Migration Round AD: AI-Washing Held-Out Sampler Seed V1

## Scope

Batch 1 from Queue V4.

Authority:
- `ai_washing_member.labeling.sample_heldout_v2_candidates`

Batch:
- seed canonical member authority
- keep the root labeling path as a compatibility shim
- migrate the restartable wrapper and direct workflow tests onto the new authority

## Pre-Scan Result

The held-out sampler boundary stayed clean enough to auto-run under Queue V4.

What made it clean:
- imports already point into member-owned `classification` and `labeling` helpers
- direct runtime caller is limited to one wrapper module
- direct regression surface is well defined in the held-out workflow tests
- no Atlas-facing or NDA-adjacent dependency surfaces are involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_sample_heldout_v2_candidates_member.py`
- `tests/test_heldout_v2_workflow.py`
- `tests/test_restartable_jobs.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/sample_heldout_v2_candidates.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/sample_heldout_v2_candidates.py`

Migrated callers:
- `src/semantic_ai_washing/labeling/sample_heldout_v2_restartable.py`
- `tests/test_heldout_v2_workflow.py`

New member-local test:
- `projects/ai_washing/tests/test_sample_heldout_v2_candidates_member.py`
