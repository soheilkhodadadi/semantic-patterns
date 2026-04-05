# Director Package Seed

## Status
- seeded package shell
- real `pyproject.toml` present
- authoritative implementation still lives in legacy paths

## Purpose

`director` is the orchestration and control-discipline package for the lab.

It should own:
- control logic
- playbooks
- run/review structure
- coordination utilities that help manage work across projects

It should not become:
- a hidden home for all business logic
- a forced dependency for every project-specific decision
- a replacement for project members

## Current source pressure

The current live director stack still exists in:
- `director/`
- selected compatibility layers under `src/semantic_ai_washing/director/`

This placeholder directory marks the future package destination, not an immediate code relocation.

## Promotion rule

Promote code here only when:
- the director-owned scope is explicit
- the package boundary is cleaner than the current mixed layout
- the migration does not blur project ownership

See also:
- `packages/director/pyproject_seed_plan_v1.md`
- `packages/director/first_extraction_slice_v1.md`

First extracted package slice:
- `packages/director/src/semantic_director/schemas.py`
- `packages/director/src/semantic_director/__init__.py`

Migration trace:
- `docs/roadmap_v2/migration_round_g_director_schema_extraction_v1.md`
