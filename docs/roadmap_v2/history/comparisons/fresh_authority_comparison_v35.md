# Fresh Authority Comparison V35

## Purpose

Choose whether the next bounded late-stage queue should execute the reviewed
repo-root cleanup or switch back to roadmap-history archive/export prep.

## Candidates

### Option A
- `hygiene.root_old_requirements_cleanup`

### Option B
- `hygiene.roadmap_history_archive_export_prep`

## Comparison

### Root old-requirements cleanup

Pros:
- directly executes the one retire candidate surfaced by Queue V31
- narrow enough to stay low-risk and easy to validate
- removes a tracked root artifact that no longer reflects the current `.venv`
  or packaging posture

Cons:
- very small queue
- mostly symbolic unless the posture docs are refreshed with it

### Roadmap history archive/export prep

Pros:
- still potentially useful later for long-term documentation management
- would continue to formalize the audit layer

Cons:
- lower leverage than the now-explicit root cleanup
- the history layer is already usable enough for current work
- would ignore the clearest safe follow-on identified by Queue V31

## Decision

Choose:
- `hygiene.root_old_requirements_cleanup`

## Why

Queue V31 did the work of narrowing the cleanup scope responsibly. The honest
next step is to execute that exact narrow cleanup rather than reopen a lower-
leverage history-prep lane.
