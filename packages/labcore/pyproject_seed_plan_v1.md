# Labcore Pyproject Seed Plan V1

## Purpose

This note defines the first packaging plan for the future `labcore` shared package.

It does not create a real `pyproject.toml` yet.
It defines the identity, scope, and migration guardrails needed before the real package metadata lands.

## Recommendation

### Distribution name
- `semantic-labcore`

### Import package name
- `semantic_labcore`

### Why this pairing
- avoids the generic and collision-prone import name `labcore`
- separates the future shared package from the current project-specific import path `semantic_ai_washing.labcore`
- stays readable if the package is later copied out or published

## Proposed future structure

```text
packages/labcore/
|-- pyproject.toml
|-- README.md
|-- src/
|   `-- semantic_labcore/
`-- tests/
```

## Initial owned scope

The first real package should own only the low-level shared helpers that already passed the Wave 3 filter:
- registry helpers
- runtime helpers
- audit helpers
- security helpers
- OpenAI Responses transport helpers

Expected source pressure from current paths:
- `src/semantic_ai_washing/labcore/registry/`
- `src/semantic_ai_washing/labcore/runtime.py`
- `src/semantic_ai_washing/labcore/audit.py`
- `src/semantic_ai_washing/labcore/security.py`
- `src/semantic_ai_washing/labcore/openai_responses.py`

## Explicit non-scope

Do not seed these into `labcore` yet:
- AI-washing analytical logic
- project scoring semantics
- delivery logic that is still paper-specific
- shared contracts that are not yet proven in code

## Dependency direction

`labcore` should be near the bottom of the dependency stack.

Allowed outgoing dependencies:
- Python standard library
- small external infrastructure dependencies only if they are truly cross-project

Allowed incoming dependents:
- `director`
- future project members

Disallowed pattern:
- `labcore` importing project-member internals

## Build-backend recommendation

For the first real package seed, prefer:
- `setuptools.build_meta`

Why:
- lowest surprise relative to the current repo
- compatible with a staged migration
- enough for the first shared package seed

We can revisit a different backend later if workspace complexity truly demands it.

## Initial pyproject shape

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "semantic-labcore"
version = "0.1.0"
description = "Shared low-level infrastructure helpers for the semantic-patterns lab"
readme = "README.md"
requires-python = ">=3.11"
```

## Preconditions before making this real

Before adding a real `pyproject.toml` here:
- package identity is accepted
- the current `semantic_ai_washing.labcore` callers are mapped
- first bounded direct-caller migration plan exists
- compatibility-shim strategy remains explicit

## Acceptance target

This package should aim to reach:
- `seeded` first
- `buildable` only after one bounded caller migration family is ready

## Bottom line

`labcore` is the first true shared package candidate.
Its package identity should be explicit, low in the dependency graph, and small in scope.
