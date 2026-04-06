# Fresh Authority Comparison V2

## Scope

Compare the next fresh-authority options after the `ai_washing` `benchmark_utils`
seed:

- `semantic_ai_washing.data.build_filing_manifest`
- `semantic_ai_washing.director.core.roadmap_model`

## Result

Chosen fresh authority:

- `semantic_director.roadmap_model`

## Why `roadmap_model` Won

- It has materially higher leverage across the active `director` lane.
- It is compact enough to extract safely.
- Its dependency shape is clean:
  - standard library
  - `yaml`
  - `semantic_director.schemas`
- It already sits at a natural package boundary inside `director`.

## Why `build_filing_manifest` Lost This Round

- It currently has only one direct production caller and one direct test edge.
- It still leans on root-owned `semantic_ai_washing.labeling.ff12_mapping`.
- That makes it a weaker acceleration surface than `roadmap_model` for the next
  fresh-authority round.

## Direct Caller Pressure

`roadmap_model` direct callers at decision time:

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/adapters/documents.py`
- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/task_graph.py`
- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_roadmap_model.py`

`build_filing_manifest` direct callers at decision time:

- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
- `tests/test_sentence_table_pilot.py`

## Decision

Take `roadmap_model` now as the next `director` fresh authority, then apply
Protocol V2 on top of that new authority in one bounded caller-family batch.
