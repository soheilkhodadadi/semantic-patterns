# Fresh Authority Comparison V11

## Purpose

Choose the opening authority for Queue V8 after Queue V7 completed cleanly.

## Candidates

### Candidate A

Authority:
- `ai_washing_member.labeling.compute_irr_metrics`

Why it is attractive:
- directly follows the just-migrated IRR subset and adjudication workflow
- already depends only on member-owned labeling helpers plus local report inputs
- has a concentrated regression surface in `tests/test_irr_phase2.py`
- naturally sets up `diagnose_irr_disagreements` as the next clean follow-on

Risks:
- stable roadmap-model command strings should stay on the root compatibility
  path for now
- the regression bundle is focused but still slightly broader than a tiny helper

### Candidate B

Authority:
- `semantic_director.executor`

Why it is attractive:
- strong `director` leverage through `cli` and the core execution bundle
- now sits downstream of already-packaged `decision`, `gates`, and `sensors`
- would make the package boundary feel much more complete

Risks:
- broader surface than the IRR candidate
- better as a cycle closer after one more flagship-project workflow move
- depends on still-root audit/runtime helpers, so it is not the lowest-blast opener

## Decision

Choose:
- `ai_washing_member.labeling.compute_irr_metrics`

Why it wins now:
- stronger current-stage relevance
- cleaner immediate continuation of the IRR workflow lane
- lower blast radius than `executor`
- preserves `semantic_director.executor` as a good V8 closeout once the IRR
  reporting pair is moved

Do not choose first:
- `semantic_director.executor`

## Queue V8 Guidance

The next three-round cycle should be:

1. `ai_washing_member.labeling.compute_irr_metrics`
2. `ai_washing_member.labeling.diagnose_irr_disagreements`
3. `semantic_director.executor`

If Batch 1 gets messy at pre-scan or gate time:
- rotate early to `semantic_director.executor`
