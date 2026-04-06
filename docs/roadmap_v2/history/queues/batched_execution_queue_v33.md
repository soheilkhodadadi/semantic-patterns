# Batched Execution Queue V33

## Purpose

This queue starts after Queue V32 completed cleanly.

It is a bounded hygiene/polish queue for roadmap-history archive/export prep.
The goal is to define how the history layer should be retained, exported, or
later archived without reopening another physical re-bucketing pass.

## Planning assumptions

- keep hygiene separate from active authority migration
- define archive/export posture before any later export action
- prefer classification and indexing over moving files again

## Immediate execution queue

### Batch 1

Name:
- `hygiene.roadmap_history_archive_export_review`

Why next:
- `docs/roadmap_v2/history/` is now large enough that its long-term retention
  posture should be explicit

Default gate:
- retention/export note created
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.roadmap_history_archive_export_posture_refresh`

Why next:
- after the review, the roadmap navigation docs should explicitly state what
  stays in-repo and what a later export pass would mean

Default gate:
- posture docs updated
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.roadmap_history_archive_export_checkpoint`

Why next:
- the queue should close with an explicit statement about whether any later
  archive/export queue is still needed

Default gate:
- queue/checkpoint docs updated
- `git diff --check`

Status:
- pending
