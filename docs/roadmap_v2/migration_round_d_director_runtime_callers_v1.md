# Migration Round D: Director Runtime Caller Slice V1

## Purpose

This note records the next bounded `labcore` adoption slice after the external `labeling` family migration.

## Migration slice

This round migrates a single low-risk `director` caller:
- `src/semantic_ai_washing/director/core/render.py`

## What changed

`render.py` now imports the generic runtime helpers directly from:
- `semantic_ai_washing.labcore.runtime`

Switched helpers:
- `now_utc_iso`
- `sha256_file`

## Why this slice was chosen

This is intentionally narrow:
- it depends only on generic runtime helpers
- it is covered by focused `director` regression tests
- it proves additional `labcore` adoption without widening scope into planner, executor, or package relocation

## What did not change

This slice does **not**:
- relocate `director` code into `packages/director/`
- change `director` planning or execution logic
- alter the compatibility shims in `semantic_ai_washing.director.core.utils`

## Acceptance gate

This slice is accepted when:
- `render.py` imports runtime helpers from `labcore`
- the focused `director` regression suite still passes
- no broader authority shift is implied

## Bottom line

This is a deliberate small `director`-internal adoption step, not a broad `director` migration.
