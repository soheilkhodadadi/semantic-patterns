# Sample Construction Audit V1

This memo compares the current preliminary panel to the sample construction used
in the comparison paper and records the implications for delivery-phase
regressions.

## 1. Comparison paper: what its sample actually is

Based on the current draft of [AI_Washing_Mar2026.pdf](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/literature/AI_Washing_Mar2026.pdf):

- Unit of observation: firm-quarter
- Core period: `2016Q1` to `2024Q2`
- Universe: U.S. public firms
- AI-communication screen:
  - the paper states that it focuses on firms that have discussed AI-related
    topics at least once in conference calls over the sample period
- Additional filters:
  - excludes information and technology industries
  - requires at least `100` active employees in the resume data
- Final sample:
  - `20,135` firm-quarter observations
  - `721` unique firms

Important interpretation:

- The paper does **not** appear to keep only quarters with positive AI talk.
- Instead, it keeps firms that ever discuss AI, then studies them in a broader
  firm-quarter panel over the sample window.

That interpretation is consistent with both:

- the wording in Section `2.6 Sample Summary Statistics`
- the scale of the observation counts in the core tables

The paper’s patent validation section also uses firm-quarter innovation outcomes
and explicitly notes that:

- AI patents are aggregated at the firm-quarter level using filing dates
- innovation analyses are truncated to mid-2021 to avoid publication-lag bias

## 2. Our current panel: what it actually is

### Canonical files

- Merged clean panel:
  - `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- Regression-ready panel:
  - `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`

### Current construction logic

The current base is built from AI narrative measures and then left-joined to
patents and controls:

- [build_preliminary_narrative_measures.py](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py)
  aggregates classified AI sentences to `source_cik x source_year`
- [merge_ai_with_patents.py](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/aggregation/merge_ai_with_patents.py)
  left-joins patents onto that AI base
- [build_panel.py](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/aggregation/build_panel.py)
  then left-joins controls onto the AI+patent base
- [prepare_panel_for_regression.py](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/src/semantic_ai_washing/analysis/prepare_panel_for_regression.py)
  drops rows with missing variables needed for the estimation sample

### What that implies

Our current merged panel is **not** a full firm-year universe and is **not** an
ever-speaker panel over all years.

It is an `AI-speaking firm-year` panel.

Direct check:

- merged panel rows: `10,004`
- merged panel firms: `3,987`
- merged panel years: `2016` to `2024`
- rows with `ai_total <= 0`: `0`

So every row in the current merged panel already has positive AI content.

### Current row counts

- merged clean panel:
  - `10,004` firm-years
  - `3,987` firms
- regression-ready sample:
  - `6,152` firm-years
  - `2,201` firms

For context, if we took the current `3,987` ever-speaking firms and expanded
them over all 9 annual periods from `2016` to `2024`, the maximum balanced
annual scaffold would be:

- `35,883` firm-years

That means the current merged panel is materially narrower than an
ever-speaker-over-all-years design.

## 3. Methodological implication

The current sample is acceptable for a narrow question such as:

- among firm-years that already contain AI disclosure, does the composition of
  that disclosure predict future AI patenting?

But it is **not** ideal for broader alignment or mismatch questions such as:

- did the firm have AI patents before it started talking about AI?
- do firms “walk first, then talk”?
- do patents occur in the same year, previous year, or later years?
- what happens around the onset of AI talk?

Why not:

- if a firm first talks about AI in `2019`, the current merged panel does not
  retain that firm’s zero-AI-disclosure rows from `2016`, `2017`, or `2018`
- so earlier patent activity for that same firm is not naturally part of the
  current panel object

There is also a second issue:

- the current lead outcomes are created by shifting to the next observed row
  within firm rather than by first enforcing a complete annual firm-year
  scaffold

This matters because the current panel has firm-year gaps. As a result:

- some current `t+1` outcomes are actually “next observed AI-disclosure year”
- some current `t+2` outcomes are not literal `t+2` calendar-year outcomes

That makes the current forward-patent regressions usable only as a preliminary
conditional signal, not yet as a clean calendar-time validation design.

This is exactly the concern raised in delivery review, and it is methodologically
important.

## 4. My recommendation

I recommend splitting the empirical workflow into two panel designs.

### Panel A: current mention-conditioned panel

Use the current panel for:

- summary statistics that explicitly describe the AI-speaking estimation sample
- disclosure-composition validation tables
- preliminary main-text Table 2 style regressions

This panel is still useful because it isolates the composition of disclosure once
the firm is already talking about AI.

### Panel B: ever-speaker annual panel

Build a second panel for the next delivery phase:

- firms: any firm that ever has AI disclosure during `2016–2024`
- years: all years `2016–2024` for those firms
- disclosure counts: fill missing years with zeros
- patents: keep all years
- controls: keep all years where available

This second panel would let us test:

- prior-year patenting (`t-1`, `t-2`, etc.)
- contemporaneous patenting (`t`)
- forward patenting (`t+1`, `t+2`, etc.)
- talk onset versus patent timing
- better mismatch-style constructs

It would also let us construct patent timing correctly in calendar time:

- `patents_ai_lag2`
- `patents_ai_lag1`
- `patents_ai_t`
- `patents_ai_lead1`
- `patents_ai_lead2`

## 5. Recommended next design change

Before generating a large stack of delivery tables, the next methodological step
should be:

1. keep current Table 2 as a valid `conditional-on-AI-disclosure` validation table
2. build an `ever-speaker annual panel`
3. rebuild patent leads and lags on a complete annual scaffold
4. compare whether the signal is strongest in:
   - prior patents
   - same-year patents
   - future patents

## 6. Direct answer to the comparison-paper concern

There is a genuine sample-construction difference between the comparison paper
and our current panel.

That difference does **not** automatically mean our current work is wrong, but it
does mean:

- our current panel is narrower than the paper’s design logic
- our current lead construction is weaker than a proper calendar-year panel
- your concern is valid
- we should not build too many final-looking tables until we decide whether to
  keep the current conditional panel as the headline design or upgrade to the
  ever-speaker panel for dynamic patent tests
