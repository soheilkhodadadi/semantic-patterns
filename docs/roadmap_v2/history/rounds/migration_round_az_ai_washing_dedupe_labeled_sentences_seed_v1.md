# Migration Round AZ: AI-Washing Dedupe Labeled Sentences Seed V1

## Scope

Batch 2 from Queue V11.

Authority:
- `ai_washing_member.labeling.dedupe_labeled_sentences`

Batch:
- seed canonical member authority
- keep the root project path as a compatibility shim
- migrate direct workflow callers and tests onto the new authority

## Pre-Scan Result

The `dedupe_labeled_sentences` boundary stayed clean enough to auto-run under Queue V11.

What made it clean:
- it is the direct follow-on after the sample-builder round
- direct caller pressure is concentrated in `tests/test_labeling_phase1.py`
- it keeps the same dataset-prep workflow inside the member-owned lane
- no Atlas-adjacent boundary pressure is involved

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_dedupe_labeled_sentences_member.py`
- `tests/test_labeling_phase1.py`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/dedupe_labeled_sentences.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/dedupe_labeled_sentences.py`

Migrated callers:
- `tests/test_labeling_phase1.py`

New member-local test:
- `projects/ai_washing/tests/test_dedupe_labeled_sentences_member.py`
