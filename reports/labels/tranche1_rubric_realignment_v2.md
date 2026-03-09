# Tranche 1 Rubric Realignment v2

## Why the original tranche-1 prelabels were misaligned

The original tranche-1 diagnostic prelabels over-assigned `Speculative`. The main
failure mode was treating generic AI risk, cybersecurity, regulatory, and market
language as if it were firm-specific speculative AI narrative. That behavior does
not match the proposal's construct of AI-washing, which is about speculative firm
AI claims without later observable capability.

The diagnostic tranche also showed a smaller but real `Actionable` drift. Some
sentences were labeled `Actionable` even though they only mentioned technology
change, acquisitions, or AI-adjacent positioning without clear present or past
firm-specific AI deployment.

## Proposal-faithful label rules

- `Actionable`: current or past firm-specific AI deployment, embedded workflow use,
  operational execution, or productized implementation.
- `Speculative`: firm-specific aspirational or forward-looking AI narrative without
  operational evidence.
- `Irrelevant`: generic market, industry, regulatory, cyber-risk, boilerplate, or
  tangential AI mention.

## Borderline decisions adopted in v2

- Generic AI risk or regulatory discussion is usually `Irrelevant`.
- Risk-section language is `Actionable` only when it clearly reveals current firm
  AI use or deployment.
- References to AI as a general technology trend, industry context, or threat
  vector are `Irrelevant`.
- Future-looking AI ambitions become `Speculative` only when the sentence is
  describing the firm's own intended AI use, strategy, or expected capability.

## Common tranche-1 false-positive patterns now mapped to Irrelevant

- Generic cyber-risk sentences about attackers using AI
- Generic statements that AI or ML introduces business or compliance risk
- General discussion of industry technology change involving AI
- Boilerplate or glossary-style references to AI/ML

## Common tranche-1 false-positive Actionable patterns now narrowed

- General references to adapting to AI or technology change without implementation
- Corporate positioning language that mentions AI but does not show present use
- Acquisition or platform references without disclosed operational deployment

## Operational decision

- `data/labels/v1/labeling_batch_v1_prelabeled.csv` and
  `data/labels/v1/labeling_batch_v1_filled.csv` remain diagnostic-only artifacts.
- Canonical tranche-1 review moves to the rubric-v2 artifacts:
  - `data/labels/v1/labeling_batch_v1_prelabeled_v2.csv`
  - `data/labels/v1/labeling_batch_v1_filled_v2.csv`
- Tranche-1 canonical labeling resumes only after rubric-v2 prelabels are regenerated.
