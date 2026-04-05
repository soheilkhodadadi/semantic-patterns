# Migration Wave 1 V1

## Purpose

This note defines the first concrete migration wave for the lab restructure.

Wave 1 is intentionally low-risk.
Its role is to establish the control plane that later waves will rely on.

## Wave objective

Create the minimum operational documents needed to make the repo understandable as a multi-program lab.

## Scope

Wave 1 covers:
- engine boundary
- source-of-truth mapping
- artifact classification
- project registry
- target repo layout
- execution plan

Wave 1 does not cover:
- moving code between packages
- renaming the package
- deleting legacy trees
- starting ERI or AllocationLab implementation

## Deliverables

Required documents:
- `engine_boundary_memo_v1.md`
- `source_of_truth_map_v1.md`
- `artifact_policy_v1.md`
- `project_registry_v1.md`
- `target_repo_layout_v1.md`
- `restructure_execution_plan_v1.md`

Supporting notes:
- `roadmap_v4_multi_program_v1.md`
- `lab_mvp_1_0_blueprint_v1.md`
- `platform_patterns_research_v1.md`
- `lab_architecture_scenarios_v1.md`

## Acceptance gate

Wave 1 is complete when all of the following are true:
- the authoritative code lane is named explicitly
- shared-core vs project-specific is named explicitly
- artifact classes are named explicitly
- active projects and their modes are named explicitly
- the target layout and future migration waves are named explicitly

## Risks addressed by Wave 1

Wave 1 reduces these risks:
- unclear ownership of outputs
- accidental mixing of public-safe and private-sensitive planning
- collaborators not knowing which code lane is canonical
- premature platform abstraction without a boundary map
- migration work happening without a staged plan

## Open questions deliberately deferred

Wave 1 does not answer yet:
- which exact code modules move first
- whether `labcore/` should exist immediately in code
- whether package-neutral naming is worth doing before reuse pressure appears
- which future project gets staffed first if multiple programs activate at once

Those belong to later waves.

## Recommended next move after Wave 1

Immediately after Wave 1, the safest next migration step is Wave 2:
- create lane structure and authoritative destinations without major code motion

That means the next likely file outputs should be:
- `docs/lab/...` scaffolding
- `docs/projects/...` scaffolding
- `reports/projects/...` scaffolding
- `output/doc/shared/` and `output/doc/projects/...` destination notes

## Bottom line

Wave 1 does not make the lab real by itself.
But it makes the restructure governable.
That is the correct first step.
