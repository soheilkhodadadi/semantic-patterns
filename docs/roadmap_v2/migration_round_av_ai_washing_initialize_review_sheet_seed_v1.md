# Migration Round AV: AI-Washing Initialize Review Sheet Seed V1

## Scope

Batch 1 from Queue V10.

Authority:
- `ai_washing_member.labeling.initialize_review_sheet`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate direct labeling workflow callers and tests onto the new authority

## Pre-Scan Result

The `initialize_review_sheet` boundary stayed clean enough to auto-run under Queue V10.

What made it clean:
- it directly serves one active labeling workflow family
- direct caller pressure is concentrated in `benchmark_prompt_variants` and the parallel-workflow tests
- roadmap-model command strings can stay on the compatibility path for now
- no Atlas-adjacent boundary pressure is involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_initialize_review_sheet_member.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/initialize_review_sheet.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/initialize_review_sheet.py`

Migrated callers:
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `tests/test_iteration2_parallel.py`

New member-local test:
- `projects/ai_washing/tests/test_initialize_review_sheet_member.py`
