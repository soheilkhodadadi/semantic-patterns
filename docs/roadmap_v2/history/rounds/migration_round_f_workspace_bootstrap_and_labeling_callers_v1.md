# Migration Round F: Workspace Bootstrap and Labeling Callers V1

## Purpose

This round makes workspace packages part of the canonical repo environment and
uses that support to migrate the first real direct caller family from legacy
`semantic_ai_washing.labcore.*` imports to canonical `semantic_labcore.*`
imports.

## What changed

Bootstrap now installs the seeded workspace packages, and repo-owned command
paths now explicitly treat them as part of the active environment through a
workspace `PYTHONPATH` profile:
- `semantic_ai_washing`
- `semantic_labcore`
- `semantic_director`

The first direct caller family now imports from `semantic_labcore` directly:
- `src/semantic_ai_washing/labeling/assistive_prelabel_batch.py`
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `src/semantic_ai_washing/labeling/score_prelabel_sheet.py`

## Why this environment step came first

Direct caller migration is only honest if the active repo environment can import
workspace packages without ad hoc `PYTHONPATH` tricks.

That makes bootstrap support part of the migration itself, not just a
developer-convenience tweak.

## Why the labeling family was first

The labeling assistive bundle is a good first direct caller family because it is:
- already low in blast radius
- already covered by focused regression tests
- already logically downstream of the extracted `labcore` helpers
- project-specific enough to prove the package path in real code

## Acceptance gate

This round is accepted when:
- `make bootstrap` completes with workspace package installs
- `make doctor` confirms all three package imports through the repo workspace path profile
- focused labeling regressions still pass
- no legacy compatibility tests regress

## Bottom line

This is the first round where canonical workspace package imports are used by
real project callers rather than only package-local tests and compatibility
shims.
