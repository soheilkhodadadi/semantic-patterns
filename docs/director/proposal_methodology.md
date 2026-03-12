# Proposal Methodology

This document is the canonical paraphrased record of the research design in the AI-washing proposal. It exists so roadmap decisions, labeling rules, and review gates can reference a stable repo-local methodology source instead of repeatedly reopening the proposal files.

## Source

- Primary source: `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/PhD-soheil/Thesis/Semantics/article/After Proposal Defence/AI washing proposal.pdf`
- Supporting source: `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/PhD-soheil/Thesis/Semantics/article/After Proposal Defence/AI washing proposal.docx`
- Scope of this document: paraphrased methodology and construct definitions only

## Core Construct

The study is not only a sentence classifier. It is a predictive credibility-measure project.

Working construct:
- AI-washing is speculative firm AI narrative without later observable AI capability.
- The label system exists to build firm-year measures that predict subsequent AI capability proxies.
- Later observable capability proxies include AI-related patents and AI-skills job postings.

## Label Semantics

### Actionable
- Present or past firm-specific AI deployment.
- Embedded workflow, productized use, operational implementation, or measurable execution.
- A sentence can be `Actionable` even in a risk section if it clearly discloses current firm AI use or deployment.

### Speculative
- Firm-specific aspirational, exploratory, or forward-looking AI narrative without operational proof.
- Plans, intentions, ambitions, transformation claims, or promised capabilities that do not show current implementation.

### Irrelevant
- Generic market, industry, cyber-risk, regulatory, or boilerplate AI mentions.
- Tangential AI references that do not function as firm capability claims.
- Generic AI risk language is usually `Irrelevant`, not `Speculative`.

## Borderline Rules

- Generic AI regulatory, cyber, market, or legal-risk language is `Irrelevant` unless it discloses current firm AI deployment.
- A sentence is not `Speculative` simply because it is uncertain or risk-oriented; it must still be a firm-specific AI narrative claim.
- A sentence is `Actionable` only when current or realized implementation evidence is explicit.
- Firm-specific future AI ambition without present execution evidence is `Speculative`.

## Data Design

- Active development window: `2021–2024`
- Publication target scope: all publicly traded firms
- Desired long-horizon publication target: `2000–2024` when source availability permits
- Core disclosure source: firm 10-K filings

## IRR Design

The proposal implies a stricter IRR design than a generic reliability spot-check.

Required design points:
- stratified sample covering at least `100` firms
- balanced by industry and year
- two independent human raters
- third adjudicator for disagreement resolution
- report Cohen's kappa overall and by class

## Named Measures

The proposal defines the following firm-year measures.

- `AI Focus = log(1 + AI sentences)`
- `log(1 + A)` where `A` is the count of `Actionable` AI sentences
- `log(1 + S)` where `S` is the count of `Speculative` AI sentences
- `SpecShare = S / (A + S)`
- `CredAI = z(A) - z(S)`
- `A_S = log(1 + A / (1 + S))`

These measures should appear explicitly in later roadmap phases and outputs rather than being left implicit.

Potential later filing-level derived variables include:
- `AnyActionable = 1` if a filing contains at least one actionable AI sentence
- `SpeculativeOnly = 1` if a filing contains speculative AI sentences but no actionable AI sentence

## Predictive Specifications

Baseline predictive validation should use:
- AI patents and AI-skills job postings as capability outcomes
- horizons `l in {0,1,2}`
- firm and year fixed effects as the baseline specification
- industry×year fixed effects as a robustness specification

## AI-Washing Specification

The proposal's AI-washing interpretation is tied to:
- `A_S`
- `A_S x PatentMismatch`

This is a predictive-validation design, not only a descriptive disclosure taxonomy.

## Calibration and Freeze Policy

The proposal supports bounded rubric refinement during development.

Allowed during development:
- revise the rubric when tranche-level evidence shows the labels do not reflect the proposal's construct
- compare candidate measures against predeclared validation outcomes such as patents and job postings

Not allowed after rubric freeze:
- open-ended label drift during publication-scale execution
- unconstrained significance chasing

Project policy derived from this:
- rubric refinement is allowed during development calibration
- rubric must freeze before publication-scale deployment
- predictive-validity should be directional and predeclared, not an unbounded significance target

## Implementation Adaptations

The current implementation may use the same versioned keyword family across disclosure and patent filtering.

This is a deliberate implementation choice in the repo workflow and is treated as compatible with the proposal-aligned roadmap unless later evidence shows it is harmful.

## Roadmap Usage

This methodology source should inform:
- `docs/labeling_protocol.md`
- `director/model/roadmap_model.yaml`
- iteration review methodology-alignment checks
- later firm-year measure construction and predictive-validity gates

If the methodology changes, patch this document first, then patch the roadmap and protocol.
