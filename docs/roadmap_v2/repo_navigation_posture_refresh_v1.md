# Repo Navigation Posture Refresh V1

## Purpose

This note closes Queue V30 and records the intended navigation posture after the
repo-root and shared workspace front-door refresh.

## New default posture

Use these as the repo entry points:
- `README.md`
- `docs/roadmap_v2/current_state_navigation_v1.md`
- `packages/README.md`
- `docs/projects/README.md`

Use these as lane-specific fronts:
- `projects/ai_washing/README.md`
- `packages/director/README.md`
- `packages/labcore/README.md`
- `docs/projects/ai_washing/README.md`

## Why this is better

- the repo root now points to the current lab structure directly
- package and project-doc workspaces now read as navigation hubs
- contributors can distinguish live code lanes from public-safe doc lanes more
  quickly

## What did not change

- no code behavior changed
- no migration authority changed
- operational history remains under `docs/roadmap_v2/history/`

## Recommended posture after Queue V30

- keep using the repo root and workspace lane docs as the front door
- keep `roadmap_v2/history/` as the audit layer
- choose any next late-stage queue only if it offers clear leverage over simple
  momentum
