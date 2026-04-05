# ERI Adapter Framing V1

## Purpose

This note defines how ERI should enter the lab as a project adapter.

ERI is the first real test of whether the lab can reuse the current workflow in a different disclosure domain without pretending the domains are the same.

## Current mode

- incubation and pilot lane
- public-safe tracked notes only where appropriate
- local-private materials remain under `local_private/projects/eri/`

## Adapter role

The ERI adapter should reuse the lab's workflow discipline while supplying a new disclosure reliability ontology.

## What the adapter is expected to own

### Corpus scope
- environmental and climate-related corporate disclosures, once corpus scope is finalized

### Domain taxonomy
- ERI-specific disclosure reliability categories
- project-specific evidence rules and scoring semantics

### Benchmark and evaluation semantics
- human review and calibration rules appropriate to ERI
- project-specific benchmark slices and quality gates

### Downstream analysis and delivery
- project-specific reliability outputs
- pilot deliverables and interview-ready proof materials once cleared for tracking

## What the adapter should reuse

Most plausible shared dependencies:
- lane resolution from `semantic_ai_washing.labcore.registry.lanes`
- shared runtime helpers from `semantic_ai_washing.labcore.runtime`
- future manifest/evidence/evaluation contracts if they become genuinely cross-project

## What should not be assumed yet

Do not assume ERI will reuse without change:
- AI-washing sentence labels
- AI patent validation logic
- current panel and regression portfolio logic
- paper-specific AI-washing delivery builders

## Near-term output contract

Tracked repo-safe outputs should stay lightweight at first:
- public-safe project brief
- taxonomy framing note if cleared
- dependency map and pilot runbook

Sensitive partner or interview material stays local-private.

## Bottom line

ERI should be the first serious reuse test, not a forced clone of AI-washing.
The adapter boundary should protect that distinction.
