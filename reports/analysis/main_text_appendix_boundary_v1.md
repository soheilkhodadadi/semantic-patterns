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

- `Disclosure Composition and AI Patent Timing`

Why main text:
- shows whether decomposition into actionable and speculative-only disclosure adds signal beyond broad AI-focus intensity
- keeps the core composition result separate and readable

### Table 4

- `Patent-Timing Matrix by Disclosure Type`

Why main text:
- mirrors the literature-style timing layout more closely
- shows the full `t-2` through `t+2` pattern with FE/sample variants in columns
- helps the reader see whether disclosure types are backward-looking, contemporaneous, or forward-looking

### Table 5

- `Credibility Metrics`

Why main text:
- can help benchmark which credibility-style constructs sharpen the broad AI-focus result
- should remain in the main text only if it clearly sharpens the story beyond Tables 2-4
- otherwise it should move to appendix and make room for the methodology-aligned `A_S x PatentMismatch` table once mismatch is implemented

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
- `Table 3` is main text as the composition-timing companion
- `Table 4 / Table 4B` are candidate main-text timing-matrix tables if they remain readable
- `Table 5 / Table 5B` are exploratory credibility tables and may move to appendix if they do not sharpen the main narrative
- the current conditional validation table from the speaking-only panel moves to the appendix
- FE ladders beyond the compact timing-matrix comparison should not enter the paper until we decide whether they clarify or distract
- count models, Poisson models, and richer appendix-style robustness remain out of the main text for now
