# Fresh Authority Comparison V12

## Purpose

Choose the Queue V9 opener after Queue V8 completed cleanly.

## Candidates compared

1. `ai_washing_member.labeling.publish_preliminary_results_readiness`
2. `semantic_director.cost`

## Candidate A: `ai_washing_member.labeling.publish_preliminary_results_readiness`

Why it is attractive:
- it stays inside the current-stage IRR/preliminary-results workflow
- it already depends only on member-owned labeling helpers plus local report artifacts
- direct caller pressure is concentrated in `tests/test_irr_phase2.py`
- roadmap-model command strings can stay on the compatibility path for now

Risk shape:
- low
- one direct workflow gate
- no Atlas-adjacent boundary pressure

## Candidate B: `semantic_director.cost`

Why it is attractive:
- high leverage surface for future `director` control-runtime work
- downstream of already-canonical audit/runtime/schema surfaces
- likely opens a clean `semantic_director.llm` follow-on round

Risk shape:
- medium
- direct caller pressure spans `director` plus `ai_washing` assistive workflows
- best handled after an `ai_washing` opener so the cycle stays balanced

## Decision

Chosen Queue V9 opener:
- `ai_washing_member.labeling.publish_preliminary_results_readiness`

## Why this wins now

It is the cleaner opener.

It keeps the current-stage IRR workflow moving in the flagship member lane,
uses a compact regression gate, and avoids opening the broader cross-lane cost
surface before the cycle is underway.

`semantic_director.cost` remains the stronger planned `director` rotation for
Batch 2, with `semantic_director.llm` as the downstream follow-on if the cost
boundary stays clean.
