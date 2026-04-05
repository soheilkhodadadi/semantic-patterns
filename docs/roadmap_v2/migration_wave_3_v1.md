# Migration Wave 3 V1

## Purpose

Wave 3 surfaces the first genuinely shared code layer without pretending that the whole repo is already a platform.

The rule for this wave is deliberately conservative:
- create `labcore/`
- add one minimal shared-core module that is already justified by the new lab layout
- keep domain semantics and project logic where they currently belong

## Precondition

Before any code movement, the active AI-washing artifact lanes are mapped here:
- `docs/lab/migration/ai_washing_legacy_to_new_mapping_v1.md`

That mapping sheet is the guardrail for this wave.

## Wave objective

Create the first `src/semantic_ai_washing/labcore/` skeleton and define the smallest believable shared-core candidate set.

## Minimal candidate set

### Candidate 1. Project and shared lane resolution
Status:
- implement now

Why it qualifies:
- the new lab structure already needs a project-agnostic way to refer to project lanes and shared lanes
- this is useful for AI-washing now and likely for ERI and AllocationLab later
- it encodes structure, not domain semantics

Implementation lane:
- `src/semantic_ai_washing/labcore/registry/lanes.py`

### Candidate 2. Manifest contracts and manifest helpers
Status:
- candidate only, do not move yet

Potential source pressure:
- `semantic_ai_washing.data.*` manifest builders
- manifest handling already appears in sentence-pool, labeling, and expansion workflows

Why not move yet:
- current manifest logic is still too entangled with AI-washing corpus semantics
- ERI reuse is not proven yet

### Candidate 3. Evaluation payload envelopes
Status:
- candidate only, do not move yet

Potential source pressure:
- `reports/evaluation/`
- `reports/models/`
- `labeling/publish_preliminary_results_readiness.py`

Why not move yet:
- we have shared-looking evaluation outputs, but not yet a cross-project contract that is stable enough to extract

### Candidate 4. Delivery destination helpers
Status:
- candidate only, do not move yet

Potential source pressure:
- delivery builders under `semantic_ai_washing.analysis`
- project/shared output lanes created in Wave 2

Why not move yet:
- current delivery builders are still AI-washing-centric and paper-centric
- extracting them now would be premature

## Likely next extraction set after the first seed

Once the lane-resolution seed proves useful, the next safest cross-project candidates are likely leaf utilities from `director/core/`, not analytical pipeline code.

Most plausible follow-on candidates:
- runtime and filesystem helpers now concentrated in `director/core/utils.py`
- append-only audit payload helpers in `director/core/audit.py`
- secret-redaction and tracked-file scanning helpers in `director/core/security.py`
- lightweight OpenAI Responses transport helpers in `director/core/openai_responses.py`

Why these are better follow-on candidates:
- they are low-level
- they have weak coupling to AI-washing semantics
- they are more reusable across multiple programs than the current analysis stack

Still defer for now:
- `director/core/cost.py`

Reason:
- it depends on current director schemas and is one layer less clean than the four modules above

## Explicit non-candidates for Wave 3

These remain project-specific for now:
- sentence classification logic
- labeling workflows and rubric semantics
- AI patent extraction and keyword logic
- panel-building and regression logic
- AI-washing-specific credibility and mismatch constructs
- manuscript table and figure generation logic

## Acceptance gate

Wave 3 is complete when:
- `src/semantic_ai_washing/labcore/` exists as a real package skeleton
- at least one small shared-core module exists with a defensible multi-project rationale
- the repo still treats AI-washing semantics as project-specific rather than forcing them into shared core

## Bottom line

Wave 3 should prove discipline, not ambition.
If we cannot name a small shared module cleanly, we should not extract a large one.
