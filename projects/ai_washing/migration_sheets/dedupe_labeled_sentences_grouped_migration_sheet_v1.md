# Dedupe Labeled Sentences Grouped Migration Sheet V1

## Authority

Canonical member authority:
- `ai_washing_member.labeling.dedupe_labeled_sentences`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.dedupe_labeled_sentences`

## Group 1: Direct workflow callers

Files:
- `tests/test_labeling_phase1.py`

Gate:
- `projects/ai_washing/tests/test_dedupe_labeled_sentences_member.py`
- `tests/test_labeling_phase1.py`
- `git diff --check`

Status:
- complete
