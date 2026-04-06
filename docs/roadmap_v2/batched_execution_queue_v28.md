# Batched Execution Queue V28

## Purpose

This queue starts after Queue V27 completed cleanly.

It is a bounded hygiene/polish queue for `projects/ai_washing`. The goal is to
consolidate older planning notes, simplify the project-member front door, and
close with an explicit navigation/posture refresh.

## Planning assumptions

- keep hygiene separate from active authority migration
- do not reopen `ai_washing` migration waves that are already closed
- prefer front-door clarity over a larger archival/history project

## Immediate execution queue

### Batch 1

Name:
- `hygiene.ai_washing_planning_note_consolidation`

Why next:
- `projects/ai_washing/` still has several older planning/reference notes at
  the top level
- those notes still matter, but they should not compete with the current
  front-door docs

Default gate:
- direct-reference scan for moved files
- `git diff --check`

Status:
- pending

### Batch 2

Name:
- `hygiene.ai_washing_readme_frontdoor_polish`

Why next:
- after the planning notes move, the project README should point cleanly to the
  new note folder and current queue/checkpoint anchors

Default gate:
- front-door docs updated
- `git diff --check`

Status:
- pending

### Batch 3

Name:
- `hygiene.ai_washing_navigation_posture_refresh`

Why next:
- the queue should close with an explicit note about how the project member
  should be navigated now

Default gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`

Status:
- pending
