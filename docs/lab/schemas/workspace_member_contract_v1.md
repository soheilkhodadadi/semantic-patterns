# Workspace Member Contract V1

## Purpose

This note defines the minimum contract for any future shared package or project member that should be absorbable into the lab with low friction and exportable later with low surgery.

This contract is intentionally stricter than an ad hoc folder convention.

## Applies to

Shared packages:
- `packages/labcore`
- `packages/director`
- later `packages/labdelivery` only if reuse proves real

Project members:
- `projects/ai_washing`
- `projects/eri`
- `projects/allocationlab`

## Minimum structure

A member or package should eventually have, at minimum:
- `pyproject.toml`
- `README.md`
- `src/`
- `tests/`

Project members should also expect:
- `docs/`
- `configs/`
- `reports/`
- `output/`

The structure should stay simple and map clearly onto the package hierarchy.

## Required metadata expectations

### 1. Packaging anchor
- a real or planned `pyproject.toml`
- explicit `[build-system]`
- explicit `[project]` metadata when the member is buildable

Reason:
- current PyPA guidance treats `[build-system]` as the required packaging anchor
- standard metadata in `[project]` makes member identity and exportability more durable

### 2. Package identity
- one clear package name
- one clear ownership boundary
- no ambiguous overlap with another member's package identity

### 3. Dependency declaration
- explicit dependencies
- explicit note whether a relationship is:
  - workspace member dependency
  - path dependency
  - still legacy and not yet promoted

### 4. Local authority
- member README states what is authoritative inside that member
- control-plane docs do not replace local member ownership docs

## Boundary rules

### Rule A. No deep cross-member imports
A member should not import another member's private internals as an informal shortcut.

### Rule B. Shared logic must earn promotion
Logic moves into shared packages only when reuse is durable and the contract is stable.

### Rule C. Project semantics stay with the project
Taxonomy, scoring semantics, corpus rules, and downstream interpretation stay in the project member unless there is a strong reason otherwise.

## Intake paths

A contribution from another repo should be absorbable in one of three ways:
1. as a new workspace member
2. as a path dependency pending promotion
3. as a private-local member where confidentiality requires it

If a contribution cannot fit one of these paths cleanly, the intake design is weak.

## Export paths

A member is in a good long-term shape when it can plausibly be:
- built as a package
- copied to a new repo with limited path edits
- shared with a collaborator or client without dragging unrelated lab internals with it

## Acceptance checks

### Structure check
- member/package has the minimum expected directories
- package hierarchy matches directory hierarchy closely

### Metadata check
- `pyproject.toml` exists or has an approved draft plan
- build backend choice is explicit

### Dependency check
- dependency direction is documented
- no hidden dependency on another member's private internals

### Validation check
- targeted tests exist or have an explicit TODO path
- lint/format scope is localizable
- packaging/build readiness is testable once the member is declared buildable

Suggested command profile when a member becomes mature enough:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `pytest`
- `uv build --package <name> --no-sources` or `python -m build <path>`
- `uv sync --package <name>` once the workspace metadata is real

### Ownership check
- README states scope and authority
- mapping note states what remains legacy vs member-owned during transition

## Standards basis

This contract aligns with current public guidance around:
- `pyproject.toml` as the packaging anchor
- standard `src/` layout
- per-package/per-project `tests/`
- workspace members with their own metadata
- path dependencies when looser coupling is preferable
- build validation before calling a member export-ready

Key public references:
- `uv` workspaces:
  - https://docs.astral.sh/uv/concepts/projects/workspaces/
- `uv` package builds:
  - https://docs.astral.sh/uv/guides/package/
- PyPA `pyproject.toml` guidance:
  - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- PyPA packaging tutorial:
  - https://packaging.python.org/en/latest/tutorials/packaging-projects/
- setuptools package discovery and `src/` layout guidance:
  - https://setuptools.pypa.io/en/stable/userguide/package_discovery.html

## Bottom line

A workspace member is not just a folder.
It is a coherent unit with:
- packaging identity
- clear scope
- explicit dependencies
- local authority
- plausible future exportability
