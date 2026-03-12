# Tranche 1 Rubric Calibration v2.1

## Why Calibration Was Needed

The earlier tranche-1 diagnostic prelabels were mechanically correct but conceptually too broad on `Speculative`.

Observed failure pattern:
- generic AI risk, regulatory, cyber, and market language was often labeled `Speculative`
- some present-tense AI product or business-offering language was labeled too weakly
- a small number of extracted rows included heading or filing-noise fragments that should not influence canonical review

This created a skew toward `Speculative` that did not reflect the proposal's construct of AI-washing as firm-specific aspirational AI narrative without later observable capability.

## Proposal-Faithful v2.1 Rule Changes

### Actionable
Use `Actionable` only for current or past firm-specific AI deployment, embedded workflow use, operational execution, or a commercialized AI offering/product/service.

### Speculative
Use `Speculative` for firm-specific AI strategy, aspiration, intention, or expected benefit when the sentence does not provide concrete present operational evidence.

### Irrelevant
Use `Irrelevant` for generic AI market, regulatory, cyber, risk, boilerplate, or tangential mentions that do not function as a firm capability claim.

## Common False-Positive Patterns Now Mapped to Irrelevant

- generic AI/ML risk-factor language
- generic cyber or regulatory discussion mentioning AI
- market-wide AI commentary without a firm capability claim
- boilerplate mention of AI among many technologies

## Narrowed Actionable Override

Risk-section language is not automatically `Speculative` or `Actionable`.

It is `Actionable` only when it reveals actual current firm AI use or deployment.

Examples of what can still qualify:
- current AI underwriting system
- deployed AI-enabled workflow
- existing AI product or service offering

## Extraction Noise to Ignore in Calibration

The following are preprocessing issues, not rubric evidence:
- `Table of Contents` contamination
- page header/footer fragments
- filing-form/page markers
- standalone glossary or bullet fragments
- section-title prefixes that leak into sentence text

## Canonical Review Decision

- earlier tranche-1 `v2` prelabels remain diagnostic only
- canonical tranche-1 review now moves to `*_v2_1` files
- the first `40` rows of the regenerated `v2.1` review sheet must be checked before full tranche-1 canonical review resumes
