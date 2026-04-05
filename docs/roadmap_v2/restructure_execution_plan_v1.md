# Restructure Execution Plan V1

## Purpose

This document converts the lab architecture work into a staged migration plan.

It is designed to let the repo evolve safely while:
- AI-washing remains active
- new projects may start soon
- the repo becomes easier to use for a team

## Migration philosophy

The restructure should follow four rules:
1. do not break the active flagship lane
2. create new authoritative lanes before deleting old ones
3. promote to shared core only after real reuse
4. keep each migration wave bounded, reviewable, and reversible

## Overall strategy

The migration will happen in waves.

Each wave should have:
- a narrow objective
- a bounded file set
- a clear acceptance gate
- explicit non-goals

## Wave map

### Wave 0. Stabilize and branch

Status:
- complete

Objective:
- checkpoint the current AI-washing and roadmap work
- merge it into `main`
- create a new restructure branch

Outcome:
- current baseline is preserved
- restructure work begins from a clean branch

### Wave 1. Control-plane setup

Objective:
- define the lab operationally before moving code

Deliverables:
- engine boundary memo
- source-of-truth map
- artifact policy
- project registry
- target repo layout
- migration plan

Acceptance gate:
- a collaborator can tell what is authoritative, what is transitional, and what belongs to which project lane

Non-goals:
- moving application code
- renaming the package
- deleting legacy lanes

### Wave 2. Directory and artifact lane creation

Objective:
- create the future lane structure with minimal logic movement

Expected work:
- create tracked documentation folders under `docs/lab/` and `docs/projects/`
- create project output lanes under `reports/projects/` and `output/*/projects/`
- create shared output lanes under `reports/registry/` and `output/*/shared/`
- document authoritative destinations for future outputs

Acceptance gate:
- future assets have clear homes before code migration begins

Non-goals:
- large refactors inside `src/semantic_ai_washing/`
- moving historical artifacts in bulk without a mapping sheet

### Wave 3. Shared-core surfacing

Objective:
- identify and extract a small set of truly shared utilities and contracts

Expected work:
- create initial `labcore/` skeleton under `src/semantic_ai_washing/`
- move only clearly cross-project helpers or wrappers into shared lanes
- keep project-specific semantics in existing lanes
- add adapter framing without forcing major code moves

Acceptance gate:
- at least one shared-core module exists with clear justification from more than one project need

Non-goals:
- fully neutral package extraction
- treating all current data/classification/analysis code as shared core

### Wave 4. Adapter framing

Objective:
- define project-specific boundaries clearly enough to support parallel work

Expected work:
- create adapter notes or thin code namespaces for:
  - AI-washing
  - ERI
  - AllocationLab
- map each project to corpus, taxonomy, benchmark, scoring, and delivery outputs
- clarify what each adapter reuses from shared core

Acceptance gate:
- project responsibilities are legible to a collaborator without chat history

Non-goals:
- full implementation of ERI or AllocationLab

### Wave 5. Delivery and onboarding normalization

Objective:
- make the lab usable by assistants or collaborators

Expected work:
- onboarding note
- runbook map
- artifact naming conventions
- handoff checklist for a new project
- first shared reporting discipline note

Acceptance gate:
- a new contributor can follow the control plane and deliver into the right lanes

## Safety rules for every wave

### Rule 1. Preserve AI-washing continuity
Any move that risks breaking the active AI-washing lane must be deferred or isolated.

### Rule 2. No bulk deletion without replacement map
Before removing or archiving legacy lanes, document:
- replacement path
- reason
- last known authoritative alternative

### Rule 3. One acceptance gate per wave
Do not stack multiple ambiguous migrations together.

### Rule 4. Package rename is deferred
Do not rename the package namespace during early waves.

### Rule 5. Private materials stay local
Project-sensitive materials for partner/interview work stay under `local_private/` and are not normalized into tracked docs.

## Validation expectations

For migration work, validation should combine:
- repo-structure checks
- documentation sanity checks
- lint/tests when code changes happen
- targeted smoke checks for any moved entrypoints

Baseline commands when code is touched:
```bash
make doctor
make lint
pytest -q
```

## Decision checkpoints

At the end of Wave 2, decide:
- are the new lanes sufficient without code motion yet?

At the end of Wave 3, decide:
- is `labcore/` justified by real reuse, or are docs and wrappers still enough?

At the end of Wave 4, decide:
- are ERI and AllocationLab still architecture/adapter lanes, or is one of them ready for true implementation?

## What success looks like

Success is not a dramatic refactor.
Success is:
- clearer boundaries
- safer parallel work
- easier onboarding
- less ambiguity about outputs and ownership
- the ability to add projects without starting from zero

## Bottom line

The restructure should happen as staged boundary-setting plus selective promotion, not as a one-shot rewrite.
