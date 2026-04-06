# Director Package Seed

## Status
- seeded package shell
- real `pyproject.toml` present
- canonical implementation now exists for selected extracted slices while
  legacy compatibility shims remain in place

## Purpose

`director` is the orchestration and control-discipline package for the lab.

It should own:
- control logic
- playbooks
- run/review structure
- coordination utilities that help manage work across projects

It should not become:
- a hidden home for all business logic
- a forced dependency for every project-specific decision
- a replacement for project members

## Current source pressure

The current live director stack still exists in:
- `director/`
- selected compatibility layers under `src/semantic_ai_washing/director/`

This placeholder directory marks the future package destination, not an immediate code relocation.

## Promotion rule

Promote code here only when:
- the director-owned scope is explicit
- the package boundary is cleaner than the current mixed layout
- the migration does not blur project ownership

See also:
- `packages/director/pyproject_seed_plan_v1.md`
- `packages/director/first_extraction_slice_v1.md`

First extracted package slice:
- `packages/director/src/semantic_director/schemas.py`
- `packages/director/src/semantic_director/__init__.py`

Migration trace:
- `docs/roadmap_v2/migration_round_g_director_schema_extraction_v1.md`

Second extracted package slice:
- `packages/director/src/semantic_director/policies/risk_register.py`
- `packages/director/src/semantic_director/policies/__init__.py`

Migration trace:
- `docs/roadmap_v2/migration_round_h_director_policies_extraction_v1.md`

Third extracted package slice:
- `packages/director/src/semantic_director/roadmap_model.py`

Migration trace:
- `docs/roadmap_v2/migration_round_t_director_roadmap_model_seed_v1.md`
- `packages/director/roadmap_model_grouped_migration_sheet_v1.md`

Fourth extracted package slice:
- `packages/director/src/semantic_director/render.py`

Migration trace:
- `docs/roadmap_v2/migration_round_u_director_render_seed_v1.md`
- `packages/director/render_grouped_migration_sheet_v1.md`

Fifth extracted package slice:
- `packages/director/src/semantic_director/task_graph.py`

Migration trace:
- `docs/roadmap_v2/migration_round_v_director_task_graph_seed_v1.md`
- `packages/director/task_graph_grouped_migration_sheet_v1.md`

Sixth extracted package slice:
- `packages/director/src/semantic_director/config.py`

Migration trace:
- `docs/roadmap_v2/migration_round_x_director_config_seed_v1.md`
- `packages/director/config_grouped_migration_sheet_v1.md`

Seventh extracted package slice:
- `packages/director/src/semantic_director/readiness.py`

Migration trace:
- `docs/roadmap_v2/migration_round_y_director_readiness_seed_v1.md`
- `packages/director/readiness_grouped_migration_sheet_v1.md`

Eighth extracted package slice:
- `packages/director/src/semantic_director/branching.py`

Migration trace:
- `docs/roadmap_v2/migration_round_aa_director_branching_seed_v1.md`
- `packages/director/branching_grouped_migration_sheet_v1.md`

Ninth extracted package slice:
- `packages/director/src/semantic_director/state.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ab_director_state_seed_v1.md`
- `packages/director/state_grouped_migration_sheet_v1.md`

Tenth extracted package slice:
- `packages/director/src/semantic_director/decision.py`

Migration trace:
- `docs/roadmap_v2/migration_round_af_director_decision_seed_v1.md`
- `packages/director/decision_grouped_migration_sheet_v1.md`

Eleventh extracted package slice:
- `packages/director/src/semantic_director/sensors.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ag_director_sensors_seed_v1.md`
- `packages/director/sensors_grouped_migration_sheet_v1.md`

Twelfth extracted package slice:
- `packages/director/src/semantic_director/playbooks.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ai_director_playbooks_seed_v1.md`
- `packages/director/playbooks_grouped_migration_sheet_v1.md`

Thirteenth extracted package slice:
- `packages/director/src/semantic_director/snapshot.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ak_director_snapshot_seed_v1.md`
- `packages/director/snapshot_grouped_migration_sheet_v1.md`

Fourteenth extracted package slice:
- `packages/director/src/semantic_director/gates.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ao_director_gates_seed_v1.md`
- `packages/director/gates_grouped_migration_sheet_v1.md`

Fifteenth extracted package slice:
- `packages/director/src/semantic_director/executor.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ar_director_executor_seed_v1.md`
- `packages/director/executor_grouped_migration_sheet_v1.md`

Sixteenth extracted package slice:
- `packages/director/src/semantic_director/cost.py`

Migration trace:
- `docs/roadmap_v2/migration_round_at_director_cost_seed_v1.md`
- `packages/director/cost_grouped_migration_sheet_v1.md`

Seventeenth extracted package slice:
- `packages/director/src/semantic_director/llm.py`

Migration trace:
- `docs/roadmap_v2/migration_round_au_director_llm_seed_v1.md`
- `packages/director/llm_grouped_migration_sheet_v1.md`

Eighteenth extracted package slice:
- `packages/director/src/semantic_director/planner.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ax_director_planner_seed_v1.md`
- `packages/director/planner_grouped_migration_sheet_v1.md`

Nineteenth extracted package slice:
- `packages/director/src/semantic_director/validation_assets.py`

Migration trace:
- `docs/roadmap_v2/migration_round_bx_director_validation_assets_seed_v1.md`
- `packages/director/validation_assets_grouped_migration_sheet_v1.md`

Twentieth extracted package slice:
- `packages/director/src/semantic_director/script_inventory.py`

Migration trace:
- `docs/roadmap_v2/migration_round_by_director_script_inventory_seed_v1.md`
- `packages/director/script_inventory_grouped_migration_sheet_v1.md`
