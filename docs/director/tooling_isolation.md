# Tooling Isolation

External skill tooling must not mutate the repo runtime.

## Atlas Rule
- Atlas is an external tool.
- Atlas must run outside the repo `.venv`.
- `uv run` from the repo root is forbidden for Atlas.
- Director uses `scripts/atlas_isolated.sh` to run Atlas metadata calls in a temporary working directory.

## Repo `.venv` Guardrail
Director doctor checks:
- `.venv/bin/python` exists
- `.venv/bin/python -m pip` works
- `.venv/pyvenv.cfg` still matches the expected project interpreter family

If Atlas or another tool rewrites `.venv`, repair the environment before continuing:
```bash
make bootstrap
make doctor
```

## Policy Source
Canonical tooling policy file:
- `director/config/tooling_policy.yaml`

This file records:
- required Atlas runner path
- wrapper path
- repo-root `uv run` prohibition
- expected repo `.venv` interpreter metadata
