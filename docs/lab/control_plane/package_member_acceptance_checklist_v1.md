# Package/Member Acceptance Checklist V1

## Purpose

This is the operational checklist for deciding whether a shared package or project member is ready to be treated as a real lab unit.

Use it for:
- package seeds under `packages/`
- project members under `projects/`
- inbound teammate modules being considered for promotion

This is intentionally concrete.
It is a gate, not just guidance prose.

## Status levels

- `planned`
  - the unit has a defined scope but is not yet buildable
- `seeded`
  - the unit has a clear structure and identity, but migration is still partial
- `buildable`
  - the unit can satisfy basic packaging and validation checks
- `export_ready`
  - the unit can plausibly be copied out or shared with limited surgery

## Checklist template

Record one row per candidate unit.

| Check family | Check | Required for planned | Required for seeded | Required for buildable | Required for export_ready | Evidence / note | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Identity | Canonical unit name is fixed | Y | Y | Y | Y |  |  |
| Identity | Scope is explicit: shared package vs project member | Y | Y | Y | Y |  |  |
| Ownership | README states unit purpose and local authority | Y | Y | Y | Y |  |  |
| Structure | Minimum directories exist or have approved plan | Y | Y | Y | Y |  |  |
| Metadata | `pyproject.toml` plan exists | Y | Y | Y | Y |  |  |
| Metadata | Real `pyproject.toml` exists | N | Y | Y | Y |  |  |
| Metadata | `[build-system]` is explicit | N | Y | Y | Y |  |  |
| Metadata | `[project]` metadata is explicit if buildable | N | N | Y | Y |  |  |
| Dependencies | Dependency direction is documented | Y | Y | Y | Y |  |  |
| Dependencies | No deep imports into another unit's private internals | N | Y | Y | Y |  |  |
| Tests | Local test scope is defined | N | Y | Y | Y |  |  |
| Tests | Targeted tests exist or TODO path is explicit | N | Y | Y | Y |  |  |
| Validation | Ruff/pytest scope is runnable without full-repo context | N | N | Y | Y |  |  |
| Validation | Basic build smoke test passes | N | N | Y | Y |  |  |
| Validation | Workspace sync or path-dependency install path is documented | N | N | Y | Y |  |  |
| Migration | Legacy-vs-new mapping note exists | N | Y | Y | Y |  |  |
| Privacy | Privacy class and local-private boundary are explicit if needed | Y | Y | Y | Y |  |  |
| Exportability | Unit could be copied out with limited path edits | N | N | N | Y |  |  |
| Exportability | Unit does not drag unrelated lab internals with it | N | N | N | Y |  |  |

## Required command profile by stage

### Seeded
- `git diff --check`
- local README and mapping-note review

### Buildable
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `pytest`
- `uv build --package <name> --no-sources` or `python -m build <path>`

### Export-ready
- all buildable checks
- explicit dependency review
- copy-out or package-boundary dry run documented

## Promotion rules

### Promote to `seeded` when
- unit identity is stable
- structure is visible
- README and mapping note exist
- dependency direction is known

### Promote to `buildable` when
- `pyproject.toml` is real
- tests are localizable
- basic build and validation pass

### Promote to `export_ready` when
- the unit can be copied out or published without deep surgery
- unrelated dependencies have been trimmed or explicitly justified

## Fail conditions

Do not promote if any of these are true:
- unit identity is still ambiguous
- README authority is missing
- the unit depends on deep private imports from another unit
- buildability is claimed without a real packaging anchor
- exportability is claimed but the unit still drags unrelated internals

## Initial intended uses

Near-term likely candidates:
- `packages/labcore`
- `packages/director`
- `projects/ai_washing`

Later candidates:
- `projects/eri`
- `projects/allocationlab`

## Bottom line

A candidate unit is accepted when we can say, with evidence:
- what it is
- who owns it
- how it builds
- what it depends on
- whether it is only seeded, buildable, or export-ready
