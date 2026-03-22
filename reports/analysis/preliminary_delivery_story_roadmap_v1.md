# Preliminary Delivery Story Roadmap V1

Date:
- `2026-03-20`

Status:
- working delivery-phase roadmap for the preliminary package
- intended to guide table-by-table and figure-by-figure production

## Purpose

This note is the bridge back from exploratory benchmarking into disciplined
preliminary delivery.

It answers four questions:

1. what story we can honestly tell now
2. which empirical objects belong in that story
3. which tables and figures should be built next
4. what we expect each object to clarify before it is considered ready

## Core Delivery Position

We now have enough infrastructure to stop treating the project as an open-ended
portfolio search.

The project has:

- a cleaned sentence and classification layer for `2016-2024`
- a promoted AI-patent series with improved assignee matching
- Compustat controls through `2016-2024`
- a conditional AI-speaking panel
- a rebuilt `ever-speaker annual panel` that supports calendar-time timing tests
- modular table generation and Word-ready review outputs

That means the next task is no longer “run more regressions.”
The next task is to build a persuasive, disciplined delivery package.

## Main Story We Are Trying To Tell

The strongest honest preliminary story is:

1. annual 10-K AI disclosure can be decomposed into actionable and speculative narrative components
2. this decomposition is economically meaningful rather than cosmetic
3. the main-text empirical package should be built on the `ever-speaker annual panel`, not only on AI-speaking firm-years
4. the next core test is whether actionable and speculative disclosure align with AI patent outcomes in prior, contemporaneous, or future years
5. the earlier conditional validation table remains useful, but it belongs in the appendix rather than as the main-text empirical anchor

## Sample Design We Are Freezing

### Panel A: Conditional AI-speaking panel

Files:
- `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`

Use:
- appendix validation tables
- conditional description of what happens once firms are already talking about AI

Interpretation rule:
- this panel is useful, but it is not a clean timing panel

### Panel B: Ever-speaker annual panel

Files:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

Use:
- timing analysis
- onset / alignment / mismatch work
- lag, contemporaneous, and lead patent outcomes

Interpretation rule:
- this is the main empirical object for the main-text delivery tables

## Main-Text Table Sequence

### Table 1. Summary Statistics And Sample Coverage

Goal:
- establish what the ever-speaker sample is
- show sparsity and skewness clearly
- make the broader annual panel, not the conditional speaking-only panel, the main-text sample definition

Preferred form:
- one clean main table on the ever-speaker estimation sample
- optional appendix companion on the narrower conditional speaking-only sample

What we expect to learn:
- whether the estimation sample still looks credible once zero-disclosure years are restored
- whether medians / percentiles communicate sparsity better than means alone

### Table 2. AI Patent Timing And Alignment

Goal:
- become the first indispensable main-text regression table on the broader panel
- show how disclosure composition aligns with AI patent outcomes across calendar-time horizons

Panel:
- ever-speaker annual panel

Primary outcome family:
- `log(1 + AI patents)` at:
  - `t-2`
  - `t-1`
  - `t`
  - `t+1`
  - `t+2`

Core regressor design:
- actionable-only models
- speculative-only models
- run separately in the headline version
- keep constants omitted from display

Expected read:
- actionable disclosure may line up more with prior or same-year AI patenting than with future AI patenting
- speculative disclosure may show a different timing profile, including weaker alignment with realized innovation
- the purpose is to learn where the relation appears in time, not to force a preferred sign pattern

Narrative role:
- this table becomes the main empirical timing table for the preliminary package

### Table 3. Disclosure Composition Timing

Goal:
- show whether actionable and speculative-only disclosure differ once timing is measured on the ever-speaker panel
- keep the composition story separate from the broad `AI_Focus` timing story

Preferred variants:
- main version:
  - `log(1 + AI patents)` timing outcomes
- appendix companion:
  - raw AI patent counts

Expected read:
- actionable and speculative-only disclosure need not share the same timing profile
- this table should tell us whether composition adds information beyond broad AI-focus intensity

### Table 4. Patent-Timing Matrix By Disclosure Type

Goal:
- mirror the literature-style distributed-lag layout more closely
- show how AI patent timing lines up with disclosure type when the full `t-2` to `t+2` window enters the same model
- let the reader compare FE/sample variants in columns instead of scattering them across separate tables

Preferred form:
- `Table 4`
  - dependent variable:
    - actionable disclosure
- `Table 4B`
  - dependent variable:
    - speculative-only disclosure
- shared rows:
  - `log(1 + AI patents)` at `t-2`, `t-1`, `t`, `t+1`, `t+2`
- shared columns:
  - firm + year FE
  - industry + year FE
  - non-financial trim
  - non-financial / non-utility trim

Expected read:
- actionable disclosure may line up more with nearby or future AI patenting
- speculative-only disclosure may look more backward-looking or contemporaneous
- the industry-FE column may be the least stable and should be read as a comparison, not automatically as the anchor

### Table 5. Credibility Metrics Table

Goal:
- move from raw class counts into paper-level narrative credibility constructs

