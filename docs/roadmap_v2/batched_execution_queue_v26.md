# Batched Execution Queue V26

## Purpose

This queue starts after Queue V25 completed cleanly.

It is a bounded `director` wrapper-normalization queue. The goal is to make the
two remaining intentionally deferred `director` compatibility contracts
package-owned on purpose, without opening a broader runtime or hygiene wave.

## Planning assumptions

- keep Protocol V2 discipline where applicable
- keep one bounded authority per commit
- only normalize the two explicit wrapper contracts identified after Queue V25
- do not reopen generic helper migration just to reduce import count

## Immediate execution queue

### Batch 1

Name:
- `semantic_director.security_wrapper_normalization`

Why next:
- `semantic_director.cli` still depends on the root compatibility security shim
- the director-facing OpenAI key validation contract is now small and stable
  enough to become package-owned explicitly

Default gate:
- `make doctor`
- targeted Ruff
- targeted `py_compile`
- focused package and root security/cli tests
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `semantic_director.runtime_wrapper_normalization`

Why next:
- `semantic_director.gates` still depends on the root compatibility
  `run_command` wrapper
- the director-specific timeout wording contract is now small and stable enough
  to become package-owned explicitly

Default gate:
- targeted Ruff
- targeted `py_compile`
- focused package and root runtime/gates tests
- `git diff --check`

Status:
- pending

### Batch 3

Name:
- `semantic_director.wrapper_normalization_posture_refresh`

Why next:
- after the two wrapper contracts become package-owned, the queue should close
  with an explicit note that the remaining `director` package pressure is now
  mostly hygiene and optional polish

Default gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`

Status:
- pending
