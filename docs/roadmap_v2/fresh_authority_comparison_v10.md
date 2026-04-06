# Fresh Authority Comparison V10

## Purpose

Choose the opening authority for Queue V7 after Queue V6 completed cleanly.

## Candidates

### Candidate A

Authority:
- `ai_washing_member.labeling.prepare_irr_subset`

Why it is attractive:
- clearly current-stage and directly follows the just-migrated
  `audit_sentence_integrity` IRR workflow edge
- already depends only on member-owned labeling helpers
- has a concentrated regression surface in `tests/test_irr_phase2.py`
- naturally sets up `adjudicate_irr_labels` as the next clean follow-on move

Risks:
- stable roadmap-model command strings should stay on the root compatibility
  path for now
- the test bundle is broad enough that we need to keep the gate focused

### Candidate B

Authority:
- `semantic_director.gates`

Why it is attractive:
- compact package boundary with a single obvious runtime consumer
- positions `semantic_director.executor` for a cleaner future round
- low implementation complexity

Risks:
- narrower immediate leverage than the IRR workflow candidate
- best value comes as a cycle closer after a stronger flagship-project opener

## Decision

Choose:
- `ai_washing_member.labeling.prepare_irr_subset`

Why it wins now:
- stronger current-stage relevance
- cleaner immediate momentum in the flagship project lane
- opens a natural two-round IRR workflow sequence before rotating back into
  `director`

Do not choose first:
- `semantic_director.gates`

## Queue V7 Guidance

The next three-round cycle should be:

1. `ai_washing_member.labeling.prepare_irr_subset`
2. `ai_washing_member.labeling.adjudicate_irr_labels`
3. `semantic_director.gates`

If Batch 1 gets messy at pre-scan or gate time:
- rotate early to `semantic_director.gates`
