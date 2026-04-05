# Director Package Seed

## Status
- seeded target only
- not yet a standalone package directory with real `pyproject.toml`

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
