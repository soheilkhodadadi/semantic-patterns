# Score Prelabel Sheet Grouped Migration Sheet V1

## Authority

Canonical member authority:
- `ai_washing_member.labeling.score_prelabel_sheet`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.score_prelabel_sheet`

## Group 1: Direct workflow callers

Files:
- `tests/test_iteration2_parallel.py`

Gate:
- `projects/ai_washing/tests/test_score_prelabel_sheet_member.py`
- `tests/test_iteration2_parallel.py -k "score_prelabel_sheet"`
- `git diff --check`

Status:
- complete
