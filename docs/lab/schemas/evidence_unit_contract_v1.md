# Evidence-Unit Contract V1

## Purpose

This note defines the minimum contract for a tracked evidence unit in the lab.

An evidence unit is a structured object that supports a claim such as:
- a classifier met a threshold
- an IRR audit reached a certain level
- a benchmark comparison favored one model over another
- a panel or output passed a validation gate

The goal is to keep validation claims reproducible and legible across projects.

## What counts as an evidence unit

An evidence unit is appropriate when a file's main job is to record a validation or benchmarking result.

Typical examples:
- held-out evaluation reports
- IRR reports
- disagreement diagnostics
- model benchmark matrices
- readiness reports
- future package build or migration validation reports

Current repo anchors include:
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `reports/labels/irr_report.json`
- `reports/models/preliminary_results_readiness_v1.json`

## Required fields

A tracked evidence unit should include these fields.

### Identity
- `evidence_id`
- `evidence_type`
  - for example: `heldout_evaluation`, `irr_audit`, `benchmark_matrix`, `readiness_report`, `migration_check`
- `status`
  - one of: `draft`, `working`, `frozen`, `superseded`, `archived`

### Scope and claim
- `scope`
  - one of: `shared`, `project`
- `project`
  - required when `scope = project`
- `claim_target`
  - what this evidence is about, such as `classifier`, `label audit`, `package member`, `migration slice`

### Provenance
- `generated_at_utc`
- `git_commit`
  - when produced from tracked code
- `producer`
  - script, module, or workflow name

### Inputs
- `inputs`
  - named inputs to the evaluation or audit
- `source_manifest_ids`
  - manifest ids when the evidence depends on pinned manifests

### Outputs and artifacts
- `artifacts`
  - named output paths such as plots, confusion matrices, tables, diagnostics

### Summary
- `summary`
  - compact machine-readable facts needed to interpret the result quickly

## Strongly recommended fields

- `parameters`
- `thresholds`
- `decision`
  - pass, fail, caution, informational
- `privacy_class`
  - one of: `public_safe`, `internal`, `private_local`
- `related_manifest_ids`
- `related_evidence_ids`
- `notes`

## Field expectations

### `evidence_id`
Use a readable and versioned identifier.

Good pattern:
- `heldout_eval_prelim_v2`
- `irr_report_v1`
- `package_member_check_ai_washing_v1`

### `claim_target`
This should say what is being evaluated, not just the project.

Good examples:
- `sentence_classifier`
- `annotation_agreement`
- `workspace_member_seed`
- `migration_slice_runtime_callers`

### `summary`
The summary should expose the main decision facts without requiring the reader to inspect the whole artifact.

Examples:
- accuracy
- macro-F1
- weighted-F1
- Cohen's kappa
- rows evaluated
- pass/fail decision
- missing checks

## Placement rules

### Shared evidence
Default home:
- `reports/evaluation/`
- `reports/models/`
- `reports/labels/`
- later, a normalized shared lane such as `shared/evaluation/`

### Project evidence
Future home:
- `reports/projects/<project>/`
- or a project member evidence lane once project members become real packages

Near-term transition rule:
- keep current authoritative paths until a replacement path is promoted explicitly

## Format guidance

Preferred tracked formats:
- JSON for machine-readable evidence
- Markdown companion note when interpretation or reviewer-facing narrative matters

A good evidence object should be machine-readable first.

## Acceptance checks

An evidence unit is in good shape when:
- it has a stable identity
- the claim target is explicit
- the producer is named
- inputs are named
- artifacts are named if they exist
- the summary contains decision-grade metrics
- the scope and authoritative lane are clear

## Relationship to manifests

A manifest describes an asset boundary.
An evidence unit evaluates or validates something that often depends on one or more manifests.

Example:
- split registry manifest defines the held-out split
- held-out evaluation evidence reports model performance on that split

## Minimal example shape

```json
{
  "evidence_id": "heldout_eval_prelim_v2",
  "evidence_type": "heldout_evaluation",
  "status": "working",
  "scope": "shared",
  "claim_target": "sentence_classifier",
  "generated_at_utc": "2026-03-25T00:00:00+00:00",
  "git_commit": "<commit>",
  "producer": "semantic_ai_washing.tests.evaluate_classifier_on_held_out",
  "inputs": {},
  "source_manifest_ids": [],
  "artifacts": {},
  "summary": {}
}
```

## Bottom line

An evidence unit should let another contributor answer:
- what claim is being supported?
- what inputs did this depend on?
- what metrics or decision facts came out?
- is this stable enough to use in a report, gate, or promotion decision?
