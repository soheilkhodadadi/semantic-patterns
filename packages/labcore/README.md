# Labcore Package Seed

## Status
- seeded target only
- not yet a standalone package directory with real `pyproject.toml`

## Purpose

`labcore` is the shared low-level infrastructure package for the lab.

It should own only:
- runtime helpers
- audit helpers
- security helpers
- transport helpers
- registry helpers
- later, shared contracts with clear cross-project reuse

It should not own:
- AI-washing semantics
- ERI scoring semantics
- AllocationLab decision logic
- project-specific analytics

## Current source pressure

The current live seed still exists in:
- `src/semantic_ai_washing/labcore/`

This placeholder directory marks the future package destination, not an immediate code move.

## Promotion rule

Promote code here only when:
- package identity is explicit
- build metadata plan is ready
- caller migration scope is bounded
- compatibility with the active AI-washing lane is preserved
