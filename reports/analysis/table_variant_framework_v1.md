# Table Variant Framework V1

Date:
- `2026-03-21`

## Purpose

This note records a working rule for delivery-phase empirical tables:

- each important empirical test can have multiple standalone variants
- those variants should be generated as separate modular tables
- only later do we decide which version belongs in the main text and which belongs in the appendix

This avoids two bad outcomes:

- overloading one table with too many specifications
- pretending one functional form is obviously correct before we have reviewed the alternatives

## Practical Rule

For empirical tables, use:

- `A` version:
  - current preferred main-text specification
- `B` version:
  - first obvious alternative specification
- additional variants only when they answer a real reviewer-style question

## Current Variant Mapping

### Table 2

Core question:
- how does broad AI disclosure intensity align with AI patent timing?

Variants:
- `Table 2`
  - ever-speaker panel
  - dependent variable:
    - `log(1 + AI patents)`
- `Table 2B`
  - same sample
  - same controls and FE
  - dependent variable:
    - raw `AI patents` count

### Table 3

Core question:
- how does disclosure composition alter that timing pattern?

Variants:
- `Table 3`
  - ever-speaker panel
  - dependent variable:
    - `log(1 + AI patents)`
  - Panel A:
    - actionable disclosure
  - Panel B:
    - speculative-only disclosure
- `Table 3B`
  - same sample
  - same controls and FE
  - dependent variable:
    - raw `AI patents` count
  - same two panels

### Table 4

Core question:
- how do prior, contemporaneous, and future AI patent outcomes line up with disclosure type once we vary FE structure and sample trims?

Variants:
- `Table 4`
  - dependent variable:
    - actionable disclosure
  - rows:
    - `log(1 + AI patents)` at `t-2`, `t-1`, `t`, `t+1`, `t+2`
  - columns:
    - firm + year FE
    - industry + year FE
    - non-financial trim
    - non-financial/non-utility trim
- `Table 4B`
  - same timing-matrix design
  - dependent variable:
    - speculative-only disclosure

Possible appendix companions:
- raw-count timing versions of `Table 4 / Table 4B`
- extra timing horizons if a reviewer-style question makes them necessary

## Next Table Topic

The next table topic after the `Table 4 / Table 4B` family is:

- `Table 5`
  - credibility-metric family
  - likely centered on:
    - `SpecShare`
    - `CredAI`
    - `A_S`
    - `SpecMinusAct`

That table should not be built until we have reviewed which timing object we want to emphasize in the current main-text sequence.

## Selection Rule

When choosing which variant becomes the main-text version, prefer the one that is:

1. easiest to interpret
2. most stable across nearby specifications
3. most aligned with the paper’s core question
4. least likely to draw an immediate reviewer objection about arbitrary functional-form choice

The non-selected variant should usually remain as an appendix companion rather than being discarded.
