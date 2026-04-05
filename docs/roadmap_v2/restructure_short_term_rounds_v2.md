# Restructure Short-Term Rounds V2

## Purpose

This note updates the short-term execution ladder to match the revised end-state:
- workspace monorepo
- shared infrastructure packages
- package-style project members
- thin shared artifact lanes

The intent is to make the next rounds move toward `packages/`, `projects/`, and `shared/`, not just toward a cleaner version of the old centralized tree.

## Current checkpoint

Completed already:
- Wave 1 control-plane setup
- Wave 2 lane scaffolding
- Wave 3 first shared-helper round
  - lane registry
  - runtime
  - audit
  - security
  - OpenAI Responses
- adapter framing and adapter registry
- revised end-state architecture and target layout V2
- Round A standards and contracts
- Round B workspace skeleton
- Round C package seeding

This means the repo now has:
- a real control-plane foundation
- a small shared package seed
- a clearer package-centric target
- visible root landing zones for `packages/`, `projects/`, and `shared/`
- first explicit seed plans for `labcore`, `director`, and `ai_washing`

Remaining actionable rounds now start at Round D.
Rounds A through C remain documented below as completed reference anchors.

## Remaining rounds

### Round A. Standards and contracts round

Objective:
- define the standards that every future shared package or project member must satisfy

Primary outputs:
- workspace-member contract
- manifest contract
- evidence-unit contract
- package/member acceptance checklist
- standards-aware validation profile for future members/packages

Why first:
- this prevents us from creating ad hoc members with inconsistent structure

Acceptance gate:
- we can answer, concretely, what qualifies as:
  - a shared package
  - a project member
  - a shared artifact
  - a path dependency that should not yet be promoted

### Round B. Workspace skeleton round

Objective:
- make the future end-state visible in the filesystem without forcing immediate code relocation

Primary outputs:
- `packages/README.md`
- `projects/README.md`
- `shared/README.md`
- placeholder lane READMEs under `shared/`
- draft package/member seed notes for `labcore`, `director`, `ai_washing`, `eri`, `allocationlab`
- initial rule for when to use a workspace member versus a path dependency

Why now:
- contributors need obvious landing zones before meaningful migrations start

Acceptance gate:
- a contributor can tell where a new shared package belongs, where a new project member belongs, and where a shared artifact belongs

### Round C. Package seeding round

Objective:
- turn the most mature future members into explicit package seeds

Primary outputs:
- draft `pyproject.toml` plan for `packages/labcore`
- draft `pyproject.toml` plan for `packages/director`
- draft member seed plan for `projects/ai_washing`
- decide whether `eri` and `allocationlab` start as planned members or path-dependent placeholders

Why here:
- this is the first point where the migration should start to look like a workspace, not just a roadmap

Acceptance gate:
- each seeded package/member has:
  - declared scope
  - package identity
  - dependency direction
  - migration guardrails

Current anchor:
- `docs/roadmap_v2/migration_round_c_package_seeding_v1.md`

### Round D. First bounded member-facing migrations

Objective:
- migrate one small real slice using the new package/member mindset

Candidate slices:
- one `labcore` direct-caller migration family
- one `ai_washing` member-owned docs/report lane normalization slice
- one shared artifact family move if the contract is already stable

Why here:
- we need one real proof that the workspace/package model works in practice

Acceptance gate:
- at least one migration batch lands into a future package/member destination without breaking current authority

### Round E. Workspace tooling decision round

Objective:
- decide whether the repo is ready for real workspace metadata or should keep staged path-style preparation longer

Decision inputs:
- how stable the member/package boundaries are
- how aligned Python requirements are
- whether shared-lockfile behavior would help or constrain us

Possible outputs:
- introduce workspace metadata in root `pyproject.toml`
- keep staged path-dependency planning a bit longer
- define the first package build/sync smoke tests that become mandatory once members are declared buildable

Acceptance gate:
- the decision is explicit and documented, not implicit drift

## Recommended order

The right near-term order is:
1. Round A
2. Round B
3. Round C
4. Round D
5. Round E

Reason:
- standards before structure
- structure before seeded members
- seeded members before real migrations
- real migrations before workspace-tooling commitment

## What not to do yet

Still defer:
- broad code relocation into `projects/` or `packages/` without contract coverage
- a multi-repo split
- large deletions of active legacy AI-washing lanes
- forcing `eri` or `allocationlab` into deep implementation before member boundaries are clear
- creating a huge neutral package namespace for everything

## Practical success condition

The next round is successful if we end up with:
- a standard for what a package/member is
- obvious future landing zones
- one or two seeded package/member identities
- at least one real bounded migration slice that follows the new model

## Bottom line

The next phase should not be "extract more random helpers."
It should be:
- define the standards
- expose the workspace shape
- seed real package/member identities
- prove the model with one bounded migration
