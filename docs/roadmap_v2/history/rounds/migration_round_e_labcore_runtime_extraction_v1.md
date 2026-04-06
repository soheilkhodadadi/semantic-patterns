# Migration Round E: Labcore Runtime Extraction V1

## Purpose

This note records the first true package extraction round for `labcore`.

## What changed

The canonical implementation of runtime helpers now exists in:
- `packages/labcore/src/semantic_labcore/runtime.py`

The legacy import path:
- `src/semantic_ai_washing/labcore/runtime.py`

is now a compatibility shim that re-exports from `semantic_labcore.runtime`.

## Why runtime was first

`runtime.py` is the best first extraction unit because it is:
- genuinely generic
- already reused across multiple caller families
- small enough to validate directly
- low in the dependency graph

## Compatibility approach

Because the workspace package is not yet wired into the root repo environment,
the legacy shim temporarily adds:
- `packages/labcore/src/`

to the import path before re-exporting from `semantic_labcore.runtime`.

This keeps active repo imports working while the shared package becomes canonical.

## Acceptance gate

This extraction round is accepted when:
- package-local runtime tests pass
- root compatibility tests still pass
- caller regression bundles still pass
- package build still passes

## Bottom line

This is the first real package-authoritative extraction in the lab migration.
