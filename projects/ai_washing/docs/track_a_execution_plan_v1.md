# AI-Washing Track A Execution Plan V1

## Purpose

Track A is the first execution track of the AI-washing publication-upgrade
phase.

Its job is to make the empirical backbone ready for the next paper round by
stabilizing:
- the refreshed filing window
- the sentence/classification layer
- the first economics-facing design choices

## Scope

Track A includes:
1. 2025 filing refresh
2. classifier accuracy and robustness refresh
3. capital-market design preparation
4. event-study candidate preparation
5. identification design selection

Track A does not include:
- full paper rewriting
- final table package production
- ERI or AllocationLab execution

## Work packages

### A1. 2025 filing refresh

Objective:
- bring the live filing backbone up to date

Tasks:
- confirm the 2025 filing source location and coverage
- compare the 2025 filing format with the current ingestion assumptions
- run refreshed indexing/extraction/classification planning
- define the exact rebuild path for downstream measures and panels
- audit filing-date availability for later event-study use
- audit patent timing and source-window requirements before panel rebuild

Deliverables:
- 2025 refresh readiness note
- updated refresh command path
- explicit output targets for refreshed sentence/classification/panel artifacts
- filing-date and patent-window audit note
- patent refresh source review note

Primary dependencies:
- filing access
- existing SEC indexing and sentence extraction surfaces

### A2. Model accuracy and robustness refresh

Objective:
- make the classification layer more defensible before the next paper round

Tasks:
- rerun current held-out evaluation on the active backbone
- define candidate model-improvement path if worthwhile
- define robustness lanes:
  - human-labeled subset
  - high-confidence subset
  - confidence/threshold sensitivity

Deliverables:
- current model state summary
- robustness plan
- decision on whether a model-upgrade pass is worth the time cost now

Primary dependencies:
- current evaluation assets
- current benchmark/model runtime surfaces

### A3. Capital-market consequence design prep

Objective:
- move from a disclosure-validation story toward an economically consequential
  story

Tasks:
- list feasible market-data inputs
- define the main candidate dependent variables
- choose the first serious test to implement
- decide whether daily or monthly data are appropriate for the first event-study lane
- decide whether WRDS merged CCM tables can replace the older split controls path

Current preferred first candidate:
- filing-date market reaction / event-study lane

Deliverables:
- capital-market design note
- required data dependency list
- first chosen test
- market-data source review note

### A4. Identification design selection

Objective:
- choose a defensible next-step identification design

Tasks:
- assess ChatGPT release as the leading candidate shock
- define the identification logic and failure modes
- compare it against any cleaner alternative that appears during scoping

Deliverables:
- identification candidate note
- explicit go/no-go selection for the first design

### A5. Execution checkpoint

Objective:
- close Track A with a clear decision on whether the project is ready to move
  into larger empirical execution

Checkpoint questions:
- is the 2025 refresh path executable?
- is the model layer credible enough to proceed?
- is there a concrete first capital-market test?
- is there a chosen identification path?

Deliverable:
- Track A checkpoint note

## Recommended order

1. A1. 2025 filing refresh
2. A2. Model accuracy and robustness refresh
3. A3. Capital-market consequence design prep
4. A4. Identification design selection
5. A5. Execution checkpoint

## Immediate next artifacts

The next concrete artifacts to create or refresh after this plan are:
- `projects/ai_washing/docs/track_a_2025_refresh_readiness_v1.md`
- `projects/ai_washing/docs/track_a_filing_date_and_patent_window_audit_v1.md`
- `projects/ai_washing/docs/track_a_patent_refresh_source_review_v1.md`
- `projects/ai_washing/docs/track_a_market_data_source_review_v1.md`
- `projects/ai_washing/docs/track_a_model_robustness_plan_v1.md`
- `projects/ai_washing/docs/track_a_capital_market_design_v1.md`
- `projects/ai_washing/docs/track_a_identification_candidate_review_v1.md`

Current A1 anchor:
- `projects/ai_washing/docs/track_a_2025_refresh_readiness_v1.md`
- `projects/ai_washing/docs/track_a_2025_source_staging_v1.md`
- `projects/ai_washing/docs/track_a_2025_refresh_contract_v1.md`
- `projects/ai_washing/docs/track_a_filing_date_and_patent_window_audit_v1.md`
- `projects/ai_washing/docs/track_a_patent_refresh_source_review_v1.md`
- `projects/ai_washing/docs/track_a_market_data_source_review_v1.md`

## Execution posture

Track A should be run as project work, not as another restructure queue.

Shared `director` remains relevant for:
- review discipline
- playbooks
- documentation norms

But the live execution surface for this phase is:
- `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
- this Track A plan

## Bottom line

Track A is the bridge from:
- accepted restructure and preliminary results

to:
- refreshed data, stronger model credibility, and a real economics-facing paper
  design.
