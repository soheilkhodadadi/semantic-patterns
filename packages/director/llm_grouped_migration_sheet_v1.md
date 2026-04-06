# LLM Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.llm`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.llm`

## Group 1: Direct director callers

Files:
- `src/semantic_ai_washing/director/core/planner.py`

Gate:
- `packages/director/tests/test_llm.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- package build smoke
- `git diff --check`

Status:
- complete
