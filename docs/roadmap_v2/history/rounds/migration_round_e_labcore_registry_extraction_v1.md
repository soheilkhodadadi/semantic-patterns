# Migration Round E: Labcore Registry Extraction V1

## Purpose

This note records the registry extraction round that completes the first package-authoritative `labcore` wave.

## What changed

The canonical registry implementation now exists in:
- `packages/labcore/src/semantic_labcore/registry/__init__.py`
- `packages/labcore/src/semantic_labcore/registry/lanes.py`
- `packages/labcore/src/semantic_labcore/registry/adapters.py`

The legacy import paths:
- `src/semantic_ai_washing/labcore/registry/__init__.py`
- `src/semantic_ai_washing/labcore/registry/lanes.py`
- `src/semantic_ai_washing/labcore/registry/adapters.py`

are now compatibility shims that re-export from `semantic_labcore.registry`.

## Why registry was last in the initial wave

`registry/` sits slightly above the lower-level helpers because it depends on package structure and lane decisions.
It is still safe to extract now because:
- its module boundaries are coherent
- its tests are already focused
- it only depends on generic path and metadata logic
- it does not pull in project analytics

## Acceptance gate

This extraction round is accepted when:
- package-local registry tests pass
- root compatibility tests still pass
- package build still passes
- root `semantic_ai_washing.labcore` exports still resolve cleanly

## Bottom line

The initial `labcore` extraction wave is complete.
The package path is now canonical for the low-level helper family and registry layer, while legacy paths remain as compatibility shims.
