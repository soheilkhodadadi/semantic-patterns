# Director Playbooks Grouped Migration Sheet V1

## Authority

Canonical authority:
- `semantic_director.playbooks`

Legacy compatibility path:
- `semantic_ai_washing.director.core.playbooks`

## Direct caller groups

### Group 1

Runtime caller pressure:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/review.py`

### Group 2

Validation surface:
- `tests/test_director_playbooks.py`
- `packages/director/tests/test_playbooks.py`
- `tests/test_director_cli.py`
