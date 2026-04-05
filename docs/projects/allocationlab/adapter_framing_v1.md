# AllocationLab Adapter Framing V1

## Purpose

This note defines the initial adapter boundary for AllocationLab.

AllocationLab is strategically important, but it should begin as an architecture-first adapter rather than an immediate full implementation lane.

## Current mode

- architecture and synthetic-case lane
- public-safe tracked notes only where appropriate
- local-private strategy and partner-sensitive materials remain under `local_private/projects/allocationlab/`

## Adapter role

The AllocationLab adapter should define the domain boundary for a future decision-system program without forcing the lab to implement that program too early.

## What the adapter is expected to own

### Domain scope
- project ontology
- scenario logic
- financing and ranking layer concepts
- synthetic case structure

### Benchmark and evaluation semantics
- synthetic-case validation rules
- architecture checkpoints and dependency maps

### Delivery surface
- architecture memos
- ontology summaries safe for the tracked repo
- project dependency and gap maps

## What the adapter should reuse

Most plausible shared dependencies:
- lane resolution from `semantic_ai_washing.labcore.registry.lanes`
- shared runtime helpers from `semantic_ai_washing.labcore.runtime`
- later, possibly shared manifest/evidence/reporting contracts once proven reusable

## What should remain out of scope for now

Do not treat AllocationLab as ready to inherit:
- AI-washing taxonomy or label logic
- AI-washing panel construction and empirical tables
- ERI-style disclosure reliability semantics
- heavy build commitments before staffing and charter are explicit

## Near-term output contract

Tracked outputs should remain architecture-first:
- adapter framing notes
- architecture memos safe for the repo
- synthetic-case definitions
- dependency maps and staged implementation notes

## Bottom line

AllocationLab should enter the lab as a bounded architecture adapter.
That keeps the lane active without letting it sprawl into premature implementation.
