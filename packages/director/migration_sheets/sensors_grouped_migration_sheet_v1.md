# Director Sensors Grouped Migration Sheet V1

## Authority

Canonical authority:
- `semantic_director.sensors`

Legacy compatibility path:
- `semantic_ai_washing.director.core.sensors`

## Direct caller groups

### Group 1

Package caller pressure:
- `packages/director/src/semantic_director/readiness.py`
- `packages/director/tests/test_readiness.py`

### Group 2

Root director runtime caller pressure:
- `src/semantic_ai_washing/director/core/executor.py`
- `tests/test_director_core.py`

### Group 3

Direct sensor validation surface:
- `tests/test_director_sensors.py`
- `packages/director/tests/test_sensors.py`

### Deferred cross-lane edge

Leave on the compatibility shim for now:
- `src/semantic_ai_washing/labeling/audit_sentence_integrity.py`

Reason:
- it is real and relevant, but it belongs to an `ai_washing` follow-on round,
  not this `director` package batch
