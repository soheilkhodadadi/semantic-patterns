# Preliminary Delivery Blueprint

Date:
- `2026-03-20`

Status:
- editable delivery-phase blueprint for the preliminary package

## Purpose

This document is the working guide for the preliminary delivery phase.

It is meant to answer:

- what story we are telling
- which tables support that story
- which figures support that story
- what belongs in the main text
- what belongs in the appendix
- what order we should build things in

## Current Truth

### What is already strong enough

- cleaned classified sentence universe
- preliminary selected model
- narrative measures
- promoted patent series
- controls backbone
- full preliminary panel
- regression-ready panel
- rebuilt ever-speaker annual panel
- first regression portfolio

### What is not yet the bottleneck

- more raw computation
- more untargeted portfolio reruns

### What is now the real bottleneck

- delivery design
- table discipline
- figure discipline
- narrative coherence
- main-text vs appendix boundaries

## Recommended Preliminary Story

The strongest honest preliminary story is:

1. annual 10-K AI disclosure can be decomposed into actionable and speculative narrative components
2. the main-text empirical package should be built on the ever-speaker annual panel rather than the narrower speaking-only panel
3. the key validation question is whether disclosure composition aligns with AI patent outcomes before, during, or after the disclosure year
4. the current speaking-only validation result remains useful, but it belongs in the appendix as a conditional check
5. this is a preliminary validation of disclosure composition, not yet a final publication-grade causal claim about AI washing

## What We Should Not Force

- do not force a stronger “washing” claim than the current evidence supports
- do not imitate the comparison paper’s market-reaction and mechanism sections unless our own data support analogous claims
- do not let exploratory robustness tables crowd out the clean main-text story

## Main-Text Table Ladder

### Table 1. Summary Statistics and Coverage

Purpose:
- establish sample credibility
- define variable scale
- show that patent outcomes are sparse and disclosure variables are skewed
- anchor the reader on the ever-speaker panel as the main-text sample

### Table 2. AI Patent Timing and Alignment

Purpose:
- first indispensable empirical table on the broader panel
- validate disclosure composition against AI patent outcomes across calendar-time horizons

### Table 3. Disclosure Composition Timing

Purpose:
- show whether actionable and speculative-only disclosure differ once timing is measured on the ever-speaker panel

### Table 4. Patent-Timing Matrix by Disclosure Type

Purpose:
- mirror the literature-style distributed-lag layout more closely
- show prior, contemporaneous, and future AI patent timing in one table family

### Table 5. Credibility Metrics

Purpose:
- move from raw class counts into the paper’s credibility constructs
- candidate measures:
  - `SpecShare`
  - `AI_Focus`
  - `CredAI`
  - `A_S`
  - `SpecMinusAct`

## Main-Text Figure Ladder

### Figure 1. Time Series of AI Disclosure Volume and Composition

Likely inputs:
- `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`

Story:
- establishes the phenomenon
- shows growth in AI disclosure and whether composition shifts toward actionable or speculative language

### Figure 2. AI Patent Coverage Over Time

Likely inputs:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`

Story:
- frames the external validation target
- shows how sparse AI patenting is

### Figure 3. Industry Heterogeneity in Disclosure Composition

Likely inputs:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`

Story:
- gives a cross-sectional picture without needing another regression table

### Figure 4. Patent Alignment by Disclosure-Composition Buckets

Likely inputs:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`

Story:
- intuitive visual partner to the patent-validation table

## Appendix Priorities

### Technical Appendix

- classifier benchmark
- held-out construction
- IRR / adjudication summary
- cleanup diagnostics
- keyword methodology

### Empirical Appendix

- current conditional validation table from the AI-speaking panel
- extensive-margin `any AI patent` timing variants
- Poisson / count-model robustness
- extra FE ladders
- extra industry splits
- alternative metric definitions
- mismatch variants once implemented

## Delivery Workflow

### Stage 1. Design

Output:
- lock table / figure ladder
- lock main-text vs appendix boundary

### Stage 2. Table Production

Output:
- one spec card per table
- one standalone artifact per table

### Stage 3. Figure Production

Output:
- one standalone artifact per figure
- one short interpretation note per figure

### Stage 4. Validation

For every table / figure:

1. verify input path
2. verify sample restriction
3. verify variable definitions
4. verify displayed notes
5. verify interpretation and caveat note

### Stage 5. Packaging

Only after the modular artifacts are reviewed:

- insert into manuscript
- build delivery packet
- refresh Word draft

## Immediate Build Order

1. `Table 1`
2. `Table 2` AI patent timing and alignment on the ever-speaker panel
3. current conditional validation table moved to appendix
4. `Table 3` disclosure composition timing
5. `Table 4 / 4B` patent-timing matrix by disclosure type
6. `Table 5 / 5B` credibility metrics
7. `Figure 1`
8. `Figure 2`
9. compact main-text vs appendix review

## Current Practical Rule

If a result is interesting but does not clearly sharpen the main story:

- keep it modular
- do not push it into the manuscript yet
- decide later whether it belongs in the appendix or not
