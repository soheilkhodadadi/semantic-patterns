# Migration Round K: AI-Washing Group 2 Callers V1

## Purpose

This round migrates the Group 2 classification caller family to the member-owned
labeling common surface.

## Authority in force

Canonical authority already existed before this round at:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/labeling/common.py`

## Caller family migrated

The following classification callers now import from
`ai_washing_member.labeling.common`:
- `src/semantic_ai_washing/classification/benchmark_utils.py`
- `src/semantic_ai_washing/classification/benchmark_preliminary_models.py`
- `src/semantic_ai_washing/classification/classify_active_window_preliminary.py`
- `src/semantic_ai_washing/classification/classify_active_window_preliminary_restartable.py`
- `src/semantic_ai_washing/classification/model_runtime.py`
- `src/semantic_ai_washing/classification/preliminary_pipeline.py`
- `src/semantic_ai_washing/classification/train_binary_relevance_then_as.py`
- `src/semantic_ai_washing/classification/train_logreg_preliminary.py`
- `src/semantic_ai_washing/classification/train_preliminary_centroids.py`

## Blockers encountered

The focused gate surfaced two pre-existing, low-blast-radius failures:
- restartable classification warming assumed a populated runtime payload even in
  a light test harness
- active-window sentence materialization assumed `args.max_tokens` always
  existed even though the parser default already defines the fallback behavior

Fixes applied in this round:
- `src/semantic_ai_washing/classification/classify_active_window_preliminary_restartable.py`
  now skips warm-up cleanly when runtime metadata is absent
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py` now
  falls back to `DEFAULT_MAX_TOKENS` when `args.max_tokens` is missing

## Playbook check

Curated playbooks were consulted.
No curated playbook directly matched this blocker because the issue was not
extraction quality or prompt-boundary quality. The fixes stayed within the same
low-blast-radius principle used by the playbook library.

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- focused pytest bundle:
  - `tests/test_preliminary_pipeline.py`
  - `tests/test_preliminary_benchmarking.py`
  - `tests/test_preliminary_classification_restartable.py`
  - `tests/test_preliminary_phase3.py`
- result: `9 passed`
- `git diff --check`

## Outcome

Group 2 is now complete.

This is the second full `ai_washing` caller-family migration after the Group 1
labeling move, and it leaves the project ready for a smaller checkpoint before
any Group 3 aggregation/data migration.
