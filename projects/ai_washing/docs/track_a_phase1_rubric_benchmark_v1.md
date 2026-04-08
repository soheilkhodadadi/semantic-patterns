# AI-Washing Track A Phase 1 Rubric Benchmark V1

## Purpose

This note starts Phase 1 of the classifier upgrade roadmap on a fixed and
reusable benchmark surface.

It also records the selected director playbook:
- `prompt_boundary_benchmark`

That playbook is the right fit because the current weakness is concentrated in
the `Actionable` / `Speculative` boundary rather than a broad extraction or
corpus-quality failure.

## Frozen benchmark assets

Benchmark asset:
- `reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv`

Blinded benchmark asset for sub-agent or prompt probes:
- `reports/final/ai_washing_classifier_as_probe_benchmark_blinded_v1.csv`

Benchmark summary:
- `reports/final/ai_washing_classifier_as_probe_benchmark_v2.json`

These replace the earlier handwritten `v1` benchmark CSV, which is no longer
the preferred surface because unquoted commas in the sentence field made it
unsafe as a machine-readable artifact.

## Current benchmark posture

The fixed slice contains `16` rows with revised adjudicated labels:
- `Actionable`: `4`
- `Speculative`: `8`
- `Irrelevant`: `4`

Relative to the older reference labels, the revised rubric changes `6 / 16`
rows:
- `Speculative -> Irrelevant`: `3`
- `Actionable -> Speculative`: `2`
- `Actionable -> Irrelevant`: `1`

The unchanged rows are `10 / 16`:
- `Actionable -> Actionable`: `4`
- `Speculative -> Speculative`: `6`

This is a healthy pattern.

It suggests the revised rubric is not relabeling the slice chaotically.
Instead, it is tightening exactly where we expected:
- present capability vs future intent
- present capability vs acquisition / competition / dependency context

## Variant set for Phase 1

### Variant A. Revised two-gate rubric

Use the current revised posture:
1. relevance gate
2. currentness gate
3. business-claim gate

Expected behavior:
- preserve strong current-capability rows as `Actionable`
- move future-intent and build/integrate rows toward `Speculative`
- keep acquisition, competition, and dependency context as `Irrelevant`

### Variant B. Stricter current-business-claim rubric

Use a slightly stricter posture:
- require an explicit present-tense claim by the reporting firm
- treat generic metric/model/tooling language as `Irrelevant` unless it
  clearly supports a current business or operating function
- keep future build/integrate/invest language as `Speculative`

Expected use:
- stress-test whether a stricter boundary reduces ambiguity or becomes too
  conservative on legitimate current-use rows

## Success condition

Phase 1 is succeeding if:
- disagreement concentrates into fewer rows
- the remaining disagreement is understandable rather than chaotic
- strong current operating-use rows stay stable
- future-intent rows stop drifting into `Actionable`

## Stop condition

Stop the prompt/rubric-only path if:
- the variant labels drift unpredictably
- the stricter posture starts harming obvious current-capability rows
- improvements come only from relabeling too much of the slice as
  `Irrelevant`

## Next execution step

Run one or two blinded sub-agent benchmark passes on the frozen `16`-row slice
using the variant set above.

Then compare:
- agreement with revised benchmark labels
- error concentration by failure mode
- whether the stricter variant is genuinely cleaner or just more conservative

## Bottom line

Phase 1 is now anchored to a clean fixed benchmark and a named playbook.

That gives us a much better loop than before:
- freeze the slice
- test variants deterministically
- keep only the variants that improve the boundary without creating new noise

## Execution result

Completed on the frozen blinded slice:
- `reports/final/ai_washing_classifier_as_probe_variant_a_labels_v1.csv`
- `reports/final/ai_washing_classifier_as_probe_variant_b_labels_v1.csv`
- `reports/final/ai_washing_classifier_as_probe_variant_a_score_v1.json`
- `reports/final/ai_washing_classifier_as_probe_variant_b_score_v1.json`

Observed result:
- Variant A (`variant_a_two_gate_v1`): `16 / 16` match, accuracy `1.00`
- Variant B (`variant_b_strict_current_claim_v1`): `16 / 16` match, accuracy
  `1.00`

This is a meaningful signal.

It says the revised benchmark labels are stable enough that two independent
blinded passes reproduced them exactly on the fixed slice.

## Critical interpretation

This does **not** yet mean the broader classifier problem is solved.

What it does mean:
- the revised rubric is coherent on the current boundary probe
- the benchmark surface is usable for deterministic iteration
- the stricter current-business-claim posture does not obviously break the
  strong positive cases on this slice

What it does **not** tell us yet:
- whether the stricter variant is actually better than Variant A on a broader
  reviewed pack
- whether the model can learn the revised boundary cleanly after retraining
- whether held-out or IRR performance will move enough on a larger sample

The fixed `16`-row slice is now good for calibration, but it is too small to
choose a winner between Variant A and Variant B because both variants converge
to the same labels here.

## Updated next step

Move to Phase 2:
- build a slightly larger reviewed boundary pack
- make sure it includes more rows from:
  - generic metric or tooling references
  - current capability vs present-tense packaging
  - current process vs future integration language
- rerun Variant A and Variant B on that larger pack before retraining

The current default posture should remain:
- Variant A as the main revised rubric
- Variant B as a stricter stress test, not yet the new default
