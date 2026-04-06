# Fresh Authority Comparison V4

## Scope

Compare the next fresh-authority options after the `director` `render` seed:

- `semantic_ai_washing.data.build_filing_manifest`
- `semantic_ai_washing.director.core.task_graph`

## Result

Chosen fresh authority:

- `semantic_director.task_graph`

## Why `task_graph` Won

- It has materially stronger direct caller pressure in the active `director` lane.
- It is compact and downstream of already-canonical `roadmap_model`.
- It supports a clean Protocol V2 batch inside one lane:
  - readiness edge
  - planning/optimization edge
  - review edge
  - validation edge

## Why `build_filing_manifest` Lost This Round

- It still has one direct production caller and one direct test edge.
- It still leans on root-owned industry mapping logic.
- It remains a plausible future `ai_washing` authority, but it is still weaker
  than the current `director` continuation path.

## Direct Caller Pressure

`task_graph` direct callers at decision time:

- `src/semantic_ai_washing/director/core/readiness.py`
- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_roadmap_model.py`

`build_filing_manifest` direct callers at decision time:

- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
- `tests/test_sentence_table_pilot.py`

## Decision

Take `task_graph` now as the next `director` fresh authority, then apply
Protocol V2 immediately on top of that authority.
