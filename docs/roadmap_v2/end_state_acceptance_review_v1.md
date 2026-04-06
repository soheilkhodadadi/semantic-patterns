# End-State Acceptance Review V1

## Purpose

Evaluate the current repo state against the clean final lab structure goal and
classify what remains as required work versus optional polish.

## Acceptance lens

The clean final lab structure goal means:
- canonical shared code lives in `packages/`
- canonical project-member code lives in `projects/`
- compatibility/history layers are explicit rather than confused with front
  doors
- repo/navigation docs point contributors to the current structure clearly
- remaining legacy or historical surfaces do not dominate the visible repo

## Current state against that goal

### Shared packages

Status:
- accepted

Why:
- `labcore` is effectively complete for its intended scope
- `director` is effectively complete for the current restructure goal
- package front doors and migration-sheet lanes are explicit

### Project member lane

Status:
- accepted for active workflow scope

Why:
- `ai_washing_member` owns the active labeling, classification, and data lanes
- remaining root-owned `ai_washing` surfaces are mostly wrappers or historical
  utilities rather than active forward-migration pressure

### Repo navigation and front-door clarity

Status:
- accepted

Why:
- repo root, package workspace, project-doc workspace, and roadmap front doors
  are now all explicit
- history layers are bucketed and de-emphasized correctly

### History/audit retention

Status:
- accepted with conditional later export

Why:
- `docs/roadmap_v2/history/` now behaves as an in-repo audit archive
- later export is optional and only justified if the history layer becomes a
  real repo-use burden

## Required remaining work

None identified as restructure-critical.

## Optional remaining polish

These are optional, not required for the clean final lab structure goal:
- later archive/export of older roadmap history, if repo-use pressure warrants
  it
- future retirement of compatibility shims only when a separate bounded pass is
  justified
- future polish of low-signal placeholder lanes such as `models/` or
  `references/` if they ever become confusing in practice

## Acceptance decision

Decision:
- the repo now effectively satisfies the clean final lab structure goal

Interpretation:
- more queues are optional polish, not required restructure work
- future queues should open only for a specific new problem, not to continue the
  current migration cadence by inertia
