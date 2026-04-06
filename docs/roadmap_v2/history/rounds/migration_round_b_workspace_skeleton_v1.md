# Migration Round B Workspace Skeleton V1

## Purpose

This note records the first visible workspace skeleton for the package-centric end-state.

Round B is about landing zones, not code relocation.
The goal is to make the future structure obvious in the filesystem before deeper migrations begin.

## Outputs created in this round

Root landing zones:
- `packages/`
- `projects/`
- `shared/`

Seeded shared package placeholders:
- `packages/labcore/`
- `packages/director/`

Seeded project member placeholders:
- `projects/ai_washing/`
- `projects/eri/`
- `projects/allocationlab/`

Shared artifact placeholder lanes:
- `shared/manifests/`
- `shared/labels/`
- `shared/evaluation/`
- `shared/registry/`

## Round B rule

These directories are currently:
- visible landing zones
- orientation anchors
- migration targets

They are not yet:
- authoritative code destinations by default
- proof that broad code movement should start immediately
- justification for deleting legacy lanes

## Workspace member vs path dependency rule

Use a workspace member when:
- the unit is central to the lab
- the scope is stable enough to seed locally
- iterative development in this repo is expected
- shared tooling and review are helpful

Use a path dependency or staged external intake when:
- the unit still lives elsewhere first
- the boundary is still unstable
- confidentiality constraints dominate
- promotion into the workspace would be premature

## Why this round matters

Without visible landing zones, contributors keep defaulting to legacy paths.
This round reduces ambiguity without forcing risky moves.

## Bottom line

Round B makes the end-state tangible.
The next rounds can now seed real package/member identities and start bounded migrations into visible destinations.
