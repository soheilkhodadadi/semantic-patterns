# Fresh Authority Comparison V8

## Purpose

Choose the opening authority for Queue V5 after the Queue V4 checkpoint and the
migrated-surface relevance audit.

## Candidates

### Candidate A

Authority:
- `semantic_director.sensors`

Why it is attractive:
- high-leverage `director` surface with direct runtime and test pressure
- already blocks the `semantic_director.readiness` package from being fully
  self-contained
- supports a clean same-lane Protocol V2 batch
- keeps Atlas-adjacent adapters out of scope

Risks:
- one downstream `ai_washing` caller still exists in `audit_sentence_integrity`
- that cross-lane edge should not be dragged into the same batch

### Candidate B

Authority:
- `ai_washing_member.labeling.freeze_split_registry`

Why it is attractive:
- clearly current-stage work, not template residue
- strong fit with the active held-out and labeling workflow lane
- direct regression bundle already exists in `tests/test_split_freeze_publishers.py`

Risks:
- has lower immediate leverage than `sensors`
- still leaves the `director` package boundary partially dependent on a root
  authority that is now obviously ready to move

## Decision

Choose:
- `semantic_director.sensors`

Why it wins now:
- stronger leverage on a currently active package boundary
- cleaner one-lane batch under Protocol V2
- improves package cohesion by removing a root dependency from
  `semantic_director.readiness`
- leaves `freeze_split_registry` available as the next good `ai_washing` round
  instead of forcing it early

Do not choose first:
- `ai_washing_member.labeling.freeze_split_registry`

## Queue V5 Guidance

The next three-round cycle should be:

1. `semantic_director.sensors`
2. `ai_washing_member.labeling.freeze_split_registry`
3. `semantic_director.playbooks`

If Batch 1 gets messy at pre-scan or gate time:
- rotate early to `ai_washing_member.labeling.freeze_split_registry`
