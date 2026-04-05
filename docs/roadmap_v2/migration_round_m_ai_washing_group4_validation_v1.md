# Migration Round M: AI-Washing Group 4 Validation Caller V1

## Purpose

This round migrates the final Group 4 director-adjacent validation caller to the
member-owned labeling common surface.

## Authority in force

Canonical authority already existed before this round at:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/labeling/common.py`

## Caller migrated

The final Group 4 caller now imports from
`ai_washing_member.labeling.common`:
- `src/semantic_ai_washing/director/tasks/validation_assets.py`

## Validation gate

Passed:
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- focused pytest bundle:
  - `tests/test_director_validation_assets.py`
- result: `3 passed`
- `git diff --check`

## Spillover check

This round stayed within repo-local `director` validation assets only.
No Atlas- or NDA-derived code or structure was introduced.

## Outcome

Group 4 is now complete.

The full `labeling/common.py` grouped migration family is now finished.
