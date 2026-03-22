# Literature Story Arc Memo

Source reviewed:
- `paper/literature/AI_Washing_Mar2026.pdf`

Date:
- `2026-03-20`

## Purpose

This memo translates the local comparison paper into a delivery-design guide for
our preliminary package. The goal is not to copy the paper. The goal is to
understand the logic of its storytelling, table progression, and appendix design
so we can apply the same discipline to our own, different project.

## What The Comparison Paper Is Doing

Its main empirical progression is highly structured:

1. frame the problem
2. introduce a new paired measurement system
3. validate the measures against an external outcome
4. define the mismatch / gap
5. characterize who exhibits the mismatch
6. show why the mismatch matters economically
7. test a mechanism for why the mismatch occurs

That progression is the core reason the paper feels persuasive.

It does not dump many regressions at once. Each section answers one question.

## Main Story Ladder In The Comparison Paper

### Stage 1: Why should anyone care?

- AI claims are proliferating
- those claims may be exaggerated or unverifiable
- misrepresentation matters because it can distort investor beliefs and capital allocation

### Stage 2: What is the paper’s main contribution?

- construct `AI talk`
- construct `AI walk`
- argue that the contribution is the distinction itself

### Stage 3: Can the reader trust those constructs?

- validate the measures using subsequent innovation outcomes
- `walk` predicts innovation
- `talk` does not

This is the first indispensable empirical section.

### Stage 4: What is the mismatch?

- test whether firms that talk more later walk more
- cross-sectionally maybe yes
- within-firm, after fixed effects, largely no

This section creates the operational object of interest.

### Stage 5: Where does the mismatch live?

- who does it
- when it grows
- which industries show more of it

### Stage 6: Why does it matter?

- market reactions
- institutional response

### Stage 7: Why does it happen?

- managerial incentives
- event-style mechanism tests

## Table And Figure Progression

### Main Text Tables

- `Table 1`: summary statistics
- `Table 2`: validation against innovation outcomes
- `Table 3`: who talks / who walks
- `Table 4`: main dynamic mismatch table
- `Table 5`: time-split mismatch table
- `Table 6`: determinants of washing
- `Table 7`: market consequences
- `Table 8`: institutional-investor consequences
- `Table 9`: incentive mechanism
- `Table 10`: event-driven opportunism

### Main Text Figures

- incidence / trend figure
- measure-intuition figure
- divergence time series
- industry-level divergence
- topic evolution
- mismatch visualization
- mechanism/event figures

## Why It Works

The paper is not “strong” because it has many tables.
It is strong because the table order creates a natural persuasion sequence:

1. trust the data and measures
2. accept the mismatch
3. learn where it happens
4. see why it matters
5. see why it happens

## Appendix Function

The appendix protects the main text.

It carries:

- measurement details
- keyword construction
- functional-form robustness
- alternative definitions
- single-lag checks
- extra count-model robustness

The appendix is not competing with the main text. It is defending it.

## What Transfers Directly To Our Paper

The transferable scaffold for our filing-based preliminary package is:

1. measurement
2. validation
3. mismatch / decomposition
4. cross-sectional description
5. lighter consequence / interpretation layer
6. appendix for technical defense

## What Must Be Different In Our Paper

We should not imitate the comparison paper too literally.

Their core contrast:
- `talk` vs `walk`

Our core contrast:
- `Actionable` vs `Speculative` narrative composition in annual filings
- validated against future AI patents

Their strongest clean claim:
- `walk` predicts innovation, `talk` does not

Our current preliminary evidence:
- more mixed
- speculative-only and speculative-share results are presently more visible than a clean actionable-dominance story

Therefore:

- do not force a stronger causal “washing” claim than the evidence supports
- do not force market-reaction or managerial-incentive sections just because the comparison paper has them
- do not present our current preliminary results as if we already have a full talk/walk design

## Best Preliminary Story For Our Paper

The most defensible preliminary story is:

1. annual 10-K AI disclosure can be decomposed into more credible/action-oriented versus more speculative narrative components
2. that decomposition is not cosmetic; it changes the empirical relationship between disclosure and later AI patent outcomes
3. the strongest preliminary evidence appears on the extensive margin of future AI patenting and on speculative-share style measures
4. this is a preliminary validation of disclosure composition, not yet a final publication-grade claim about causal AI washing

## Delivery Implication

A disciplined preliminary package should therefore look like:

- `Table 1`: summary statistics / variable definitions / coverage
- `Table 2`: AI-focus timing table on the ever-speaker panel
- `Table 3`: separate actionable-only and speculative-only headline regressions
- `Table 4`: disclosure-type timing matrix
- `Table 6`: methodology-aligned `A_S x PatentMismatch` table
- `Figure 1`: time series of overall AI mentions and actionable/speculative components
- `Figure 2`: AI patent coverage over time
- `Figure 3`: mismatch / patent-alignment style visualization
- appendix:
  - conditional validation table
  - exploratory credibility metrics (`Table 5 / 5B`)
  - classifier benchmark
  - IRR / adjudication note
  - keyword methodology
  - functional-form robustness
  - extra FE and sample-trim tables

## Practical Takeaway

For our delivery phase, the main problem is no longer “we need more regressions.”
The main problem is:

- choose the story we can honestly tell
- define the exact table ladder that supports that story
- produce each table as a separate validated artifact
- move only supporting material into the appendix
