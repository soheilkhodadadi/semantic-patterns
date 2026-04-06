# Labcore Package Seed

## Status
- seeded package shell
- real `pyproject.toml` present
- canonical package modules now active for:
  - `runtime.py`
  - `audit.py`
  - `security.py`
  - `openai_responses.py`
  - `registry/`
- compatibility shims remain in legacy paths while caller migration continues

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

Those legacy modules now increasingly act as compatibility shims.
The package path under:
- `packages/labcore/src/semantic_labcore/`

is becoming the canonical implementation lane.

## Promotion rule

Promote code here only when:
- package identity is explicit
- build metadata plan is ready
- caller migration scope is bounded
- compatibility with the active AI-washing lane is preserved

See also:
- `packages/labcore/pyproject_seed_plan_v1.md`
- `docs/lab/control_plane/labcore_extraction_protocol_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_e_labcore_runtime_extraction_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_e_labcore_support_modules_extraction_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_e_labcore_registry_extraction_v1.md`
