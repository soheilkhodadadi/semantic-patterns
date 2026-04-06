# Director Package

## Status
- package-owned code is real
- the package boundary is effectively complete for the current restructure goal
- remaining work is now polish and hygiene, not foundational extraction

## Purpose

`director` is the shared orchestration and control-discipline package for the
lab.

It owns:
- control logic
- review and decision structure
- planning and execution coordination
- playbooks, validation, and control-plane evidence tooling

It should not become:
- a hidden home for project-specific business logic
- a replacement for project members
- a generic dumping ground for unrelated utilities

## Canonical locations

Package code:
- `packages/director/src/semantic_director/`

Package tests:
- `packages/director/tests/`

Migration sheets:
- `packages/director/migration_sheets/README.md`

Compatibility shims still exist in:
- `src/semantic_ai_washing/director/`

## Current canonical families

### Control core
- `schemas.py`
- `roadmap_model.py`
- `task_graph.py`
- `state.py`
- `decision.py`
- `planner.py`
- `review.py`
- `optimizer.py`
- `executor.py`
- `gates.py`
- `readiness.py`

### Entry and runtime surface
- `cli.py`
- `__main__.py`
- `config.py`
- `branching.py`
- `security.py`
- `runtime.py`

### Evidence, rendering, and governance
- `render.py`
- `documents.py`
- `iteration_log.py`
- `snapshot.py`
- `atlas.py`
- `api_assistive.py`
- `api_bootstrap.py`
- `cost.py`
- `llm.py`
- `validation_assets.py`
- `script_inventory.py`
- `playbooks.py`

## Read this folder in this order

1. `packages/director/src/semantic_director/`
2. `packages/director/migration_sheets/README.md`
3. `docs/roadmap_v2/restructure_progress_checkpoint_v19.md`
4. `docs/roadmap_v2/current_state_navigation_v1.md`

## Planning documents that still matter

- `packages/director/pyproject_seed_plan_v1.md`
- `packages/director/first_extraction_slice_v1.md`

These are background/reference notes now, not the package front door.

## Current posture

- the active `director` runtime, adapter, wrapper, and governance lanes are now
  canonical under `semantic_director`
- package-internal dependence on root `semantic_ai_washing.director.*`
  compatibility imports is now closed
- remaining work is optional export polish, documentation polish, and separate
  hygiene
- any future queue in this lane should be chosen deliberately for polish, not to
  recreate migration momentum for its own sake
