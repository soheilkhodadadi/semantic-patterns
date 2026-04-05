# Restructure Parallel Protocol V2

## Purpose

This protocol supersedes the earlier centralized-migration mindset.

The repo is no longer moving toward:
- one dominant shared package tree with attached project lanes

It is moving toward:
- one workspace monorepo
- a small number of shared infrastructure packages
- a small number of package-style project members
- thin shared artifact lanes
- explicit intake and export paths

The goal is to move faster without losing control of:
- source of truth
- packaging boundaries
- privacy and NDA boundaries
- active AI-washing continuity
- migration traceability

## Bottom line

Parallelism is still the right operating model.
But the unit of parallel work has changed.

The right model is now:
- one serialized control-plane and standards lane
- several bounded package/member preparation lanes
- one end-of-batch acceptance gate based on package and workspace readiness

## Core principles

### Principle 1. The replaceable unit is a package-sized module

Do not optimize the migration around tiny helper extraction alone.

Optimize it around units that can later be:
- owned by one contributor
- absorbed from another repo
- exported to another repo
- replaced without deep surgery in unrelated areas

### Principle 2. Shared layers stay thin and stable

Shared packages should own only:
- low-level runtime and infrastructure helpers
- stable contracts
- registries
- delivery primitives only after real reuse is demonstrated

They should not absorb project semantics prematurely.

### Principle 3. Project members are first-class

`ai_washing`, `eri`, and `allocationlab` should be treated as future package-style members, not as optional side folders.

That means the migration should increasingly ask:
- what belongs to the project member?
- what belongs to shared infrastructure?
- what belongs to shared artifact lanes?

### Principle 4. Intake and export are real design paths

Any migration choice that makes future intake or export harder should be treated as suspect.

Acceptable end-state landing patterns are:
- workspace member
- path dependency pending promotion
- private-local member where confidentiality requires it

## Serialized lanes

The following must remain serialized:
- control-plane memos
- source-of-truth policy
- workspace/package standards
- member contract definitions
- shared-vs-project lane definitions
- authoritative path changes
- deletion or archival decisions

Reason:
- if these drift, parallel work becomes fast but incoherent

## Parallel lanes

The following can run in bounded parallel slices once the standards lane is stable.

### Lane A. Shared package hardening

Examples:
- `packages/labcore`
- `packages/director`
- later `packages/labdelivery` only if reuse proves real

Typical work:
- leaf helper migrations
- package-local tests
- package-local README updates
- import cleanup inside clearly owned write scopes

### Lane B. Project member preparation

Examples:
- `projects/ai_washing`
- `projects/eri`
- `projects/allocationlab`

Typical work:
- member README and docs seeding
- placeholder `pyproject.toml` planning
- package identity decisions
- mapping notes for what stays legacy vs what becomes member-owned

### Lane C. Shared artifact lane normalization

Examples:
- `shared/manifests`
- `shared/labels`
- `shared/evaluation`
- `shared/registry`

Typical work:
- define what is genuinely cross-project
- move only newly authoritative assets
- avoid bulk historical movement unless there is a strong payoff

### Lane D. Caller migrations and dependency cleanup

Examples:
- caller migrations from legacy shims to shared packages
- explicit dependency declarations for future members
- path/workspace dependency trial moves

Typical work:
- one caller family at a time
- one dependency edge at a time
- compatibility shims remain until direct callers are stable

## Package and workspace standards gate

Every nontrivial migration batch should be checked against package/workspace readiness, not just repo-local convenience.

### Gate A. Metadata and structure
- Does the affected package or future member have a clear package identity?
- Is there a `pyproject.toml` plan or real file where appropriate?
- Does the structure stay simple enough to follow standard `src/` layout guidance?
- Is the package/member README authoritative for its scope?

### Gate B. Dependency clarity
- Are dependencies explicit?
- Is the slice correctly treated as a workspace member, path dependency, or legacy lane?
- Did we avoid deep informal imports into another package or member's private internals?

### Gate C. Shared-vs-project placement
- Did anything project-specific accidentally migrate into a shared lane?
- Did anything truly shared remain buried inside one project without good reason?

### Gate D. Build and test readiness
- If a member or package becomes buildable, can it satisfy a basic packaging flow?
- Are tests localizable to the touched package/member?
- Are validation commands scoped enough that another contributor can run them without understanding the full repo?

Suggested command profile once a slice is mature enough:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `pytest`
- `uv build --package <name> --no-sources` or `python -m build <path>` once that package/member is explicitly buildable
- `uv sync --package <name>` once real workspace metadata exists

### Gate E. Privacy and intake/export safety
- No private material normalized into tracked docs
- No project-private logic moved into shared scope by accident
- The slice would still make sense if copied out or received from another repo

### Gate F. Compatibility and continuity
- Are legacy imports still supported where they must remain?
- Did we preserve the active AI-washing paper lane?
- If authority changed, was the mapping or registry updated?

## Standards we should align to

The migration should prefer established packaging standards instead of inventing one-off local conventions.

The most relevant current anchors are:
- `pyproject.toml` as the packaging/configuration anchor
- `src/` layout for package/member code
- per-package or per-member `tests/`
- workspace-member metadata when a shared lockfile and common tooling are justified
- path dependencies where a looser coupling is safer than forcing full workspace membership
- explicit build validation before treating a member as export-ready

These come directly from current official Python packaging and workspace guidance.

## Recommended short-term operating pattern

### Stage 1. Define standards first
Serialized:
- workspace-member contract
- shared artifact/evidence contract
- package/member acceptance gate

### Stage 2. Prepare bounded members and packages
Parallel:
- shared package hardening
- project member scaffolding
- shared artifact lane definition

### Stage 3. Migrate through declared edges
Parallel:
- one caller family per batch
- one project member prep slice per batch
- one artifact family per batch

Serialized gate:
- update mappings, registry, and authoritative notes only after slices are reviewed together

## Where Director still helps

Director remains valuable as:
- the control-plane discipline
- the runbook and playbook lane
- the gate-definition lane
- the blocker-tracking lane

Director should not force all project logic into itself.
It should help coordinate the lab, not swallow the lab.

## Bottom line

V1 helped us start the migration.
V2 gives us the right operating rule for the next phase:

- standards first
- package-sized units
- project members as first-class
- shared layers thin
- parallel work only after boundaries are explicit
