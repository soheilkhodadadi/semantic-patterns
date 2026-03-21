# Preliminary Results Table Plan

Date:
- `2026-03-20`

Status:
- draft planning artifact for the preliminary delivery phase

## Why This Exists

We now have enough empirical output that the limiting factor is no longer
whether we can generate results. The limiting factor is whether we can turn
those results into a disciplined, persuasive, non-messy delivery package.

This plan is meant to restore a stage-based workflow:

- table design first
- then targeted estimation
- then validation
- then narrative assembly

Not:

- rerun everything
- inspect a giant output dump
- decide later what it means

## Current Truth

### Preliminary empirical core

Substantially complete:

- cleaned classified sentence universe
- preliminary selected classifier
- firm-year narrative measures
- promoted patent series
- Compustat controls
- merged full panel
- regression-ready panel
- first broad regression portfolio

### Preliminary delivery

Started but not formalized enough:

- some tables exist
- some manuscript snippets exist
- a compiled markdown draft exists
- but the table ladder, release manifest, and main-text vs appendix boundary are still too implicit

## Recommended Delivery Model

Use a three-layer production process.

### Layer 1: Story design

Output:
- one short statement of the main preliminary claim
- one ordered list of the tables/figures needed to support that claim

### Layer 2: Table-by-table production

Output:
- one file per table
- one table-specific note documenting:
  - data source
  - sample
  - dependent variable
  - main regressor(s)
  - controls
  - FE
  - clustering
  - interpretation
  - caveats

### Layer 3: Packaging

Output:
- a clean main-text package
- a clearly bounded appendix package
- release manifest describing what was actually used

## Proposed Story Arc For The Preliminary Delivery

Recommended main story:

1. we build a sentence-level measure of annual AI disclosure composition
2. we validate whether disclosure composition aligns with subsequent AI patent outcomes
3. the strongest preliminary evidence appears in the extensive margin of future AI patenting and in speculative-share style measures
4. the results suggest that disclosure composition matters, but the exact asymmetry between actionable and speculative language remains a live empirical question

This story is narrower than the comparison paper, but it is honest and publishable as a preliminary result package.

## Proposed Main-Text Tables

### Table 1. Summary Statistics And Coverage

Purpose:
- establish sample credibility
- show the scale of the panel
- define the core variables

Should include:
- `n_A`
- `n_S`
- `n_I`
- `AI_Focus`
- `ActShare`
- `SpecShare`
- `CredAI`
- `A_S`
- `patents_ai`
- `patents_total`
- core controls

### Table 2. Core Patent Validation

Purpose:
- first indispensable empirical table
- show whether filing-based disclosure composition aligns with future AI patenting

Recommended first pass:
- separate actionable-only and speculative-only future-patent LPMs
- share-based robustness next to them only if it sharpens the same message

### Table 3. Headline Separate Regressions

Purpose:
- keep the main text focused on one narrative variable at a time

Recommended structure:
- actionable-only
- speculative-only
- firm/year FE
- industry/year FE
- no-FE comparison only if explicitly labeled as sensitivity, not as headline evidence

### Table 4. FE Ladder / Sample Trims

Purpose:
- show how stable the main effect is across reasonable specifications

Recommended variants:
- full sample
- non-financial
- non-financial/non-utility
- high-tech split if useful

### Table 5. Credibility Metrics

Purpose:
- move from class counts to disclosure-composition constructs

Recommended metrics:
- `SpecShare`
- `AI_Focus`
- `CredAI`
- `A_S`
- `SpecMinusAct`

## Proposed Main-Text Figures

### Figure 1. Time Series Of AI Disclosure Composition

Show:
- AI mention volume
- actionable share
- speculative share

### Figure 2. Industry Heterogeneity

Show:
- top industries by AI disclosure growth
- or industry variation in `SpecShare`

### Figure 3. Patent Alignment / Mismatch Visualization

Show:
- distribution of disclosure credibility against later patent outcomes
- or a first preliminary mismatch plot once the mismatch construct is implemented

## Proposed Appendix

### Technical Appendix

- held-out benchmark summary
- model benchmark matrix
- IRR / adjudication summary
- keyword methodology
- sentence cleanup / coverage

### Empirical Appendix

- functional-form robustness
- Poisson / count models
- extra FE variants
- single-variable alternative metrics
- SIC / high-tech subsamples

## Table Production Checklist

For each table, do not mark it ready until all of the following are written down:

1. exact input file path
2. exact sample restriction
3. exact dependent variable
4. exact focal regressor(s)
5. exact controls
6. exact FE
7. exact clustering rule
8. exact output file path
9. one-paragraph interpretation
10. one-paragraph caveat note

## What Not To Do

- do not rebuild the full paper after every small regression tweak
- do not mix main-text and appendix tables in the same production step
- do not present exploratory models as if they are headline evidence
- do not let a large portfolio substitute for a deliberate table ladder

## Immediate Next Stage

The next disciplined step should be:

1. freeze the preliminary story arc
2. define the exact first five tables and first three figures
3. produce them one at a time
4. validate each before moving to the next
5. only then assemble the delivery draft

## Immediate Candidate Work Queue

1. finalize `Table 1` summary-stats spec
2. finalize `Table 2` core patent-validation spec
3. finalize `Table 3` separate actionable/speculative headline table
4. implement `Table 4` FE-ladder / trims table
5. implement `Table 5` credibility-metrics table
6. implement first mismatch construct for figure or appendix table

