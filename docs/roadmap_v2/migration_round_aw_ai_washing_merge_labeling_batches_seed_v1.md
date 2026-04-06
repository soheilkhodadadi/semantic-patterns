# Migration Round AW: AI-Washing Merge Labeling Batches Seed V1

## Scope

Batch 2 from Queue V10.

Authority:
- `ai_washing_member.labeling.merge_labeling_batches`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate direct workflow callers and tests onto the new authority

## Pre-Scan Result

The `merge_labeling_batches` boundary stayed clean enough to auto-run under Queue V10.

What made it clean:
- it remains inside the same active labeling workflow family as Queue V10 Batch 1
- direct caller pressure is concentrated in the parallel workflow test bundle
- roadmap-model command strings can stay on the compatibility path for now
- no Atlas-adjacent boundary pressure is involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_merge_labeling_batches_member.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/merge_labeling_batches.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/merge_labeling_batches.py`

Migrated callers:
- `tests/test_iteration2_parallel.py`

New member-local test:
- `projects/ai_washing/tests/test_merge_labeling_batches_member.py`
