# Director Migration Sheets

## Purpose

This folder contains the grouped migration sheets for extracted `director`
package slices.

Each sheet records:
- the canonical package-owned authority
- the main migrated callers
- the focused validation gate used for that surface

These are operational tracking artifacts. They are useful during migration, but
they should not dominate the package front door.

## Current grouped sheets

- `roadmap_model_grouped_migration_sheet_v1.md`
- `render_grouped_migration_sheet_v1.md`
- `task_graph_grouped_migration_sheet_v1.md`
- `config_grouped_migration_sheet_v1.md`
- `readiness_grouped_migration_sheet_v1.md`
- `branching_grouped_migration_sheet_v1.md`
- `state_grouped_migration_sheet_v1.md`
- `decision_grouped_migration_sheet_v1.md`
- `sensors_grouped_migration_sheet_v1.md`
- `playbooks_grouped_migration_sheet_v1.md`
- `snapshot_grouped_migration_sheet_v1.md`
- `gates_grouped_migration_sheet_v1.md`
- `executor_grouped_migration_sheet_v1.md`
- `cost_grouped_migration_sheet_v1.md`
- `llm_grouped_migration_sheet_v1.md`
- `planner_grouped_migration_sheet_v1.md`
- `validation_assets_grouped_migration_sheet_v1.md`
- `script_inventory_grouped_migration_sheet_v1.md`
- `iteration_log_grouped_migration_sheet_v1.md`
- `documents_grouped_migration_sheet_v1.md`
- `atlas_grouped_migration_sheet_v1.md`
- `api_bootstrap_grouped_migration_sheet_v1.md`
- `cli_grouped_migration_sheet_v1.md`
- `main_module_grouped_migration_sheet_v1.md`
- `api_assistive_grouped_migration_sheet_v1.md`
- `optimizer_grouped_migration_sheet_v1.md`
- `review_grouped_migration_sheet_v1.md`

## How to use this folder

If you are trying to understand the package quickly, start here instead:
- `packages/director/README.md`
- `docs/roadmap_v2/current_state_navigation_v1.md`

Use the grouped migration sheets only when you need slice-by-slice migration
detail.
