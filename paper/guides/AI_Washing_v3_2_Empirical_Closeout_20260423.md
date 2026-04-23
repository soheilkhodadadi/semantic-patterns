# AI-Washing v3.2 Empirical Closeout

Date: 2026-04-23  
Purpose: decide whether the empirical lane is ready to close, whether `test_29` is main-text safe, and whether `test_31` or any greenwashing-bridge work is still worth doing before rewriting.

## 1. Bottom Line

Current recommendation:

- the empirical lane is ready to close
- `test_29` is already suitable for the main text if we write it with the right discipline
- `test_31` should stay deferred
- the next highest-value move is to switch to manuscript rewriting, not to open another empirical packet

The threshold from here should be strict:

- only run another empirical test if it can plausibly beat one of the current main-text keepers

## 2. Does Test 29 Need More Work To Be Main-Text Safe?

My answer is no on the data side, yes on the writing side.

What is already good enough:

- strong post-2024 cleanup in `SpecShare`, `A/S`, and `PatentMismatch`
- consistent direction across alternative 2022 exposure definitions
- a public, legible external shock that a referee will naturally expect us to check
- a useful substantive result: cleanup without silence

What still has to happen in the manuscript:

1. call it a `regulatory salience / acceleration` result, not a clean causal DID
2. mention the `2023` placebo direction explicitly in the text or table note
3. pair it conceptually with `test_20`, so the paper shows two versions of scrutiny-related cleanup:
   - firm-specific comment-letter scrutiny
   - broad public enforcement salience
4. avoid language like `the SEC caused firms to stop AI-washing`

So there is nothing more I think we need to run for `test_29` before putting it in the main text.

## 3. Quick Greenwashing-Methods Review

I checked the nearby greenwashing literature mainly for one question:

- would a `claims vs. actions bridge` test add something essential before we start writing?

### Method lesson 1: greenwashing work is dominated by two measurement logics

The recent systematic methodological review says firm-level greenwashing measures mostly fall into:

- `selective disclosure`
- `decoupling`

Source:
- [Lublóy, Keresztúri, and Berlinger (2025), "Quantifying firm-level greenwashing: A systematic literature review"](https://www.sciencedirect.com/science/article/pii/S0301479724033851)

Why that matters for us:

- our paper already does both in an AI setting
- the text-based disclosure side is the selective-disclosure side
- the later patent realization side is the action / realization side
- `PatentMismatch` is already a decoupling-style construct

So conceptually, we are already doing the core greenwashing move.

### Method lesson 2: selective-disclosure papers often benchmark claims against bad outcomes or missing substantive follow-through

A recent selective-disclosure paper studies whether firms disclose negative sustainability events and finds high under-disclosure, with limited help from formal reporting frameworks.

Source:
- [Roszkowska-Menkes, Aluchna, and Kamiński (2024), "True transparency or mere decoupling? The study of selective disclosure in sustainability reporting"](https://www.sciencedirect.com/science/article/pii/S1045235423001612)

Key lesson for us:

- the high-value test is not “more claims data” by itself
- the high-value test is a disciplined comparison between communication and substantive realization or scrutiny

We already have that logic in:

- `test_16` and `test_17` through later patent outcomes
- `test_20` and `test_29` through scrutiny and cleanup
- `test_30` through financing-window deterioration and partial unwind

### Method lesson 3: regulation is a standard and credible greenwashing determinant

The carbon-disclosure greenwashing literature finds stricter climate-related regulation is associated with less greenwashing.

Source:
- [Mateo-Márquez, González-González, and Zamora-Ramírez (2022), "An international empirical study of greenwashing and voluntary carbon disclosure"](https://www.sciencedirect.com/science/article/pii/S0959652622021679)

Key lesson for us:

- our `test_29` already covers this broad insight in an AI-specific way
- that lowers the urgency of creating another bridge-style regulation test before rewriting

### Method lesson 4: market reactions in greenwashing are context-dependent, not broad and uniform

A recent event study on greenwashing allegations finds reactions depend on firm size and allegation materiality / compliance salience.

Source:
- [Dorfleitner, Eckberg, Utz, and Brehm (2025), "What drives stock market reactions to greenwashing? An event study of European companies"](https://www.sciencedirect.com/science/article/pii/S1544612325020495)

Key lesson for us:

- this supports what we already learned from the AI-washing side
- if we revisit the market lane later, we should keep targeting narrow, context-heavy designs rather than broad sorts
- `test_32` already moves in exactly that direction

## 4. What This Means For Test 31

`test_31_greenwashing_claims_vs_actions_bridge` is not wrong. It is just not the best use of time before rewriting.

Why I would defer it:

- the paper already has an internal claims-actions bridge through later AI patent realization
- the paper already has scrutiny-based cleanup results
- the paper already has incentive timing around issuance windows
- the paper already has a narrower state-dependent market refinement
- a greenwashing bridge now would mostly be conceptual spillover or future-project infrastructure, not a current-paper blocker

So my recommendation is:

- do not run `test_31` before rewriting
- keep it as a future bridge for a later cross-domain or greenwashing project

## 5. Remaining Empirical Gaps Before Writing

I do not see a remaining empirical gap that is both:

- obvious enough that a strong referee would expect it immediately, and
- likely enough to beat the current main-text keepers

What we do still need is not new data work. It is packaging and disciplined writing.

## 6. Rewrite-Ready Packet

I created a rewrite-start packet here:

- [rewrite start packet](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/rewrite_start_packet_20260423)

It is meant to be the handoff point from empirical work to manuscript revision.

## 7. Practical Stop Rule

From here, the clean stop rule is:

1. close the empirical lane
2. open a rewriting branch
3. rewrite from the selected keeper set
4. only reopen empirical work if, during writing, we discover a missing table that would clearly outrank one of the current main-text keepers

## 8. Final Recommendation

The project is ready to move into writing mode.

If we want to be disciplined and maximize paper quality, the next branch should be a rewriting branch, not another empirical branch.
