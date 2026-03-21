# Preliminary Results Execution Plan

Updated: `2026-03-20`

## Goal

Deliver a disciplined preliminary package that looks like the early stage of a
real paper rather than a loose benchmark dump.

The immediate objective is to move from exploratory portfolio work into a
story-driven delivery sequence with:

- a clear sample definition
- a clean table ladder
- a clean figure ladder
- modular reviewable artifacts
- stakeholder updates at stage gates

## Current Position

### Infrastructure now in place

- cleaned classified sentence universe for `2016-2024`
- promoted patent series for `2016-2024`
- Compustat controls through `2016-2024`
- modular table and DOCX generation
- conditional AI-speaking panel
- rebuilt ever-speaker annual panel

### What changed methodologically

We confirmed that the earlier merged panel kept only `AI-speaking firm-years`.
That panel remains useful for conditional validation, but it is too narrow for
calendar-time questions about prior, contemporaneous, and future patenting.

We therefore rebuilt the panel as an `ever-speaker annual panel`:

- firms that ever mention AI during `2016-2024`
- all years `2016-2024` retained for those firms
- zero-disclosure years preserved
- patent lags and leads constructed on an annual scaffold

### Current authoritative panel files

Conditional panel:
- `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`

Ever-speaker panel:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

Supporting audit notes:
- `reports/analysis/sample_construction_audit_v1.md`
- `reports/analysis/sample_comparison_ever_speaker_v1.md`
- `reports/analysis/preliminary_delivery_story_roadmap_v1.md`

## Delivery-Phase Working Decision

Treat the project as being in a delivery-design stage, not a raw-computation
stage.

That means:

- no broad portfolio sweeps unless they answer a specific table question
- one standalone artifact per table or figure
- main text and appendix handled separately
- sample and timing logic checked before visual packaging

## Workstreams

### Workstream A: Conditional Validation

Purpose:
- preserve the useful result already obtained on the AI-speaking panel

Current output:
- appendix conditional patent-validation object

Interpretation rule:
- this remains valid as a conditional-on-speaking result
- it should not be treated as the main-text empirical anchor

### Workstream B: Ever-Speaker Timing Analysis

Purpose:
- use the rebuilt annual panel to test where patent alignment lives in time

Next tests:
- `log(1 + AI patents)` at:
  - `t-2`
  - `t-1`
  - `t`
  - `t+1`
  - `t+2`
- keep extensive-margin `any AI patent` models as a companion robustness family

Initial design rule:
- separate actionable-only and speculative-only models
- firm/year FE as the anchor specification
- additional FE structures as robustness

### Workstream C: Delivery Tables And Figures

Main-text build order:
1. `Table 1` summary statistics and sample coverage
2. `Table 2` AI patent timing and alignment on the ever-speaker panel
3. `Table 3` FE ladder and sample trims
5. `Figure 1` disclosure composition over time
6. `Figure 2` AI patent coverage over time

Appendix queue:
- current conditional validation table from the AI-speaking panel
- credibility metrics table
- count and Poisson robustness
- extra FE ladders
- industry splits
- mismatch variants

### Workstream D: Stakeholder Communication

Purpose:
- keep supervisory review aligned with what has actually been built

Cadence:
1. infrastructure/sample-definition update
2. timing-analysis update
3. assembled preliminary-package update

Format:
- short prose memo
- Word-ready artifact
- consistent tone and current empirical read

## Expected Empirical Read

These are expectations to test, not claims to force.

- actionable disclosure may line up more with prior or contemporaneous AI patenting than with later AI patenting
- speculative disclosure may remain a modest positive signal for later AI patent outcomes, but this should be checked on the broader panel
- no-FE results may be larger and less trustworthy than firm/year FE results
- share-style credibility measures may remain more stable than raw count measures

## Validation Rule

No table moves into the main text until we have recorded:

1. input file path
2. sample restriction
3. dependent variable(s)
4. focal regressor(s)
5. controls
6. FE
7. clustering
8. interpretation note
9. caveat note

## Highest-Leverage Order

1. update `Table 1` so the main-text version is anchored on the ever-speaker panel
2. build the new main-text `Table 2` on AI patent timing outcomes in the ever-speaker panel
3. move the current conditional validation table to the appendix
4. run FE ladder / sample trims on the winning timing specification
4. build the first two figures
5. update the delivery packet only after those modular objects are reviewed

## User Help That Would Speed Things Up

- review each standalone table or figure as it is produced rather than waiting for a full manuscript refresh
- use the supervisor-update memo as a lightweight review checkpoint when helpful
- flag any must-have main-text exhibit early so we can prioritize it in the build order
