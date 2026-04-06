# Migration Round DF

## Queue

Queue V30

## Batch

`hygiene.shared_workspace_navigation_refresh`

## Purpose

Refresh the shared workspace lane docs so `packages/` and `docs/projects/`
work as clear navigation hubs after the late-stage restructure passes.

## Expected surfaces

- `packages/README.md`
- `docs/projects/README.md`
- `docs/projects/ai_washing/README.md`

## Gate

Required gate:
- lane-level front-door docs updated
- current canonical entry points are explicit
- `git diff --check`

## Outcome

Completed:
- rewrote `packages/README.md` into a lane-level package workspace guide
- rewrote `docs/projects/README.md` into a lane-level project-docs guide
- clarified `docs/projects/ai_washing/README.md` as the public-safe docs lane
  rather than the live project-member front door

Validation:
- lane-level entry docs now point to current canonical project/package fronts
- `git diff --check` passed
