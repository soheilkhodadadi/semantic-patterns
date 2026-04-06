# Migration Round BG: AI-Washing Score Prelabel Sheet Seed V1

## Scope

Batch 3 from Queue V13.

Authority:
- `ai_washing_member.labeling.score_prelabel_sheet`

Batch:
- seed canonical member authority
- keep the legacy root path as a compatibility shim
- close the assistive calibration workflow with the scoring/report utility

## Pre-Scan Result

The `score_prelabel_sheet` boundary stayed clean enough to auto-run after Batches 1 and 2.

What made it clean:
- the module is self-contained and already shared the same workflow-level root gate
- it has no transport or monkeypatch-sensitive dependency surface of its own
- the compatibility shim can stay minimal without distorting test behavior
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_score_prelabel_sheet_member.py`
- `tests/test_iteration2_parallel.py -k "score_prelabel_sheet"`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/score_prelabel_sheet.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/score_prelabel_sheet.py`

New member test:
- `projects/ai_washing/tests/test_score_prelabel_sheet_member.py`
