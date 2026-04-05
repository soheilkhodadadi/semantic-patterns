# Fresh Authority Comparison V3

## Scope

Compare the next fresh-authority options after the `director` `roadmap_model`
seed:

- `semantic_ai_washing.data.build_filing_manifest`
- `semantic_ai_washing.director.core.render`

## Result

Chosen fresh authority:

- `semantic_director.render`

## Why `render` Won

- It has broader direct caller leverage in the active `director` lane.
- It is tightly related to the already-migrated `roadmap_model` authority.
- It keeps acceleration inside one lane with a clean Protocol V2 batch:
  - CLI runtime edge
  - optimization edge
  - review/reporting edge
  - direct validation edge

## Why `build_filing_manifest` Lost This Round

- It still has only one direct production caller and one direct test edge.
- It still depends on a root-owned mapping surface.
- It remains a reasonable future `ai_washing` authority, but not the strongest
  current acceleration surface.

## Direct Caller Pressure

`render` direct callers at decision time:

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/optimizer.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_roadmap_model.py`

`build_filing_manifest` direct callers at decision time:

- `src/semantic_ai_washing/data/build_expanded_sentence_pool.py`
- `tests/test_sentence_table_pilot.py`

## Decision

Take `render` now as the next `director` fresh authority, then apply Protocol V2
on top of that authority in one bounded caller-family batch.
