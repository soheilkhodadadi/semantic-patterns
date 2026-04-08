# AI-Washing Track A Classifier Boundary Benchmark Plan V1

## Purpose

This note turns the revised A/S probe slice into a reusable benchmark plan for
the next classifier-upgrade cycle.

## Fixed benchmark asset

Use:
- [ai_washing_classifier_as_probe_benchmark_v2.csv](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv)

This is a small fixed slice designed to stress exactly the boundary types that
are currently hurting agreement:
- current capability vs future intent
- build / integrate / invest vs already deployed use
- risk / competition context
- internal operating use vs generic tooling references

## Why this matters

The benchmark is small enough to iterate quickly, but structured enough to tell
us something useful.

It is not a substitute for:
- held-out evaluation
- formal IRR

It is a fast calibration surface.

## Recommended uses

### 1. Rubric benchmarking

Use the fixed slice to compare:
- current rubric
- revised two-gate rubric
- any further tie-breaker refinements

### 2. Prompt or API benchmarking

This slice is also a good fit for the existing director playbook:
- `prompt_boundary_benchmark`

That is the right playbook when:
- overall model quality is acceptable enough to continue
- but one narrow boundary is underperforming

### 3. Sub-agent diagnostics

Use the same fixed slice for small blinded sub-agent passes under different
rubric versions.

This is useful for:
- spotting unstable instructions
- identifying rows where the rubric is still too vague

It is **not** a replacement for human IRR.

## Suggested benchmark sequence

1. apply the revised rubric to the fixed slice
2. run one or two sub-agent or prompt variants on the same rows
3. compare agreement against the revised labels
4. if the rubric still looks unstable, refine the rubric again
5. if the rubric looks stable, move to training-set cleanup and retraining

## Success signal

The benchmark has done its job if:
- disagreement becomes concentrated in fewer rows
- the remaining disagreements are understandable, not chaotic
- current operating-use rows stop being confused with investment or future
  intent rows

## Bottom line

The fixed `16`-row A/S probe slice is now a reusable calibration artifact.

That means the next classifier work can be benchmark-driven rather than
intuition-driven.
