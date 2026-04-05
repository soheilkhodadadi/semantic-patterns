# Restructure Parallel Protocol V1

## Purpose

This protocol translates the current lab design into a faster short-term migration model.

The goal is not parallelism for its own sake.
The goal is to move faster without losing control of:
- source of truth
- safety and privacy boundaries
- active AI-washing continuity
- migration traceability

## Bottom line

From this point forward, the restructure should run in parallel batches, not only one file family at a time.

But the parallelism should be structured.

The right model is:
- one serialized control-plane lane
- several bounded parallel implementation lanes
- one end-of-batch acceptance gate

## The rule set

### Rule 1. Control plane stays serialized

These should not be edited in uncontrolled parallel bursts:
- boundary memos
- source-of-truth maps
- artifact policy
- schemas
- project registry
- migration wave notes

Reason:
- these define the meaning of the migration itself
- conflicting edits here create invisible drift

### Rule 2. Low-blast-radius code moves can run in parallel

These are good candidates for parallel batches:
- low-level shared helper extraction
- compatibility shim creation
- tests for extracted helpers
- README pointer updates in local areas
- adapter framing notes and project-scoped orientation docs

Reason:
- bounded file sets
- easy to validate
- easy to back out

### Rule 3. Adapter semantics stay serialized by project

Within a given project, semantic changes should be serialized.

For example, do not run two overlapping migrations at once for:
- AI-washing taxonomy and outputs
- ERI taxonomy and scoring semantics
- AllocationLab ontology and scenario semantics

Reason:
- these changes are conceptually coupled even if files differ

### Rule 4. End-of-batch gates are mandatory

Every parallel batch should finish with:
- staged diff review
- targeted tests
- lint/format on touched Python files
- migration-note update if the steady-state story changed
- explicit note of what remained intentionally untouched

### Rule 5. Parallel batches need declared write ownership

Before a parallel batch starts, each slice should declare:
- its write scope
- its expected authoritative lane impact
- whether it requires a control-plane note update at merge time

Reason:
- parallel speed is useful only if ownership is explicit
- this prevents two safe-looking batches from colliding indirectly

## Recommended short-term workstreams

### Workstream A. Shared contracts

Focus:
- `docs/lab/schemas/`
- `labcore/manifests/`
- `labcore/evidence/`
- `labcore/evaluation/`

Objective:
- define manifest and evidence contracts before broader code movement

Parallel-friendly?
- yes, if split by contract family

Suggested batch shape:
- one contract note
- one minimal code representation where justified
- one focused test file

### Workstream B. Adapter namespace preparation

Focus:
- `docs/projects/*`
- future `src/semantic_ai_washing/adapters/*`

Objective:
- make adapter boundaries real enough to host later code migrations

Parallel-friendly?
- yes, by project

Suggested batch shape:
- one project per batch
- one namespace or placeholder module
- one mapping note for what stays legacy vs what moves later

### Workstream C. Caller migration from shims to `labcore`

Focus:
- low-risk import migrations for code that can use `labcore` directly

Objective:
- start proving that shared helpers are not just extracted but actually shared

Parallel-friendly?
- yes, by caller family

Suggested batch shape:
- one helper family at a time
- one caller cluster at a time
- always keep shims until all intended callers are stable

### Workstream D. Artifact-lane normalization

Focus:
- `docs/projects/*`
- `reports/projects/*`
- `data/processed/projects/*`
- `output/*/projects/*`

Objective:
- make future project outputs land in the right places by default

Parallel-friendly?
- yes, mostly by project

Suggested batch shape:
- one project lane at a time
- move only newly authoritative artifacts, not historical bulk outputs

## What should remain serialized for now

Keep these serialized until the contracts are clearer:
- manifest contract design
- evidence-unit contract design
- any package-namespace question
- any deletion or archival of legacy lanes
- AI-washing flagship output moves that risk breaking the active paper lane

## End-of-batch acceptance gate

Every parallel batch should close with the same checklist.

### Gate A. Control-plane alignment
- Does the batch still match the current boundary memo and target layout?
- If not, did the migration note get updated?

### Gate B. Source-of-truth alignment
- Did any authoritative path change?
- If yes, is there a mapping note or registry update?

### Gate C. Validation
- `make doctor` if environment-sensitive code moved
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- targeted `pytest` for the touched slice

### Gate D. Safety and privacy
- No private material normalized into tracked docs
- No accidental lane-crossing for project-sensitive artifacts
- No bulk delete without replacement path

### Gate E. Compatibility
- If code was extracted, do compatibility shims still exist where needed?
- Are old callers still stable?

### Gate F. Ownership and merge sanity
- Did two parallel slices touch the same authoritative file or lane?
- If yes, was that collision intentional and resolved explicitly?
- Is the merge order recorded if one slice logically depended on another?

## Where Director should be used

Director is useful here as a migration-control system, not something to dismantle.

Use Director discipline for:
- wave notes
- runbook-style batching
- gate definitions
- blocker logging when a migration slice exposes deeper coupling
- reusable playbooks when the same restructure blocker appears repeatedly

Immediate opportunity:
- add restructure-specific playbooks once the first repeated blocker patterns are clear
- for example: shim-first extraction, mapping-before-move, contract-before-migration

## Suggested short-term execution map

### Round 1. Contract round
Serialized:
- manifest contract note
- evidence contract note

Parallel:
- minimal code placeholders for contract families if justified
- README/control-plane pointer updates

### Round 2. Adapter round
Parallel by project:
- AI-washing namespace prep
- ERI namespace prep
- AllocationLab namespace prep

Serialized gate:
- adapter registry update only after all three project slices are reviewed

### Round 3. Caller-migration round
Parallel by helper family:
- runtime callers
- audit callers
- security callers
- responses callers

Serialized gate:
- verify compatibility shims still cover untouched callers

### Round 4. Artifact-lane round
Parallel by project:
- docs lane normalization
- reports lane normalization
- output lane normalization

Serialized gate:
- update authoritative mapping sheet and registry pointers

## What success looks like

Success is not that everything moved quickly.
Success is that we can move faster while still being able to answer:
- what changed?
- what stayed authoritative?
- what is safe to parallelize next?
- what should still wait?

## Bottom line

The repo is ready to stop doing only one-file-family-at-a-time migrations.

The next effective mode is:
- parallel bounded workstreams
- serialized control-plane decisions
- one explicit acceptance gate at the end of each batch

That gives us the speed-up you want without giving up the safety that made the first rounds work.
