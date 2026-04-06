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
- `packages/director/migration_sheets/roadmap_model_grouped_migration_sheet_v1.md`

Fourth extracted package slice:
- `packages/director/src/semantic_director/render.py`

Migration trace:
- `docs/roadmap_v2/migration_round_u_director_render_seed_v1.md`
- `packages/director/migration_sheets/render_grouped_migration_sheet_v1.md`

Fifth extracted package slice:
- `packages/director/src/semantic_director/task_graph.py`

Migration trace:
- `docs/roadmap_v2/migration_round_v_director_task_graph_seed_v1.md`
- `packages/director/migration_sheets/task_graph_grouped_migration_sheet_v1.md`

Sixth extracted package slice:
- `packages/director/src/semantic_director/config.py`

Migration trace:
- `docs/roadmap_v2/migration_round_x_director_config_seed_v1.md`
- `packages/director/migration_sheets/config_grouped_migration_sheet_v1.md`

Seventh extracted package slice:
- `packages/director/src/semantic_director/readiness.py`

Migration trace:
- `docs/roadmap_v2/migration_round_y_director_readiness_seed_v1.md`
- `packages/director/migration_sheets/readiness_grouped_migration_sheet_v1.md`

Eighth extracted package slice:
- `packages/director/src/semantic_director/branching.py`

Migration trace:
- `docs/roadmap_v2/migration_round_aa_director_branching_seed_v1.md`
- `packages/director/migration_sheets/branching_grouped_migration_sheet_v1.md`

Ninth extracted package slice:
- `packages/director/src/semantic_director/state.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ab_director_state_seed_v1.md`
- `packages/director/migration_sheets/state_grouped_migration_sheet_v1.md`

Tenth extracted package slice:
- `packages/director/src/semantic_director/decision.py`

Migration trace:
- `docs/roadmap_v2/migration_round_af_director_decision_seed_v1.md`
- `packages/director/migration_sheets/decision_grouped_migration_sheet_v1.md`

Eleventh extracted package slice:
- `packages/director/src/semantic_director/sensors.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ag_director_sensors_seed_v1.md`
- `packages/director/migration_sheets/sensors_grouped_migration_sheet_v1.md`

Twelfth extracted package slice:
- `packages/director/src/semantic_director/playbooks.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ai_director_playbooks_seed_v1.md`
- `packages/director/migration_sheets/playbooks_grouped_migration_sheet_v1.md`

Thirteenth extracted package slice:
- `packages/director/src/semantic_director/snapshot.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ak_director_snapshot_seed_v1.md`
- `packages/director/migration_sheets/snapshot_grouped_migration_sheet_v1.md`

Fourteenth extracted package slice:
- `packages/director/src/semantic_director/gates.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ao_director_gates_seed_v1.md`
- `packages/director/migration_sheets/gates_grouped_migration_sheet_v1.md`

Fifteenth extracted package slice:
- `packages/director/src/semantic_director/executor.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ar_director_executor_seed_v1.md`
- `packages/director/migration_sheets/executor_grouped_migration_sheet_v1.md`

Sixteenth extracted package slice:
- `packages/director/src/semantic_director/cost.py`

Migration trace:
- `docs/roadmap_v2/migration_round_at_director_cost_seed_v1.md`
- `packages/director/migration_sheets/cost_grouped_migration_sheet_v1.md`

Seventeenth extracted package slice:
- `packages/director/src/semantic_director/llm.py`

Migration trace:
- `docs/roadmap_v2/migration_round_au_director_llm_seed_v1.md`
- `packages/director/migration_sheets/llm_grouped_migration_sheet_v1.md`

Eighteenth extracted package slice:
- `packages/director/src/semantic_director/planner.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ax_director_planner_seed_v1.md`
- `packages/director/migration_sheets/planner_grouped_migration_sheet_v1.md`

Nineteenth extracted package slice:
- `packages/director/src/semantic_director/validation_assets.py`

Migration trace:
- `docs/roadmap_v2/migration_round_bx_director_validation_assets_seed_v1.md`
- `packages/director/migration_sheets/validation_assets_grouped_migration_sheet_v1.md`

Twentieth extracted package slice:
- `packages/director/src/semantic_director/script_inventory.py`

Migration trace:
- `docs/roadmap_v2/migration_round_by_director_script_inventory_seed_v1.md`
- `packages/director/migration_sheets/script_inventory_grouped_migration_sheet_v1.md`

Twenty-first extracted package slice:
- `packages/director/src/semantic_director/iteration_log.py`

Migration trace:
- `docs/roadmap_v2/migration_round_bz_director_iteration_log_seed_v1.md`
- `packages/director/migration_sheets/iteration_log_grouped_migration_sheet_v1.md`

Twenty-second extracted package slice:
- `packages/director/src/semantic_director/documents.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ca_director_documents_seed_v1.md`
- `packages/director/migration_sheets/documents_grouped_migration_sheet_v1.md`

Twenty-third extracted package slice:
- `packages/director/src/semantic_director/atlas.py`

Migration trace:
- `docs/roadmap_v2/migration_round_cb_director_atlas_seed_v1.md`
- `packages/director/migration_sheets/atlas_grouped_migration_sheet_v1.md`

Twenty-fourth extracted package slice:
- `packages/director/src/semantic_director/api_bootstrap.py`

Migration trace:
- `docs/roadmap_v2/migration_round_cc_director_api_bootstrap_seed_v1.md`
- `packages/director/migration_sheets/api_bootstrap_grouped_migration_sheet_v1.md`

Twenty-fifth extracted package slice:
- `packages/director/src/semantic_director/cli.py`

Migration trace:
- `docs/roadmap_v2/migration_round_cd_director_cli_seed_v1.md`
- `packages/director/migration_sheets/cli_grouped_migration_sheet_v1.md`

Twenty-sixth extracted package slice:
- `packages/director/src/semantic_director/__main__.py`

Migration trace:
- `docs/roadmap_v2/migration_round_ce_director_main_module_seed_v1.md`
- `packages/director/migration_sheets/main_module_grouped_migration_sheet_v1.md`

Late-stage boundary cleanup:
- `docs/roadmap_v2/migration_round_co_director_runtime_schema_boundary_cleanup_v1.md`
- `docs/roadmap_v2/migration_round_cp_director_responses_transport_boundary_cleanup_v1.md`
- `docs/roadmap_v2/director_utility_boundary_posture_refresh_v1.md`

Late-stage wrapper normalization:
- `packages/director/src/semantic_director/security.py`
- `packages/director/src/semantic_director/runtime.py`
- `docs/roadmap_v2/migration_round_cr_director_security_wrapper_normalization_v1.md`
- `docs/roadmap_v2/migration_round_cs_director_runtime_wrapper_normalization_v1.md`
- `docs/roadmap_v2/director_wrapper_normalization_posture_refresh_v1.md`
