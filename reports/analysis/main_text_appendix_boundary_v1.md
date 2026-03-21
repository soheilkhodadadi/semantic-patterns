# Main-Text vs Appendix Boundary

Date:
- `2026-03-20`

Status:
- preliminary delivery-design boundary

## Principle

Main text should answer the paper’s core preliminary question with the smallest
set of clean, interpretable, persuasive artifacts.

Appendix should defend the main text:

- alternative estimators
- extra fixed-effect ladders
- extra sample trims
- technical validation details
- alternative variable definitions

Main text should not become a holding area for every interesting regression.

## Main Text

### Table 1

- `Summary Statistics and Coverage`

Why main text:
- defines the sample
- establishes the scale of the measures
- orients the reader before any regression table
- should be anchored on the ever-speaker annual panel rather than the narrower speaking-only sample

### Table 2

- `AI Patent Timing and Alignment on the Ever-Speaker Panel`

Why main text:
- first indispensable main-text regression table on the broader panel
- directly links narrative composition to AI patent outcomes at multiple calendar-time horizons
- should use AI patent outcomes rather than generic patent incidence

### Table 3

- `FE Ladder / Timing Robustness`

Why main text:
- shows whether the timing result is stable under standard fixed-effect and sample choices
- stays compact enough to support the main story without turning into an appendix dump

### Table 4

- `Credibility Metrics`

Why main text:
- moves beyond raw counts into the paper’s distinctive credibility constructs

### Main Figures

- time series of AI disclosure composition
- industry heterogeneity
- patent-alignment / mismatch visualization

## Appendix

### Technical Validation

- held-out benchmark details
- model benchmark matrix
- IRR / adjudication details
- sentence cleanup diagnostics
- keyword construction details

### Estimator Robustness

- extensive-margin `any AI patent` timing models
- logit variants
- Poisson / count models
- alternative functional forms

### Additional Design Sensitivity

- extra FE variants beyond the compact ladder
- extra SIC / industry splits
- high-tech only or special-sample splits if not needed in main text

### Alternative Construct Definitions

- `SpecMinusAct`
- alternative walk / talk analogues if later added
- mismatch variants once implemented

## Current Boundary Decision

As of this preliminary delivery stage:

- `Table 1` is main text
- `Table 2` is main text
- `Table 3` is the compact FE ladder / timing-robustness companion if it remains readable
- the current conditional validation table from the speaking-only panel moves to the appendix
- FE ladders beyond the compact headline comparison should not enter the paper until we decide whether they clarify or distract
- count models, Poisson models, and richer appendix-style robustness remain out of the main text for now
