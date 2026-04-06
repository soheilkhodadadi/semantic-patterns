# Batched Execution Queue V30

## Purpose

This queue starts after Queue V29 completed cleanly.

It is a bounded hygiene/polish queue for repo-root and shared workspace
navigation. The goal is to make the repo front door reflect the current lab
structure without reopening settled migration lanes.

## Planning assumptions

- keep hygiene separate from active authority migration
- improve navigation before adding any more late-stage queues
- prefer front-door clarity over archival/export polish

## Immediate execution queue

### Batch 1

Name:
- `hygiene.repo_root_frontdoor_refresh`

Why next:
- the repo `README.md` still mixes delivery context, migration context, and lab
  transition notes without a clear current entry order

Default gate:
- moved/reference scan where needed
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.shared_workspace_navigation_refresh`

Why next:
- `packages/README.md` and `docs/projects/README.md` should work as lane-level
  front doors now that package/project member docs are much cleaner

Default gate:
- front-door docs updated
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.repo_navigation_posture_refresh`

Why next:
- after the front-door docs change, the queue should close with an explicit
  posture note and a new checkpoint

Default gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`

Status:
- complete
