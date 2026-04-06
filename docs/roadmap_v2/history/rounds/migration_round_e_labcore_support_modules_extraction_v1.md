# Migration Round E: Labcore Support Modules Extraction V1

## Purpose

This note records the next package-authoritative extraction round for `labcore`.

## What changed

The canonical implementations of these support modules now exist in:
- `packages/labcore/src/semantic_labcore/audit.py`
- `packages/labcore/src/semantic_labcore/security.py`
- `packages/labcore/src/semantic_labcore/openai_responses.py`

The legacy import paths:
- `src/semantic_ai_washing/labcore/audit.py`
- `src/semantic_ai_washing/labcore/security.py`
- `src/semantic_ai_washing/labcore/openai_responses.py`

are now compatibility shims that re-export from `semantic_labcore`.

## Why these modules were grouped

These three modules are a good grouped extraction round because they are:
- already isolated from project-specific logic
- already covered by focused tests
- already wrapped by `director` compatibility shims
- small enough to validate with package-local and root-level parity checks

## Compatibility approach

As with `runtime.py`, each legacy shim temporarily adds:
- `packages/labcore/src/`

to the import path before re-exporting from `semantic_labcore`.

This keeps active repo imports working while the shared package becomes canonical.

## Acceptance gate

This extraction round is accepted when:
- package-local audit, security, and responses tests pass
- root compatibility tests still pass
- director-facing tests still pass
- package build still passes

## Bottom line

`labcore` now has canonical package implementations for the full low-level helper set that was targeted in the initial extraction wave.
