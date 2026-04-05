# Migration Round D: AI-Washing Member Lane Normalization V1

## Purpose

This note records the first member-facing normalization slice for `ai_washing`.
The goal is to make the project member's future lanes visible and usable without disturbing current manuscript and analysis authority.

## What changed

The repo now has explicit `ai_washing` project sub-lanes under:
- `reports/projects/ai_washing/`
- `output/doc/projects/ai_washing/`
- `output/figures/projects/ai_washing/`
- `data/processed/projects/ai_washing/`

Each lane has a local README that explains:
- what belongs there
- what still stays authoritative in legacy lanes
- how fresh project-scoped work should be routed

## Why this is the right first normalization step

This slice is intentionally light.
It creates project-owned destinations before any builder or artifact moves happen.
That keeps the live AI-washing paper lane stable while still letting the member model become real in the filesystem.

## What did not change

This slice does **not**:
- move manuscript assets out of `paper/`
- move current analysis notes out of `reports/analysis/`
- move current delivery artifacts out of legacy `output/doc/` and `output/figures/` folders
- change current processed-data authority

## Acceptance gate

This slice is accepted when:
- `ai_washing` has visible project-owned sub-lanes
- each lane has a clear usage rule
- no existing authoritative artifact is displaced by implication

## Follow-on implication

With these lanes in place, the next fresh `ai_washing` artifacts can land in member-owned destinations by default when they are not manuscript-bound or shared-benchmark-bound.

## Bottom line

This is the first filesystem-level normalization step for the `ai_washing` member.
It makes the member real without forcing premature moves.
