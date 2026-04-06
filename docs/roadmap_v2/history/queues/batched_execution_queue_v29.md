# Batched Execution Queue V29

## Purpose

This queue starts after Queue V28 completed cleanly.

It is a bounded hygiene/polish queue for `docs/roadmap_v2`. The goal is to
bucket operational-history artifacts into dedicated subfolders, reduce
top-level clutter, and refresh the front-door docs to match the new structure.

## Planning assumptions

- keep hygiene separate from active authority migration
- do not rewrite historical content, only re-home it
- prefer mechanical path updates over editorial churn

## Immediate execution queue

### Batch 1

Name:
- `hygiene.roadmap_history_bucket_seed`

Why next:
- queues, fresh-authority comparisons, and progress checkpoints are already
  recognized as history classes and can be re-homed mechanically

Default gate:
- direct-reference scan for moved files
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.roadmap_round_history_bucket`

Why next:
- migration rounds are the largest remaining flat history class and should move
  after the bucket structure is already in place

Default gate:
- direct-reference scan for moved files
- `git diff --check`

Status:
- pending

### Batch 3

Name:
- `hygiene.roadmap_history_navigation_refresh`

Why next:
- after the history files move, the front-door docs should explicitly describe
  the new structure and latest checkpoint location

Default gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`

Status:
- pending
