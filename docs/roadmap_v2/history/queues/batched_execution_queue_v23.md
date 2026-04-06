# Batched Execution Queue V23

## Purpose

This queue starts after Queue V22 completed cleanly.

It is the first script-deprecation hygiene follow-on. The goal is to reduce
registry and inventory ambiguity around six historical data utilities without
mixing deletion into the queue.

## Planning assumptions

- keep Protocol V2 discipline where applicable
- keep hygiene separate from active authority migration
- keep one bounded hygiene batch per commit
- update source-of-truth generator logic before publishing generated outputs
- do not delete or quarantine code surfaces in this queue

## Immediate execution queue

### Batch 1

Name:
- `hygiene.script_inventory_deprecation_rules`

Why next:
- the current generator still advertises six historical data utilities as
  canonical current entrypoints
- the source-of-truth rule should change before any snapshot or registry is
  republished

Default gate:
- targeted Ruff
- targeted `py_compile`
- focused script-inventory tests
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.script_registry_publish`

Why next:
- after the generator posture changes, the published snapshot and rendered
  registry should reflect the same deprecation posture

Default gate:
- regenerate inventory + registry from the package-owned task
- focused script-inventory tests
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.script_deprecation_posture_refresh`

Why next:
- late-stage navigation should say clearly that the six utilities are
  deprecation candidates, not current canonical workflow front doors

Default gate:
- queue/posture docs updated
- `git diff --check`

Status:
- complete
