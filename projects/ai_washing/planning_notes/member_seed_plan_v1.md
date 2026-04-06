# AI-Washing Member Seed Plan V1

## Purpose

This note defines the first true member-seeding plan for `ai_washing`.

Unlike ERI and AllocationLab, AI-washing already has:
- active code
- active reports
- active manuscript outputs
- an existing package identity

That makes it the only project member that should move beyond placeholder status in the near term.

## Recommendation

### Distribution name
- `semantic-ai-washing`

### Import package name
- `semantic_ai_washing`

### Why this pairing
- preserves the current import identity instead of forcing a disruptive rename
- keeps the active paper lane and existing scripts stable during transition
- gives the member a real package identity immediately, because it already has one in practice

## Member decision

`ai_washing` should be treated as:
- a local workspace member seed
- not a path-dependent placeholder

Why:
- it is the flagship active project
- the repo already contains its code and delivery stack
- delaying its member identity would keep the migration abstract for too long

## Proposed future member structure

```text
projects/ai_washing/
|-- pyproject.toml
|-- README.md
|-- src/
|   `-- semantic_ai_washing/
|-- tests/
|-- docs/
|-- configs/
|-- reports/
`-- output/
```

## Important boundary rule

The manuscript lane remains separate:
- `paper/`

Even after the member becomes real, the paper should remain a distinct manuscript lane rather than being flattened into a generic project output bucket.

## Current source pressure

Member-owned pressure currently spans:
- `src/semantic_ai_washing/`
- `tests/`
- `docs/projects/ai_washing/`
- parts of `reports/analysis/`
- future project-scoped outputs under `output/doc/projects/ai_washing/` and `output/figures/projects/ai_washing/`

## Near-term migration strategy

Do not move everything at once.
Seed the member in this order:
1. project-local docs and reports
2. project output lanes for fresh artifacts
3. bounded code-side migrations only after mappings are explicit

Keep current authoritative legacy lanes until each replacement path is validated.

## Initial pyproject shape

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "semantic-ai-washing"
version = "0.1.0"
description = "AI disclosure and validation workflows for the semantic-patterns lab"
readme = "README.md"
requires-python = ">=3.11"
```

## Acceptance target

`ai_washing` should be the first project member to reach:
- `seeded`

It should reach `buildable` only after:
- member-local docs/report lanes are clearer
- at least one bounded code-side migration is ready
- package metadata can be introduced without breaking the active paper workflow

## Bottom line

`ai_washing` is the first real project member.
Its member seed should preserve the current import identity while gradually moving ownership into the `projects/ai_washing/` lane.
