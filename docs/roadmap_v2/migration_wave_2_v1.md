# Migration Wave 2 V1

## Purpose

Wave 2 creates the lane structure and first authoritative destinations needed for the lab to operate like a multi-program repo.

## Wave objective

Establish tracked scaffolding for:
- lab documentation
- project documentation
- registry reporting
- project report lanes
- project and shared output destinations
- project and shared processed-data destinations

## Scope

Wave 2 covers:
- `docs/lab/` scaffolding
- `docs/projects/` scaffolding
- `reports/registry/` scaffolding and the first artifact registry
- `reports/projects/` scaffolding
- `data/manifests/` and processed-data destination notes
- `output/doc/shared/`, `output/doc/projects/...`
- `output/figures/shared/`, `output/figures/projects/...`

Wave 2 does not cover:
- large code moves
- package renaming
- bulk migration of existing outputs
- deletion of legacy lanes that are still in use

## Deliverables

Required artifacts:
- `docs/lab/**/README.md`
- `docs/projects/**/README.md`
- `reports/registry/artifact_registry_v1.md`
- `reports/projects/**/README.md`
- `data/manifests/README.md`
- `data/processed/shared/README.md`
- `data/processed/projects/**/README.md`
- `output/doc/shared/README.md`
- `output/doc/projects/**/README.md`
- `output/figures/shared/README.md`
- `output/figures/projects/**/README.md`

## Acceptance gate

Wave 2 is complete when:
- the lab has stable tracked scaffolding for shared and project lanes
- new artifacts have named authoritative landing zones
- existing legacy lanes remain undisturbed unless a replacement map exists
- registry-style reporting has a dedicated home

## Why this wave matters

Without Wave 2, collaborators will keep inventing new landing zones.
That is exactly how the repo drifts back into mixed-purpose clutter.

## Recommended next move after Wave 2

Proceed to Wave 3 only after validating that:
- the new lane structure is understandable
- collaborators can place new artifacts without guessing
- active AI-washing work is not disrupted
