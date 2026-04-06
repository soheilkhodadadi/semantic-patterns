# Fresh Authority Comparison V19

## Purpose

Choose the Queue V16 opener from the remaining active `ai_washing` surfaces in the root-surface triage registry.

## Candidates compared

1. `ai_washing_member.classification.publish_selected_preliminary_eval`
2. `ai_washing_member.data.build_expanded_sentence_pool`

## Candidate A: `ai_washing_member.classification.publish_selected_preliminary_eval`

Why it is attractive:
- it opens the remaining downstream preliminary classification reporting lane after Queue V15
- it pairs naturally with `reconcile_preliminary_classification_report` and the thin restartable wrapper closeout
- it lets Queue V16 finish the remaining active preliminary classification surfaces before rotating lanes
- the existing benchmarking and restartable test bundles already provide a clean, bounded gate shape

Risk shape:
- medium-low
- one active `ai_washing` workflow lane
- narrow dependency spread because the upstream model-selection path is already canonical

## Candidate B: `ai_washing_member.data.build_expanded_sentence_pool`

Why it is attractive:
- it remains a strong active data candidate from the triage registry
- it has substantial direct test pressure in the Iteration 2 sentence-pool workflow
- it could open a full three-batch data queue cleanly

Risk shape:
- medium
- broader lane rotation because it opens a new active data family before the current classification reporting lane is finished
- better suited as the next queue after the remaining active preliminary reporting surfaces are closed

## Decision

Chosen Queue V16 opener:
- `ai_washing_member.classification.publish_selected_preliminary_eval`

## Why this wins now

It gives Queue V16 a cleaner closeout shape:

1. `publish_selected_preliminary_eval`
2. `reconcile_preliminary_classification_report`
3. `classify_active_window_preliminary_restartable`

That finishes the remaining active preliminary classification/reporting lane before we rotate into the next active data lane.
