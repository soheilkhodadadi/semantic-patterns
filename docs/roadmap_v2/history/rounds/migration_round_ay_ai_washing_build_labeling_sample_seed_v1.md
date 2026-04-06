# Migration Round AY: AI-Washing Build Labeling Sample Seed V1

## Scope

Batch 1 from Queue V11.

Authority:
- `ai_washing_member.labeling.build_labeling_sample`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate direct workflow callers and tests onto the new authority

## Pre-Scan Result

The `build_labeling_sample` boundary stayed clean enough to auto-run under Queue V11.

What made it clean:
- it opens a coherent Phase 1 dataset-prep workflow that is still active
- direct caller pressure is concentrated in `tests/test_labeling_phase1.py`
- it naturally opens the dedupe and QA follow-on rounds
- no Atlas-adjacent boundary pressure is involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_build_labeling_sample_member.py`
- `tests/test_labeling_phase1.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/build_labeling_sample.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/build_labeling_sample.py`

Migrated callers:
- `tests/test_labeling_phase1.py`

New member-local test:
- `projects/ai_washing/tests/test_build_labeling_sample_member.py`
