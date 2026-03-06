# Roadmap Model Spec

`director/model/roadmap_model.yaml` is the canonical planning source for director.

## Core Rules
- YAML is canonical; `docs/director/roadmap_master.md` is generated from it.
- Phases remain the public execution unit.
- Tasks are the internal optimization and readiness unit.
- The optimizer is proposal-only. It may emit resequencing patches, but it may not rewrite the canonical roadmap.
- Historical and superseded phases stay in the model for traceability but are not executable.

## Required Top-Level Keys
- `schema_version`
- `project`
- `settings`
- `policies`
- `data_layers`
- `source_windows`
- `tooling_policies`
- `iterations`

## Policy Model
Each policy defines:
- `policy_id`
- `kind`
- `description`
- `enforcement`
- `targets`
- `value`

Current hard policies include:
- held-out freeze
- human-human IRR only
- assistive-only API use
- no significance optimization
- split registry required before retraining
- sentence-quality gates before labeling and IRR

## Data Layer Model
Each data layer defines:
- `layer_id`
- `canonical_path`
- `format`
- `required_fields`
- optional `review_export_path`
- optional `description`

Canonical layers in v2:
- source index
- manifest registry
- sentence table
- split registry
- label table
- model artifacts
- classification table
- panel

## Source Window Model
Each source window defines:
- `source_window_id`
- `years`
- `source_root_ref`
- `status`
- optional `availability_condition`

This allows the optimizer to defer historical work when the indexed source window is unavailable.

## Tooling Policy Model
Each tooling policy defines:
- `policy_id`
- `tool`
- `mode`
- `repo_root_uv_run_forbidden`
- `required_runner`
- optional `wrapper_path`
- optional repo `.venv` expectations

This is used for Atlas isolation and doctor checks.

## Phase Model
Each phase defines:
- `phase_id`
- `title`
- `goal`
- `depends_on`
- `canonical`
- `required_artifacts`
- `lifecycle_state`
- optional `source_window_id`
- optional `tags`
- `tasks`

Allowed `lifecycle_state` values:
- `planned`
- `active`
- `completed`
- `historical`
- `superseded`
- `deferred`

## Task Model
Each task defines:
- `task_id`
- `title`
- `description`
- `iteration_id`
- `phase_id`
- `kind`
- `depends_on`
- `inputs`
- `outputs`
- `preconditions`
- `quality_checks`
- `commands`
- `manual_handoff`
- `risks`
- `estimated_effort`
- `risk_reduction`
- `automation_level`
- `on_fail`
- `reroute_to`
- `evidence_required`
- `tags`
- `gate_class`

Allowed `gate_class` values:
- `science`
- `data`
- `ops`
- `manual`
- `release`

## Conditions
Supported condition kinds in v2:
- `artifact_exists`
- `csv_row_count_gte`
- `json_field_compare`
- `file_hash_present`
- `manual_artifact_present`
- `sentence_fragment_rate_lte`
- `indexed_years_include`

Conditions may:
- `block`
- `warn`
- `reroute`

## Remediation Library
Reusable corrective tasks live in `director/model/remediation_library.yaml`.

The optimizer may reference remediation task ids when:
- a precondition fails with reroute semantics
- a quality check fails with reroute semantics
- sentence-quality gates fail before labeling or IRR

## Validation
Use:
```bash
python -m semantic_ai_washing.director.cli render-roadmap
python -m semantic_ai_washing.director.cli ingest \
  --protocol docs/director/implementation_protocol_master.md \
  --roadmap-model director/model/roadmap_model.yaml \
  --iteration-log docs/iteration_log.md
python -m semantic_ai_washing.director.cli optimize
python -m semantic_ai_washing.director.cli doctor
```

`doctor` validates:
- roadmap model schema load
- remediation library schema load
- rendered roadmap freshness
- tooling policy presence
- repo `.venv` policy compliance for Atlas-safe execution
