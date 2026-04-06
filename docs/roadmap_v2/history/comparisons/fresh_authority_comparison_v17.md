# Fresh Authority Comparison V17

## Purpose

Choose the Queue V14 opener from the new root-surface triage registry.

## Candidates compared

1. `ai_washing_member.classification.train_preliminary_centroids`
2. `ai_washing_member.data.build_expanded_sentence_pool`

## Candidate A: `ai_washing_member.classification.train_preliminary_centroids`

Why it is attractive:
- it opens the active preliminary-classification chain from the new triage registry
- it sits on top of member-owned support already migrated under `ai_washing_member.classification`
- it naturally opens `classify_active_window_preliminary` and `evaluate_preliminary_heldout` as a coherent Queue V14 follow-on
- strong focused regression bundles already exist in `tests/test_preliminary_phase3.py` and `tests/test_preliminary_benchmarking.py`

Risk shape:
- medium
- one active `ai_washing` workflow lane
- no mixed hygiene or control-plane boundary needed

## Candidate B: `ai_washing_member.data.build_expanded_sentence_pool`

Why it is attractive:
- it remains a real active candidate from the root-surface triage registry
- it has strong tests and clear downstream relevance to sentence-table workflows

Risk shape:
- medium-high
- wider data-lane caller spread than the classification opener
- less clean as a three-batch Queue V14 workflow than the centroid baseline chain

## Decision

Chosen Queue V14 opener:
- `ai_washing_member.classification.train_preliminary_centroids`

## Why this wins now

It gives Queue V14 a cleaner workflow shape:

1. `train_preliminary_centroids`
2. `classify_active_window_preliminary`
3. `evaluate_preliminary_heldout`

That keeps the queue inside one active preliminary-classification lane while using the new triage registry exactly as intended.
