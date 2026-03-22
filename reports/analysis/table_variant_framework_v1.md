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

## Next Table Topic

The next table topic after the `Table 2 / Table 3` family is:

- `Table 4`
  - FE ladder / sample-trim robustness for the timing result we decide to anchor in the main text

That table should not be built until we have visually reviewed the `A` and `B` variants for the current timing family.

## Selection Rule

When choosing which variant becomes the main-text version, prefer the one that is:

1. easiest to interpret
2. most stable across nearby specifications
3. most aligned with the paper’s core question
4. least likely to draw an immediate reviewer objection about arbitrary functional-form choice

The non-selected variant should usually remain as an appendix companion rather than being discarded.
