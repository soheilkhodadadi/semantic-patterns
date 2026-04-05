# AI-Washing Adapter Framing V1

## Purpose

This note defines how AI-washing should be understood as a project adapter inside the lab structure.

The goal is not to neutralize the project.
The goal is to make its boundaries explicit so the lab can support it without confusing project semantics with shared core.

## Current mode

- flagship publication program
- active empirical and manuscript lane
- mixed public-safe and internal audience

## Adapter role

The AI-washing adapter is the reference implementation for the current lab.
It owns the domain semantics that turn the shared text-analysis workflow into an AI-disclosure credibility research program.

## What the adapter owns

### Corpus scope
- SEC annual filing text in the current AI-washing window
- AI-related sentence extraction from those filings

### Domain taxonomy
- `Actionable`
- `Speculative`
- `Irrelevant`
- AI-focus and composition measures
- `PatentMismatch` logic and downstream AI-washing constructs

### Benchmark and evaluation semantics
- IRR workflow and adjudication rules used for this project
- held-out evaluation framing for the current sentence classifier
- project-specific readiness and technical-audit packaging

### Downstream analysis
- firm-year aggregation
- patent linkage and mismatch logic
- ever-speaker panel construction
- paper-facing tables, figures, and delivery packets

## What the adapter should reuse

Shared-core dependencies that are already plausible:
- lab lane resolution in `semantic_ai_washing.labcore.registry.lanes`
- shared runtime helpers in `semantic_ai_washing.labcore.runtime`
- later, possibly shared manifest, audit, security, and transport helpers once they are extracted cleanly

## What should stay out of shared core

These remain AI-washing-specific unless proven otherwise:
- sentence label semantics
- credibility-metric definitions
- patent matching and AI keyword logic
- panel design choices and empirical timing specifications
- paper-specific reporting builders

## Near-term output contract

The AI-washing adapter should keep producing into the currently authoritative legacy lanes until replacement maps are deliberately enacted.

Current guardrail:
- see `docs/lab/migration/ai_washing_legacy_to_new_mapping_v1.md`

## Bottom line

AI-washing is the benchmark adapter.
It should inform the lab structure, but it should not define the shared core by itself.
