# Fresh Authority Comparison V22

## Purpose

Choose the Queue V19 opener after Queue V18 completed cleanly.

## Candidates compared

1. `ai_washing_member.labeling.build_irr_boundary_benchmark`
2. `semantic_director.validation_assets`

## Candidate A: `ai_washing_member.labeling.build_irr_boundary_benchmark`

Why it is attractive:
- it is the last remaining active `ai_washing` labeling migration candidate in the triage registry
- it closes the live IRR benchmark publication edge instead of leaving a small but real benchmark surface behind
- it is operationally narrow and has a compact member-local test shape
- it sharpens the meaning of the later validation-asset registry by making the boundary benchmark authority canonical first

Risk shape:
- low
- no direct runtime caller pressure beyond its own CLI-style authority
- one compact data-output regression gate

## Candidate B: `semantic_director.validation_assets`

Why it is attractive:
- it has real downstream value for the `director` validation/reporting lane
- it already has focused regression coverage and a clean package boundary
- it pairs naturally with `semantic_director.script_inventory` as an operational-governance follow-on

Risk shape:
- medium
- it depends on the current validation asset posture, including the IRR boundary benchmark surface
- it is cleaner after the benchmark authority is canonical rather than before

## Decision

Chosen Queue V19 opener:
- `ai_washing_member.labeling.build_irr_boundary_benchmark`

## Why this wins now

It is the cleaner opener.

Queue V18 largely closed the active data lane. Queue V19 should now close the
last active labeling benchmark edge before rotating into the `director`
validation/governance follow-ons.

`semantic_director.validation_assets` remains the stronger planned Queue V19
Batch 2, with `semantic_director.script_inventory` as the Batch 3 closeout if
that validation boundary stays clean.
