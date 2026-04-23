# AI-Washing Publication Upgrade Roadmap V1

## Purpose

This roadmap defines the next active phase of the AI-washing project after the
preliminary-results and restructure period.

It assumes the repo restructure is accepted and the project can now use the new
lab structure instead of continuing to build it.

## Inputs

Primary planning inputs:
- `projects/ai_washing/docs/publication_upgrade_stakeholder_expectations_v1.md`
- `docs/director/stakeholder_expectations.md`
- `docs/director/proposal_methodology.md`
- `paper/source/AI Washing - SK - 2026.03.25.pdf`

## Phase goal

Upgrade the project from a credible preliminary disclosure-validation paper into
a stronger publication package with:
- refreshed data
- stronger model credibility and robustness
- capital-market consequence tests
- at least one serious identification path

## Current status as of 2026-04-10

Measurement and benchmark status:
- `2025` filing refresh and patent refresh lanes are largely operational
- patent fuzzy matching was tested and rejected as too noisy for the main panel
- the classifier lane now has a provisional deployable winner:
  - layered local base
  - API-A selective defer
- `IRR v3 rerun` passed with the original second rater
- the shadow full-corpus local pass is complete and the deferred API-A tranche
  is running on the `conf49` slice
- first pilot filing-date CAR regressions now exist on the matched filing sample
- broad-sample WRDS raw fundamentals and monthly market pulls now exist for the `2016-2025` refresh backbone

Implication:
- the next highest-leverage publication work is no longer basic classifier
  rescue
- it is now capital-market design, event-study execution, and panel rebuilding
  on top of the provisional hybrid classifier

## Workstreams

### Workstream A. Data refresh and sample extension

Goal:
- extend the filing window to include 2025

Main tasks:
- ingest 2025 10-K filings
- run extraction on the refreshed filing set
- run classification on the refreshed sentence set
- rebuild core downstream disclosure measures and panels

Success condition:
- the project has a reproducible `2016-2025` or `2021-2025` refreshed analysis
  backbone ready for empirical work

### Workstream B. Classifier credibility and robustness

Goal:
- make the empirical results less vulnerable to the current classifier accuracy
  concern

Main tasks:
- rerun the current evaluation and document the present model state
- test improvement paths if realistic
- build robustness variants:
  - human-labeled subset
  - high-confidence subset
  - threshold or confidence sensitivity

Success condition:
- the main paper claims do not depend on one fragile reading of full-sample
  model output

### Workstream C. Capital-market consequence design

Goal:
- quantify why AI-washing matters economically

Primary candidate tests:
- filing-date event study around 10-K filing dates
- delayed-price / post-filing drift test
- long-short credibility versus mismatch portfolio

Secondary tests:
- valuation response in annual panel form
- institutional or analyst reaction if the first two lanes work cleanly
- financing or market-access consequences if data access is practical

Primary design note:
- `projects/ai_washing/docs/track_a_event_study_and_economic_impact_design_v1.md`

Success condition:
- at least one credible economic-stakes result is implemented and interpretable
- and the paper can quantify a shareholder consequence of low-credibility AI
  disclosure

### Workstream D. Identification design

Goal:
- move beyond a purely predictive framing

Primary candidate:
- ChatGPT release as a salience or disclosure-cost shock

Preferred implementation order:
1. post-ChatGPT interaction in the filing-date event study
2. delayed-price / portfolio differences pre versus post ChatGPT
3. only then larger diff-in-diff or triple-difference designs if the first two
   are promising

Secondary candidates:
- other disclosure or regulatory shocks if cleaner

Success condition:
- one identification path is selected, documented, and run far enough to judge
  whether it should stay in the paper

### Workstream E. Paper package hardening

Goal:
- align the output package with stronger journal expectations

Main tasks:
- move the strongest surprising finding to the front
- explain or replace vulnerable specification/reporting choices
- prepare:
  - before/after examples
  - literature differentiation
  - robustness summary

Success condition:
- the empirical package tells a stronger and more defensible story than the
  March 2026 draft

## Recommended execution order

1. Workstream A: data refresh
2. Workstream B: classifier credibility and robustness
3. Workstream C: capital-market consequence design
4. Workstream D: identification design
5. Workstream E: paper package hardening

Reason:
- the first two workstreams stabilize the measurement layer
- the next two determine whether the paper clears the economics bar
- the final workstream packages the evidence coherently

## Near-term 30-day targets

### Target 0

Close the measurement gate enough to support provisional economics work.

Current status:
- largely achieved
- the remaining step is to finish and merge the running `conf49` deferred
  API-A slice

### Target 1

Stand up the publication-upgrade planning lane.

Deliverables:
- this roadmap
- stakeholder expectations note
- clear workstream ownership

### Target 2

Refresh the data backbone.

Deliverables:
- 2025 filing ingestion decision
- updated extraction/classification run plan
- explicit list of required data dependencies

### Target 3

Prototype the next empirical turn.

Deliverables:
- one capital-market test design note
- one identification design note
- one model-credibility robustness plan
- one event-ready filing panel specification for WRDS/CRSP/Compustat pulls
- one explicit delayed-price / portfolio design tied to AI-credibility mismatch

## Active execution anchor

The current execution surfaces for this roadmap are:
- `projects/ai_washing/docs/track_a_execution_plan_v1.md`
- `projects/ai_washing/docs/track_a_publication_execution_map_v1.md`
- `projects/ai_washing/docs/track_a_stage_checkpoint_v1.md`
- `projects/ai_washing/docs/track_a_event_study_and_economic_impact_design_v1.md`
- `projects/ai_washing/docs/track_a_event_ready_panel_spec_v1.md`
- `projects/ai_washing/docs/track_a_event_study_scaffold_progress_v1.md`
- `projects/ai_washing/docs/track_a_wrds_bridge_progress_v1.md`
- `projects/ai_washing/docs/track_a_event_return_panel_progress_v1.md`
- `projects/ai_washing/docs/track_a_first_car_regressions_v1.md`
- `projects/ai_washing/docs/track_a_full_sample_wrds_raw_progress_v1.md`

## What this roadmap is not

This roadmap is not:
- another restructure queue
- a promise to solve every paper issue at once
- a commitment to a new giant append-only machine-readable roadmap immediately

It is a scoped upgrade plan for the next serious research phase.

## Machine-readable roadmap posture

Recommended posture:
- keep `director/model/roadmap_model.yaml` as the archive of the preliminary and
  restructure era
- only create a new lightweight machine-readable AI-washing publication model if
  this roadmap becomes the primary execution lane

## Bottom line

The project now needs to shift from:
- "can we measure and preliminarily validate AI-washing?"

to:
- "can we show that AI-washing matters economically and withstands a stronger
  publication standard?"
