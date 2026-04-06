# Migration Round L: AI-Washing Group 3 Callers V1

## Purpose

This round migrates the Group 3 aggregation, analysis, and data caller family to
 the member-owned labeling common surface.

## Authority in force

Canonical authority already existed before this round at:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/labeling/common.py`

## Caller family migrated

The following Group 3 callers now import from
`ai_washing_member.labeling.common`:
- `src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py`
- `src/semantic_ai_washing/aggregation/merge_ai_with_patents.py`
- `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- focused pytest bundle:
  - `tests/test_preliminary_phase3.py`
  - `tests/test_preliminary_benchmarking.py`
  - `tests/test_load_table_fallback.py`
- result: `7 passed`
- `git diff --check`

## Spillover check

This round stayed within repo-local `ai_washing` aggregation, analysis, and data
callers only.
No Atlas- or NDA-derived code or structure was introduced.

## Outcome

Group 3 is now complete.

Only the Group 4 director-adjacent validation caller remains in the current
`labeling/common.py` grouped migration plan.
