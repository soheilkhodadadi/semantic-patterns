# Fresh Authority Comparison V9

## Purpose

Choose the opening authority for Queue V6 after Queue V5 completed cleanly.

## Candidates

### Candidate A

Authority:
- `ai_washing_member.labeling.publish_rubric_freeze`

Why it is attractive:
- clearly current-stage and directly follows the just-migrated split-freeze workflow
- already depends on member-owned labeling helpers
- has a concentrated validation surface in `tests/test_split_freeze_publishers.py`
- keeps lane balance healthier after Queue V5 ended in `director`

Risks:
- the stable command string in `tests/test_director_roadmap_model.py` should stay on the
  root compatibility path for now
- one additional readiness-oriented test path exists in `tests/test_irr_phase2.py`

### Candidate B

Authority:
- `semantic_director.snapshot`

Why it is attractive:
- meaningful `director` leverage through `cli` and the core test bundle
- snapshot ingestion is an important package boundary for the control plane
- pairs naturally with already-packaged `state`, `roadmap_model`, and `playbooks`

Risks:
- touches Atlas-adjacent adapter wiring through `fetch_atlas_metadata`
- slightly broader surface than the `ai_washing` candidate
- less desirable as the immediate opener after a Queue V5 that ended in `director`

## Decision

Choose:
- `ai_washing_member.labeling.publish_rubric_freeze`

Why it wins now:
- cleaner immediate opener
- stronger lane balance
- lower blast radius than `snapshot`
- preserves `semantic_director.snapshot` as the next good director rotation once
  this `ai_washing` follow-on closes cleanly

Do not choose first:
- `semantic_director.snapshot`

## Queue V6 Guidance

The next three-round cycle should be:

1. `ai_washing_member.labeling.publish_rubric_freeze`
2. `semantic_director.snapshot`
3. `ai_washing_member.labeling.audit_sentence_integrity`

If Batch 1 gets messy at pre-scan or gate time:
- rotate early to `semantic_director.snapshot`
