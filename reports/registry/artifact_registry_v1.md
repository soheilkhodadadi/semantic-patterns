# Artifact Registry V1

## Purpose

This registry names the first authoritative landing zones for Wave 2.
It does not move existing artifacts yet.
It makes future placement explicit so later migrations are deliberate.

## Registry fields

- `artifact class`
- `authoritative tracked lane`
- `project split`
- `status`
- `notes`

## Current registry

| Artifact class | Authoritative tracked lane | Project split | Status | Notes |
| --- | --- | --- | --- | --- |
| Lab control-plane docs | `docs/roadmap_v2/` now, later `docs/lab/control_plane/` | shared | working | Current active planning remains in roadmap form until promoted |
| Shared schemas and contracts | `docs/lab/schemas/` | shared | scaffolded | Populate only when a contract is meant to serve multiple programs |
| Project orientation docs | `docs/projects/<project>/` | project | scaffolded | Use for stable, public-safe project notes |
| Registry and inventory reports | `reports/registry/` | shared | authoritative | This lane is now the default home for registry-style reports |
| Project analytical reports | `reports/projects/<project>/` | project | scaffolded | Use for project-specific analyses after migration |
| Shared processed datasets | `data/processed/shared/` | shared | scaffolded | Only for genuinely cross-project derived datasets |
| Project processed datasets | `data/processed/projects/<project>/` | project | scaffolded | Future destination for project-specific derived data products |
| Shared document outputs | `output/doc/shared/` | shared | scaffolded | Use for reusable, non-project-specific delivery objects |
| Project document outputs | `output/doc/projects/<project>/` | project | scaffolded | Future destination for project-level polished docs |
| Shared figure outputs | `output/figures/shared/` | shared | scaffolded | Use for reusable visual assets or shared demos |
| Project figure outputs | `output/figures/projects/<project>/` | project | scaffolded | Future destination for project-level figure outputs |

## Immediate interpretation

Wave 2 establishes the lanes.
It does not force a bulk move of legacy outputs.
New material should prefer these destinations when there is no stronger project-specific convention already in place.
