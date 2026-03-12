# Tranche 1 Rubric Calibration v2.2

## Why v2.1 was still insufficient

The tranche-1 `v2.1` slice improved raw agreement materially, but it still left two systematic issues:

1. `Actionable` was still too narrow in practice.
   - Requiring visible technical detail made genuinely checkable firm claims look non-actionable.
   - Present-tense statements such as "we offer", "we provide", "we have used", "we invest", and "we have expertise" can function as verifiable firm capability claims even without technical detail.

2. Generic AI risk language was still over-considered as a capability signal.
   - Generic cyber, regulatory, or market risk language in Item 1A often mentions AI without making a firm capability claim.
   - Those sentences should default to `Irrelevant` unless they disclose present use, investment, or current capability.

A smaller but still important issue remained in extraction quality:
- title prefixes
- table-of-contents fragments
- page header/footer leakage
- glossary or bullet fragments
- malformed parenthesis noise

These issues need to be reduced before tranche-1 labels are suitable for second- and third-rater review.

## Rubric v2.2 rule changes

### Actionable
A sentence is `Actionable` when it makes a firm-specific claim that is presently or historically checkable, including:
- current or past AI deployment
- embedded workflow or operational use
- current investment, resource allocation, or capability-building that is checkable
- present-tense AI expertise
- commercialized AI offering, product, or service

### Speculative
A sentence is `Speculative` when it is firm-specific but mainly aspirational, strategic, future-looking, or hard to verify/refute, including:
- intended AI strategy
- expected benefits
- opportunity language
- exploration or aspiration without current proof

### Irrelevant
A sentence is `Irrelevant` when it does not function as a firm capability claim, including:
- generic AI market commentary
- generic cyber/regulatory/risk language
- boilerplate or tangential AI mentions

## Borderline decisions from the reviewed slice

- Generic Item 1A risk language defaults to `Irrelevant`.
- Risk-section language becomes `Actionable` only if it reveals current use, present investment, or current capability.
- "We may find opportunities" / "we intend to" / "we aim to" remains `Speculative`.
- "We offer / we provide / we have used / we invest / we have expertise" can be `Actionable` if the statement is firm-specific and checkable.

## Workflow decision

- `v2` and `v2.1` tranche-1 files remain diagnostic only.
- Canonical tranche-1 review is paused pending a rebuilt and cleaner `slice40` under rubric `v2.2`.
- The next calibration step is:
  1. rebuild the current `40`-row slice from raw filings
  2. regenerate assistive prelabels on that rebuilt slice under rubric `v2.2`
  3. manually review the rebuilt slice
  4. only then decide whether full tranche-1 `240`-row regeneration is justified