Candidate metrics:
- `SpecShare`
- `AI_Focus`
- `CredAI`
- `A_S`
- `SpecMinusAct`

Expected read:
- `AI_Focus` may remain the most stable broad measure
- share-style measures such as `SpecShare` and `SpecMinusAct` may only sharpen under some FE choices
- some credibility metrics may remain exploratory and belong in appendix if they do not sharpen the story

Methodology caveat:
- the methodology treats `A_S` and `A_S x PatentMismatch` as the core AI-washing specification
- therefore the current credibility-metric table is informative, but it does not replace the later mismatch-based AI-washing table

Current placement:
- appendix-only exploratory table family

### Table 6. Methodology-Aligned AI-Washing Table

Goal:
- implement the methodology's core AI-washing specification directly
- test whether the positive link between credible AI disclosure and future AI patenting attenuates in mismatch years

Core regressors:
- `A_S`
- `A_S x PatentMismatch`

PatentMismatch construction:
- low credibility in year `t`:
  - low `A_S` or high `SpecShare` among AI-talking firm-years
- weak contemporaneous AI patenting relative to the industry-year

Preferred variants:
- main version:
  - `log(1 + AI patents)` at `t+1`
- nearby companion:
  - `log(1 + AI patents)` at `t+2`

Expected read:
- `A_S` should enter positively
- `A_S x PatentMismatch` should enter negatively
- the interaction should be clearer at `t+1` than at `t+2`

Narrative role:
- this is the first table that maps directly onto the methodology's explicit AI-washing specification
- it should likely outrank the exploratory credibility-metric table in the main-text hierarchy

Current placement:
- promoted into the main-text ladder

## Main-Text Figure Sequence

### Figure 1. AI Disclosure Volume And Composition Over Time

Purpose:
- show the phenomenon visually
- distinguish overall disclosure growth from composition changes

Expected read:
- AI disclosure rises over time
- composition may shift in ways relevant to later patent alignment

### Figure 2. AI Patent Coverage Over Time

Purpose:
- show how sparse AI patenting remains even in the ever-speaker universe
- visually motivate why binary incidence may be more stable than counts

Expected read:
- AI patenting is sparse but meaningful
- means alone understate how zero-heavy the distribution is

### Figure 3. Patent Alignment And Mismatch Visualization

Purpose:
- complement Table 6 with a more intuitive picture
- show how future AI patenting differs between mismatch and non-mismatch firm-years across the `A_S` distribution

Expected read:
- non-mismatch firm-years should show a steeper positive relation between `A_S` and future AI patenting
- mismatch firm-years should show attenuation of that relation

### Figure 4. Industry Heterogeneity

Purpose:
- show where AI disclosure composition is most concentrated
- provide cross-sectional context without overcrowding the main tables

## Appendix Sequence

### Technical appendix

- classifier benchmark
- IRR / adjudication summary
- keyword and assignee-matching methodology
- sample-construction comparison note
- table-layout and generation notes if useful

### Empirical appendix

- conditional validation table from the speaking-only panel
- extensive-margin `any AI patent` timing companion
- Poisson and count robustness
- alternative functional forms
- extra FE ladders
- additional industry splits
- exploratory credibility-metric tables if they do not sharpen the core story
- extra patent-mismatch variants once the baseline interaction table is fixed

## What We Expect To Learn Next

The next empirical gate is not generic significance.
It is whether the rebuilt ever-speaker panel changes the interpretation of the
narrative measures.

Specifically:

1. does actionable disclosure line up more with prior or same-year patenting than with future patenting?
2. does speculative disclosure remain positively related to later patent incidence once zero-disclosure years are restored?
3. are the current conditional results mostly a within-speaking-years result, or do they survive in the broader annual panel?
4. whether the methodology-aligned mismatch interaction behaves in the expected negative direction at `t+1` and `t+2`
5. whether Table 6 is strong enough to become the paper's main AI-washing table
6. which remaining exploratory tables deserve appendix space

## Build Order

1. rebuild `Table 1` so the main-text version is anchored on the ever-speaker panel
2. build the new main-text `Table 2` on AI patent timing outcomes in the ever-speaker panel
3. move the current conditional validation table to the appendix
4. build `Table 4 / Table 4B` as the literature-style patent-timing matrix family
5. build `Figure 1` and `Figure 2`
6. promote `Table 6 / Table 6B` into the main-text ladder
7. keep `Table 5 / Table 5B` in the appendix lane
8. build `Figure 3` as the mismatch visualization companion
9. only then assemble the next delivery packet

## Stop Rules

Do not move a new table into the main text until all of the following are fixed:

1. exact input file path
2. exact sample restriction
3. exact dependent variable(s)
4. exact focal regressor(s)
5. exact control set
6. exact FE structure
7. clustering rule
8. one-paragraph interpretation
9. one-paragraph caveat note

## Stakeholder-Update Cadence

Use a short narrative update at three points:

1. after major infrastructure repair and sample-definition changes
2. after the first timing table is estimated and interpreted
3. after the preliminary package is assembled for review

Those updates should be prose-first, not bullet dumps, and should summarize:
- what changed
- what we learned
- what the next gate is
