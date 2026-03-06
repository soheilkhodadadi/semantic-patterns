# Roadmap Model Spec

`director/model/roadmap_model.yaml` is the canonical planning source for director.

## Core Rules

- YAML is canonical; `docs/director/roadmap_master.md` is generated from it.
- Phases remain the user-facing execution unit.
- Tasks are the internal planning and optimization unit.
- The optimizer may emit patch proposals, but it does not rewrite the canonical YAML automatically.

## Required Top-Level Keys

- `schema_version`
- `project`
- `settings`
- `iterations`

## Iteration Model

Each iteration defines:

- `iteration_id`
- `title`
- `goal`
- `phases`

## Phase Model

Each phase defines:

- `phase_id`
- `title`
- `goal`
- `depends_on`
- `canonical`
- `required_artifacts`
- `tasks`

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

## Conditions

Supported condition kinds in v1:

- `artifact_exists`
- `csv_row_count_gte`
- `json_field_compare`
- `file_hash_present`
- `manual_artifact_present`
- `sentence_fragment_rate_lte`

Conditions can:

- `block`
- `warn`
- `reroute`

## Remediation Library

Reusable corrective tasks live in `director/model/remediation_library.yaml`.

The optimizer may reference remediation task ids in patch proposals when:

- a precondition fails with `reroute`
- a quality check fails with `reroute`

## Render and Validation

Use:

- `python -m semantic_ai_washing.director.cli render-roadmap`
- `python -m semantic_ai_washing.director.cli doctor`

`doctor` validates:

- roadmap model schema load
- remediation library existence
- generated roadmap freshness against canonical YAML hash
