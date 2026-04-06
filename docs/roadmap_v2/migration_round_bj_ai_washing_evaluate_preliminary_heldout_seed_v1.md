# Migration Round BJ: AI-Washing Evaluate Preliminary Heldout Seed V1

## Purpose

Seed the canonical member-owned held-out evaluation authority for the preliminary classification lane and migrate its direct caller.

## Canonical authority

- `projects/ai_washing/src/ai_washing_member/classification/evaluate_preliminary_heldout.py`

## Compatibility shim

- `src/semantic_ai_washing/classification/evaluate_preliminary_heldout.py`

## Direct callers migrated

- `tests/test_preliminary_phase3.py`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_evaluate_preliminary_heldout_member.py`
- `tests/test_preliminary_phase3.py -k "preliminary_training_eval_classification"`
- `git diff --check`
