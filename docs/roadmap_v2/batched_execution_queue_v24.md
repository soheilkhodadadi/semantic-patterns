# Batched Execution Queue V24

## Purpose

This queue starts after Queue V23 completed cleanly.

It is the bounded legacy script-consumer cleanup follow-on. The goal is to
reduce the remaining ambiguity around the flat `src/data/*` shims for six
historical data utilities without deleting them.

## Planning assumptions

- keep Protocol V2 discipline where applicable
- keep hygiene separate from active authority migration
- keep one bounded hygiene batch per commit
- update the source-of-truth generator before publishing generated outputs
- do not delete or quarantine code surfaces in this queue

## Immediate execution queue

### Batch 1

Name:
- `hygiene.script_consumer_deprecation_rules`

Why next:
- the generator still treats the flat `src/data/*` shims as generic
  compatibility surfaces
- they should instead be marked explicitly as legacy consumers of
  script-deprecation candidates

Default gate:
- targeted Ruff
- targeted `py_compile`
- focused script-inventory tests
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.script_consumer_registry_publish`

Why next:
- once the source-of-truth rule changes, the published snapshot and rendered
  registry should reflect the refined consumer posture

Default gate:
- regenerate inventory + registry from package-owned functions
- focused script-inventory tests
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.script_consumer_posture_refresh`

Why next:
- the late-stage docs should say clearly that the flat `src/data/*` shims are
  compatibility consumers in a later deprecation lane, not front-door
  workflows

Default gate:
- posture docs updated
- `git diff --check`

Status:
- complete
