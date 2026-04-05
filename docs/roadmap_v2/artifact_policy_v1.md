# Artifact Policy V1

## Purpose

This policy defines the major artifact classes for the lab and where they should live.

The goal is to prevent confusion when multiple programs are active.

## Principle

Every important artifact should answer four questions clearly:
- what class of artifact is this?
- who is it for?
- is it authoritative or provisional?
- where should it live?

## Artifact classes

### 1. Control-plane artifacts
Purpose:
- define governance, policy, source-of-truth, and project boundaries

Examples:
- roadmap notes
- engine boundary memo
- source-of-truth map
- artifact policy
- project registry

Recommended lane:
- `docs/roadmap_v2/`
- relevant policy anchors under `docs/director/`

### 2. Benchmark artifacts
Purpose:
- define labeled data, IRR subsets, benchmark samples, and adjudication records

Examples:
- labels tables
- IRR subsets
- adjudication outputs
- benchmark manifests

Recommended lane:
- `data/labels/`
- `reports/labels/`
- `data/manifests/`

### 3. Evaluation artifacts
Purpose:
- record model quality, scoring quality, and audit evidence

Examples:
- held-out evaluation reports
- benchmark matrices
- readiness summaries
- calibration summaries

Recommended lane:
- `reports/evaluation/`
- `reports/models/`

### 4. Analysis artifacts
Purpose:
- support project-specific analytical work

Examples:
- panels
- regression outputs
- project-specific derived datasets
- analytical QC notes

Recommended lane:
- `data/processed/`
- `results/`
- `reports/analysis/`

### 5. Delivery artifacts
Purpose:
- present results to humans in polished form

Examples:
- docx tables
- figures
- review packets
- results scaffolds
- monthly reports

Recommended lane:
- `output/doc/`
- `output/figures/`
- `output/paper/`

### 6. Public-safe proof artifacts
Purpose:
- communicate capabilities externally without exposing private or partner-specific materials

Examples:
- FilingLens proof outputs
- sanitized case studies
- public-safe screenshots or memo samples

Recommended lane:
- tracked docs under `docs/roadmap_v2/`
- selected output objects under `output/` only if cleared as public-safe

### 7. Local-private artifacts
Purpose:
- support interviews, partner engagement, and sensitive planning without putting them in the public repo

Examples:
- partner-specific architecture notes
- interview prep kits
- non-public project Q&A
- organization-specific pilot plans

Recommended lane:
- `local_private/roadmap_v2/`

## Authoritative status markers

Every major artifact should be treated as one of:
- `authoritative`
- `working`
- `archived`
- `superseded`

If practical, these should be indicated in filenames, surrounding notes, or registry tables.

## Promotion rules

### Promote into authoritative lanes when
- validation is complete enough for the intended audience
- the artifact has a clear owner
- the artifact has a stable path and name

### Keep as working when
- the logic is changing quickly
- the audience is internal only
- the artifact depends on incomplete assumptions

### Archive when
- it is useful for traceability but no longer current
- a newer authoritative artifact exists

## Privacy rules

### Public-safe tracked docs may contain
- architecture concepts
- workflow patterns
- public source references
- generic project descriptions

### Public-safe tracked docs must not contain
- confidential partner terms
- NDA-protected details
- private source text copied from sensitive documents
- organization-specific strategy that should remain local

### Local-private docs may contain
- organization-specific notes
- interview prep linked to named organizations
- sensitive implementation strategy
- confidential planning materials

## Delivery rule

Polished tables, figures, and memos are not automatically reusable shared-core assets.
They are delivery artifacts unless and until a broader reusable pattern is extracted from them.

## Bottom line

The lab will stay manageable only if artifacts are classified deliberately.
This policy is the minimal rule set for doing that.
