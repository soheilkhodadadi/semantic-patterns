# Batched Execution Queue V27

## Purpose

This queue starts after Queue V26 completed cleanly.

It is a bounded hygiene/polish queue for `packages/director`. The goal is to
consolidate top-level migration sheets, simplify package navigation, and close
with an explicit posture update without reopening code-boundary migration.

## Planning assumptions

- keep hygiene separate from active authority migration
- do not reopen `director` boundary work
- prefer navigation clarity over more top-level operational clutter

## Immediate execution queue

### Batch 1

Name:
- `hygiene.director_migration_sheet_consolidation`

Why next:
- `packages/director/` still has many grouped migration sheets sitting at the
  top level
- those sheets are useful, but they should not dominate the package front door

Default gate:
- direct-reference scan for moved files
- `git diff --check`

Status:
- pending

### Batch 2

Name:
- `hygiene.director_readme_frontdoor_polish`

Why next:
- after the migration sheets move, the package README should become a true
  front-door document instead of an append-only ledger

Default gate:
- front-door docs updated
- `git diff --check`

Status:
- pending

### Batch 3

Name:
- `hygiene.director_navigation_posture_refresh`

Why next:
- the queue should close with an explicit note about what changed and how
  `director` should be navigated now

Default gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`

Status:
- pending
