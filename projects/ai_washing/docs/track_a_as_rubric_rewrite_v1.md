# AI-Washing Track A A/S Rubric Rewrite V1

## Purpose

This note rewrites the `Actionable` / `Speculative` boundary using the first
`16`-row probe slice from the current classifier audit pack.

The goal is not to freeze a final publication rubric immediately. The goal is
to produce a clearer next-draft rule set that we can probe, benchmark, and
then test with a second human rater.

## Why a rewrite is warranted

The current A/S boundary is not failing at random. The probe slice shows
repeated confusion in a small set of sentence types:
- current capability vs future intent
- implementation in progress vs already deployed use
- risk/competition references that mention AI but do not actually claim present
  capability
- generic model/tooling references that are real but not clearly a disclosed
  business capability
- acquisition/exposure references

That means the next best move is not a blind model change. It is a clearer
label rule.

## Revised decision order

### Step 0. Relevance precondition

Before applying the A/S split, ask:

`Does the sentence make a firm-specific AI business or operational claim at all?`

If the answer is no, label:
- `Irrelevant`

Typical `Irrelevant` cases under this revised posture:
- generic competition or market references
- generic AI risk or dependency statements
- acquisition or ownership references without a present firm capability claim
- generic AI/tooling references without a meaningful firm-specific use claim

Hard rule:
- if the sentence does not itself assert AI use, AI capability, or AI
  implementation by the reporting firm, default to `Irrelevant` even if AI is
  strategically important in the surrounding context

Only if the sentence passes this relevance precondition should it move to the
A/S boundary.

## Revised A/S boundary

For relevant sentences, apply two gates.

### Gate 1. Currentness gate

Ask:

`Is the sentence making a present or already operative claim, rather than mainly a future, modal, conditional, or in-progress claim?`

The sentence **fails** the currentness gate if it is mainly framed by language
such as:
- intend
- plan
- may
- expect
- would
- could
- in the future
- will continue to
- remain ongoing
- continue to build / integrate / develop

These can still be relevant, but they usually point toward `Speculative`, not
`Actionable`.

The sentence can still **pass** the currentness gate if it contains a clear
present-tense capability clause and only then adds a trailing future, risk, or
improvement clause. In that case, anchor the label to the strongest present
business claim rather than the trailing hedge.

### Gate 2. Business-claim gate

Ask:

`Is AI tied to a concrete product, workflow, service, operating process, or named business function?`

The sentence **passes** this gate when it describes things like:
- a current AI-enabled product capability
- a currently supported workflow or use case
- current operational use of AI or ML in a business process
- a concrete internal process that is already using AI or ML
- a current measurement, risk-management, or operational decision process that
  explicitly relies on AI or ML models

The sentence **fails** this gate when AI is only:
- broad strategic context
- a named investment area
- generic tooling or methodology without a real operating claim
- competition/risk context
- acquisition/exposure context

Important clarification:
- internal operating processes count
- the sentence does **not** need to describe a customer-facing product to be
  `Actionable`
- but it does need to tell us what the AI is currently doing in a real
  business or operating function
- if the sentence only describes methodology, tooling architecture, or
  analytics ingredients without saying what present business function AI is
  performing, it should not pass this gate

## Proposed rule

### `Actionable`

Label `Actionable` only if:
1. the sentence passes the relevance precondition
2. it passes the currentness gate
3. it passes the business-claim gate

Short version:
- `Actionable = relevant + current + concrete business use`

### `Speculative`

Label `Speculative` if:
1. the sentence passes the relevance precondition
2. but fails either:
   - the currentness gate, or
   - the business-claim gate in a way that still reflects a real firm-facing AI
     strategy or intended capability

Short version:
- `Speculative = relevant AI claim, but not yet a present concrete business use`

### `Irrelevant`

Label `Irrelevant` if the sentence does not pass the relevance precondition.

Short version:
- `Irrelevant = AI is mentioned, but the sentence is not really making a firm
  AI business/operational claim`

## Boundary clarifications from the probe slice

### Usually `Actionable`

- present-tense product/functionality claims
- present operational workflow support
- present internal use of ML models in a concrete operating process
- present use of AI/ML inside a measurement, risk, or decision system when the
  function is concrete and already operative

Examples from the probe slice:
- `AIQ also enables a series of AI-driven origination tasks...`
- `This Infrastructure-as-a-Service enables use cases ... for AI/ML workflows.`
- metric/tooling references only when they clearly describe a current operating
  process rather than just general methods language
- `Our calculations of MAP rely upon ... machine learning models...`
- `We manage, identify and assess risks ... including through the use of machine learning...`

### Usually `Speculative`

- intention-to-implement statements
- investment priorities
- in-progress build/integration language without a clear present deployment
- ongoing R&D plus “may begin to use”

Examples:
- `In the future, we ... may incorporate artificial intelligence...`
- `We intend to focus on six key investment areas: AI...`
- `We continue to build and integrate AI into our offerings...`
- `We are making investments in AI initiatives ... to recommend ... enhance ... develop...`

### Usually `Irrelevant`

- competition/risk statements where AI is only the context
- acquisition/exposure references
- broad generic references that do not disclose current firm capability

Examples:
- `If we are unable or slow to develop, adopt, and deploy generative AI...`
- `...we may become subject to additional competition...`
- acquisition of a firm owning an AI platform, without a current use claim by
  the reporting firm

## Tie-breakers for hard cases

Use these tie-breakers in order:

1. If the sentence is mainly a risk, competition, dependency, or acquisition
   statement, label `Irrelevant` unless it also independently states a current
   AI-enabled business capability.
2. If the sentence says the firm is investing, building, integrating, or
   planning AI "to" achieve some goal, but does not state that the capability
   already exists, label `Speculative`.
3. If the sentence says the firm currently uses AI or ML in a named internal
   workflow, decision, measurement, risk, or operating process, label
   `Actionable`.
4. If a sentence mixes a current capability clause with a trailing risk or
   improvement clause, label by the main operative clause. A present capability
   clause outranks a trailing hedge, purpose clause, or risk clause.
5. If a sentence mentions AI as a strategic area or initiative without telling
   us what is currently in use, label `Speculative`.

## Probe-slice implications

Under this rewrite, the first `16`-row probe slice implies:
- `Actionable` should be retained for current enablement and current internal
  operating-process claims
- several prior `Actionable` disagreements should move to `Speculative`
  because they are really investment/build/integration statements
- several prior `Speculative` disagreements should move to `Irrelevant`
  because they are risk or competition context rather than disclosure of a
  firm AI capability

## What this rewrite is trying to fix

This rewrite is mainly trying to stop these bad transitions:
- `Speculative -> Actionable` because the sentence sounds ambitious or detailed
- `Actionable -> Speculative` because the sentence contains future-looking or
  risk language even though it still describes a current capability

The rule tries to separate:
- genuine current business use
from:
- future intention
- implementation in progress
- strategic priority
- risk context

## Recommended next use

1. apply this draft rubric to the `16`-row probe slice
2. check whether the disagreements become cleaner and more defensible
3. if yes, promote it into a small rubric benchmark cycle
4. only after that:
   - clean or expand the training set
   - test probability tuning

## Bottom line

The revised A/S boundary should be:
- first, ask whether the sentence is even making a real firm-specific AI claim
- then require both:
  - a currentness signal
  - a concrete business-use signal

That is a cleaner and more defensible starting point than the current looser
boundary.
