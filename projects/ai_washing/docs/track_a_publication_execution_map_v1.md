# AI-Washing Track A Publication Execution Map V1

## Purpose

This note is the current navigation map for the AI-washing publication phase.

It answers four practical questions:
1. where should we look first when resuming work?
2. which paths are live execution surfaces versus archives?
3. where do the benchmark, IRR, and shadow-classification assets now live?
4. where should new work be added so we do not lose the thread again?

## Current execution principle

The repo restructure is only partially visible from path names.

That means this rule matters:
- the installed runtime and canonical CLI entrypoints still primarily flow
  through `src/semantic_ai_washing/`
- project planning and handoff notes live under `projects/ai_washing/docs/`
- benchmark and label artifacts live under `data/labels/` and
  `data/validation/`
- execution reports live under `reports/`

So if a script is actively executed with:
- `python -m semantic_ai_washing...`

then the canonical runtime path is usually under:
- `src/semantic_ai_washing/`

even if a related member-scoped file also exists under:
- `projects/ai_washing/src/ai_washing_member/`

## Directory map

### 1. Project docs and execution notes

Use:
- `projects/ai_washing/docs/`

For:
- publication roadmap
- stakeholder expectations
- classifier and IRR notes
- market-data and event-study design notes
- project-scoped execution memos

Read first:
- `publication_upgrade_stakeholder_expectations_v1.md`
- `publication_upgrade_roadmap_v1.md`
- `track_a_stage_checkpoint_v1.md`
- `track_a_execution_plan_v1.md`
- `track_a_event_study_and_economic_impact_design_v1.md`

### 2. Live runtime scripts

Use:
- `src/semantic_ai_washing/`

For:
- classification
- labeling
- data extraction / cleaning
- aggregation
- shadow selective-defer utilities
- panel-building and measurement scripts

Current important live families:
- `classification/`
- `labeling/`
- `data/`
- `aggregation/`
- `patents/`

### 3. Member-local code

Use:
- `projects/ai_washing/src/ai_washing_member/`

For:
- member-scoped helpers
- wrappers and local experiments
- project-local code that should travel with the project member if exported

Operational caution:
- do not assume the member path has replaced the canonical runtime path
- for active runs, verify the actual invoked module path before editing

### 4. Labels and IRR assets

Use:
- `data/labels/v1/`
- `data/labels/v2/`
- `data/labels/v3/`

Interpretation:
- `v1`: original and revised label backbone, early IRR assets
- `v2`: revised-boundary adjudication and held-out-v4 build inputs
- `v3`: rerun IRR cycle, rerun adjudication, failed-run archive separation

Current trustworthy human-reliability surface:
- `reports/labels/irr_boundary_revised_v3_rerun_report.json`
- `reports/labels/irr_boundary_revised_v3_rerun_status.json`

### 5. Held-out benchmark assets

Use:
- `data/validation/held_out_v3/`
- `data/validation/held_out_v4/`
- `data/validation/irr_boundary_benchmark_v1.csv`

Interpretation:
- `held_out_v3`: rebuilt reviewed benchmark under revised rubric
- `held_out_v4`: adjudicated development benchmark built from revised IRR v2
- `irr_boundary_benchmark_v1.csv`: hard-case benchmark surface

Current benchmark summary outputs:
- `reports/evaluation/model_benchmark_matrix_heldout_v3_v1.json`
- `reports/evaluation/model_benchmark_matrix_heldout_v3_layered_v1.json`
- `reports/evaluation/model_benchmark_matrix_heldout_v4_v1.json`
- `reports/evaluation/selective_defer_heldout_v4_hybrid_api_upgrade_v2.json`

### 6. Shadow full-corpus classification lane

Use:
- `data/processed/classifications_shadow_local_layered_v1/`
- `data/processed/shadow/deferred_review_sheets/`
- `reports/classification/`
- `reports/api/`

Interpretation:
- local layered pass outputs sit under `reports/classification/`
- deferred API review sheets sit under
  `data/processed/shadow/deferred_review_sheets/`
- live API progress and spend reports sit under `reports/api/`
- shard progress currently lives under `reports/api/shards/`

Current provisional hybrid lane:
- policy: `conf49`
- deferred slice:
  - `data/processed/shadow/deferred_review_sheets/selective_defer_conf49_shadow_full_corpus_v1.csv`

### 7. Final handoff-style reports

Use:
- `reports/final/`

For:
- compact narrative summaries
- handoff CSV/JSON artifacts
- one-off robustness notes worth citing in later writing

Examples:
- `reports/final/ai_washing_patent_matching_robustness_v1.md`
- `reports/final/ai_washing_validation_asset_registry_v3.json`

## What to treat as current versus historical

Treat as current:
- the docs listed in the read order above
- `reports/evaluation/` outputs for the layered and selective-defer runs
- `reports/labels/irr_boundary_revised_v3_rerun_*`
- `reports/classification/active_window_coverage_shadow_local_layered_*`
- `reports/api/shards/*`

Treat as background / audit trail:
- migration sheets
- planning notes from the restructure period
- older tranche-level prompt calibration notes unless directly reused

## Recommended resume order for a future session

1. `projects/ai_washing/docs/track_a_publication_execution_map_v1.md`
2. `projects/ai_washing/docs/track_a_stage_checkpoint_v1.md`
3. `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
4. `projects/ai_washing/docs/track_a_event_study_and_economic_impact_design_v1.md`
5. latest relevant status report under `reports/labels/`, `reports/classification/`,
   or `reports/api/`
6. only then edit runtime scripts under `src/semantic_ai_washing/`

## Bottom line

The repo is usable now, but only if we keep one distinction explicit:
- execution code is still primarily under `src/semantic_ai_washing/`
- project reasoning and execution control live under `projects/ai_washing/docs/`

That split is acceptable as long as the docs keep pointing to the live surfaces.
