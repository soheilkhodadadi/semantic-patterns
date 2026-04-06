# Batched Execution Queue V25

## Purpose

This queue starts after Queue V24 completed cleanly.

It is a tiny `director` utility boundary cleanup queue. The goal is to replace
root compatibility imports with direct canonical imports where equivalents
already exist, without touching intentionally `director`-specific shims.

## Planning assumptions

- keep Protocol V2 discipline where applicable
- keep one bounded authority per commit
- only change imports with direct canonical equivalents
- do not force cleanup of `director`-specific wrapper behavior just to reduce
  import count

## Immediate execution queue

### Batch 1

Name:
- `semantic_director.runtime_schema_boundary_cleanup`

Why next:
- several package-owned modules still import pure runtime helpers from
  `semantic_ai_washing.director.core.utils`
- one package-owned module still imports schemas through the root compatibility
  surface

Default gate:
- `make doctor`
- targeted Ruff
- targeted `py_compile`
- focused package and root `director` tests
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `semantic_director.responses_transport_boundary_cleanup`

Why next:
- `semantic_director.api_bootstrap` still imports the responses transport
  through the root compatibility surface even though the canonical shared
  transport now lives in `semantic_labcore`

Default gate:
- targeted Ruff
- targeted `py_compile`
- focused api-bootstrap and related director tests
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `semantic_director.utility_boundary_posture_refresh`

Why next:
- after the direct-equivalent import cleanup lands, the queue should close with
  an explicit note about what remains intentionally deferred

Default gate:
- queue/posture docs updated
- `git diff --check`

Status:
- complete
