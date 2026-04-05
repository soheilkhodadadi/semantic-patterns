# Migration Round D: Package Shell Seeding V1

## Purpose

This note records the first real package-shell seeding step for the new workspace model.

## What changed

Real package shells now exist for:
- `packages/labcore/`
- `packages/director/`

Each shell now has:
- a real `pyproject.toml`
- a real `src/` package namespace
- a minimal import smoke test

## Important constraint

These are packaging anchors, not code relocations.
They do **not** yet mean that authoritative implementation has moved out of:
- `src/semantic_ai_washing/labcore/`
- `src/semantic_ai_washing/director/`

## Why this is useful

This gives the workspace model a real packaging surface early.
It lets us validate structure and package identity before heavier code migration begins.

## Acceptance gate

This slice is accepted when:
- both package shells are structurally valid
- import smoke tests pass
- build smoke tests pass
- no code authority is misrepresented

## Bottom line

The repo now has real package shells for the first two shared package candidates.
