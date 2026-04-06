# Migration Round AU: Director LLM Seed V1

## Scope

Batch 3 from Queue V9.

Authority:
- `semantic_director.llm`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct `director` planner caller onto the new authority

## Pre-Scan Result

The `llm` boundary stayed clean enough to auto-run under Queue V9.

What made it clean:
- it sits downstream of canonical `semantic_director.cost`
- direct caller pressure is concentrated in the planner surface
- shared transport/runtime/schema dependencies already have canonical package surfaces
- Atlas-adjacent adapter boundaries remain outside this round

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_llm.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/llm.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/llm.py`

Migrated callers:
- `src/semantic_ai_washing/director/core/planner.py`

New package-local test:
- `packages/director/tests/test_llm.py`
