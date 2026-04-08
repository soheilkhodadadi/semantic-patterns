# AI-Washing Track A A/S Rubric Probe Adjudication V1

## Purpose

This note records the first concrete adjudication pass using the revised
`Actionable` / `Speculative` rubric from the `16`-row probe slice.

It is not a final IRR result. It is a bridge between the rubric rewrite and the
next benchmark cycle.

## Inputs

- revised rubric:
  - `projects/ai_washing/docs/track_a_as_rubric_rewrite_v1.md`
- original probe slice:
  - `reports/final/ai_washing_classifier_rubric_probe_slice_v1.csv`
- adjudicated probe slice:
  - `reports/final/ai_washing_classifier_rubric_probe_slice_revised_labels_v1.csv`

## Revised label mix

First-pass adjudication on the `16`-row slice gives:
- `Actionable`: `4`
- `Speculative`: `8`
- `Irrelevant`: `4`

This is a healthier pattern than the earlier looser boundary because it
separates:
- current present-tense business or operating use
- investment / build / integrate / future-intent language
- AI context that is not actually a firm capability disclosure

## What changed most

### Rows that remain `Actionable`

These are the strongest current-use cases:
- infrastructure or product capability that currently enables AI workflows
- current internal operating processes that explicitly rely on ML/AI

Examples:
- AI-enabled origination and risk analysis
- storage/infrastructure for AI/ML workflows
- risk-management or measurement processes that currently use ML

### Rows that move to `Speculative`

These are now more consistently treated as not-yet-current:
- investment priorities
- build / integrate / implement language
- ongoing R&D plus possible future use

This matters because the prior boundary was too permissive whenever a sentence
was detailed or ambitious.

### Rows that move to `Irrelevant`

These are now treated more strictly:
- competition context
- adoption risk / dependency context
- acquisition or ownership references

That tightening is important because these sentences mention AI but often do
not disclose a present AI capability by the reporting firm.

## What this implies for the next step

The next classifier gain should start with:
1. rubric benchmark pass using this revised boundary
2. only then targeted training-set cleanup or expansion
3. probability tuning after the rubric and labels are cleaner

## Bottom line

The revised rubric is doing useful work already.

It is turning a blurry `Actionable` / `Speculative` boundary into a three-way
decision that is easier to defend:
- current concrete use -> `Actionable`
- relevant but not yet current -> `Speculative`
- AI context without a capability claim -> `Irrelevant`
