# Director Pyproject Seed Plan V1

## Purpose

This note defines the first packaging plan for the future `director` shared package.

It does not create a real `pyproject.toml` yet.
It defines the identity, scope, and guardrails needed before package metadata becomes real.

## Recommendation

### Distribution name
- `semantic-director`

### Import package name
- `semantic_director`

### Why this pairing
- avoids a bare `director` package name that is too generic
- separates the future shared package from the current mixed root artifact lane `director/`
- leaves room for the root `director/` lane to remain an artifact and control-plane store even after package extraction starts

## Proposed future structure

```text
packages/director/
|-- pyproject.toml
|-- README.md
|-- src/
|   `-- semantic_director/
`-- tests/
```

## Initial owned scope

The future package should eventually own the code-side orchestration layer, including:
- CLI entry points
- schemas and policies that are package-owned
- planning, review, render, readiness, and task-graph code
- adapters and tasks that genuinely belong to the orchestration system

Current source pressure comes from:
- `src/semantic_ai_washing/director/`

## Important distinction

The root lane:
- `director/`

currently mixes artifact storage and configuration with the director system identity.

Round C should not collapse those into one thing.
A likely future split is:
- `packages/director/` for code
- root `director/` retained or renamed later for director-owned artifacts and operational records

## Dependency direction

Allowed outgoing dependencies:
- `semantic_labcore` once that package is real
- explicit external dependencies required by the orchestration layer

Allowed incoming dependents:
- project members that need orchestration entry points
- operator workflows and scripts

Disallowed pattern:
- forcing every project-specific semantic decision to depend on `director`

## Build-backend recommendation

For the first real package seed, prefer:
- `setuptools.build_meta`

Why:
- consistent with staged migration
- easier to introduce without changing the whole repo at once

## Initial pyproject shape

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "semantic-director"
version = "0.1.0"
description = "Orchestration and control-plane package for the semantic-patterns lab"
readme = "README.md"
requires-python = ">=3.11"
```

## Preconditions before making this real

Before adding a real `pyproject.toml` here:
- code scope is separated from root `director/` artifact lanes
- package-owned modules are explicitly named
- dependency on `labcore` is clarified
- at least one bounded extraction path from `src/semantic_ai_washing/director/` is mapped

## Acceptance target

This package should aim to reach:
- `seeded` after scope and package identity are accepted
- `buildable` only after code-vs-artifact separation is clearer

## Bottom line

`director` is a real shared package candidate, but it is less clean than `labcore` right now.
It should be seeded deliberately and only after the code/artifact split is explicit.
