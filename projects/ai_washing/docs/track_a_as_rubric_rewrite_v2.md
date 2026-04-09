# AI-Washing Track A A/S Rubric Rewrite V2

## Purpose

This note updates the prior revised rubric with edge-case tie-breakers learned
from the finalized `IRR v2` adjudication pack.

`V1` already improved clarity on currentness, business-claim relevance, and
generic risk language. `V2` keeps that structure and only adds rules where the
adjudicated disagreements showed systematic gaps.

Base rubric:
- [track_a_as_rubric_rewrite_v1.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/projects/ai_washing/docs/track_a_as_rubric_rewrite_v1.md)

Adjudication source:
- `data/labels/v2/adjudication_boundary_revised_v2_final.parquet`

## What changed after adjudication

The main unresolved weakness was still `Speculative`.

The adjudicated disagreements show that `Speculative` was being overused in
three specific situations:
- future-looking language about clients or the market, not the focal firm
- trend or demand statements that mention AI but do not state a focal-firm
  capability
- sentences that contain future language but also disclose an already-existing
  platform, solution, or owned AI asset

There was also a smaller `Actionable vs Irrelevant` issue for acquisition and
biography-style references.

## Decision order

Keep the `V1` sequence:
1. relevance precondition
2. currentness gate
3. business-claim gate

Then apply the new `V2` tie-breakers below before finalizing the label.

## New V2 tie-breakers

### 1. Client future use is not the focal firm's AI claim

If a sentence is mainly about what clients, users, or other outside parties may
do with AI in the future, it should usually be:
- `Irrelevant`

Reason:
- the future-facing AI narrative belongs to the client or market participant,
  not the reporting firm

Example pattern:
- `These clients are consciously evaluating potential areas where AI-enabled technologies could be utilized in the future.`

### 2. Market trend, demand, or technology trajectory language is `Irrelevant`

If AI is discussed as a macro trend, demand driver, or technology trajectory,
without a concrete focal-firm capability claim, label:
- `Irrelevant`

This stays true even when the sentence implies the firm may benefit from the
trend.

Example patterns:
- generative AI will drive bandwidth demand
- proliferation of AI applications will accelerate content creation
- AI development paves the way for future autonomous services

### 3. Existing product or platform plus expected expansion can still be `Actionable`

If a sentence clearly states that a product, platform, or solution already
exists now, then trailing expectation or expansion language does not make it
`Speculative`.

Label:
- `Actionable`

Reason:
- the core operative claim is present capability
- the future clause is only about scaling or adoption, not about whether the
  capability exists

Example patterns:
- `This solution enables organizations ...`
- `... expand robotics offerings through the AI.ME platform ...`

### 4. Completed acquisition of an AI platform or provider can be `Actionable`

If the reporting firm has already completed an acquisition of an AI platform,
AI software asset, or AI provider, and the sentence states that completed
ownership relation as fact, treat it as:
- `Actionable`

Reason:
- the firm is disclosing a present owned AI asset or capability position, not
  just a generic exposure reference

Important limit:
- this does not mean every acquisition mention is `Actionable`
- if the sentence only describes deal context without a concrete present owned
  AI asset, it can still be `Irrelevant`

### 5. Biography or expertise references are not automatically `Irrelevant`

Biography-style sentences remain risky, but they should not be forced into
`Irrelevant` just because they are personnel-focused.

Use this rule:
- if the sentence only gives background about a person with no meaningful tie
  to current firm AI capability, label `Irrelevant`
- if the sentence identifies current firm leadership, provider role, platform
  ownership, or active expertise that is functioning as part of the firm's
  present AI capability story, it can be `Actionable`

This is a narrow exception, not a broad invitation to label all biographies as
`Actionable`.

## Updated short definitions

### `Actionable`

Use `Actionable` when the sentence makes a focal-firm present or past factual AI
claim, including:
- current product or platform capability
- current operating or internal use
- present investment or implementation already underway as fact
- present owned AI asset through a completed acquisition
- present capability conveyed through a current leadership/platform context
  rather than mere biography

### `Speculative`

Use `Speculative` when the sentence is still a focal-firm AI claim, but the AI
capability is not yet stated as present fact.

Typical cases:
- intends to build
- expects to deploy
- plans to integrate
- hopes to benefit
- mission or ambition statements without evidence of current capability

### `Irrelevant`

Use `Irrelevant` when AI is present but the sentence is not making a real
focal-firm capability or owned-asset claim.

Typical `V2` cases:
- market or industry trend statements
- generic AI risk or compliance language
- client-side future use
- future technology trajectories not tied to current firm capability
- biography references without a real current firm capability implication

## Practical summary

The `V2` correction is:
- reduce false `Speculative` labels for existing solutions, platforms, and
  completed AI asset ownership
- reduce false `Speculative` labels for market-trend statements that should be
  `Irrelevant`
- keep the `V1` posture that build/integrate/plan language is `Speculative`
  unless there is an independent present factual claim

## Intended use

This `V2` note is a prompt and benchmark calibration aid.

It should be used for:
- `held_out_v4` API prompt benchmarking
- hybrid selective-defer refinement
- the next blinded `IRR v3` handoff pack

It should not be treated as proof that the human IRR problem is solved.
