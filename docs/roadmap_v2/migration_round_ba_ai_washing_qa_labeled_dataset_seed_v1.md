# Migration Round BA: AI-Washing QA Labeled Dataset Seed V1

## Scope

Batch 3 from Queue V11.

Authority:
- `ai_washing_member.labeling.qa_labeled_dataset`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate direct workflow callers and tests onto the new authority

## Pre-Scan Result

The `qa_labeled_dataset` boundary stayed clean enough to auto-run under Queue V11.

What made it clean:
- it closes the same active Phase 1 dataset-prep workflow as Batches 1 and 2
- direct caller pressure is concentrated in `tests/test_labeling_phase1.py`
- the shared regression bundle already covers the full workflow chain
- no Atlas-adjacent boundary pressure is involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_qa_labeled_dataset_member.py`
- `tests/test_labeling_phase1.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/qa_labeled_dataset.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/qa_labeled_dataset.py`

Migrated callers:
- `tests/test_labeling_phase1.py`

New member-local test:
- `projects/ai_washing/tests/test_qa_labeled_dataset_member.py`
