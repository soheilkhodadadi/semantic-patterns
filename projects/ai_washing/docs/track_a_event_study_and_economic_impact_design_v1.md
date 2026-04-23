# AI-Washing Track A Event-Study And Economic-Impact Design V1

## Purpose

This note turns the publication-upgrade ask into concrete empirical lanes.

It answers:
1. which economic-impact tests are most worth running first?
2. which nearby papers give us credible templates?
3. which tests belong in the first pass versus later robustness?
4. what WRDS data pulls and build steps are needed next?

## Current measurement posture

Classifier posture now strong enough for provisional downstream work:
- human reliability gate cleared on `IRR v3 rerun`
- kappa: `0.85`
- current provisional winner:
  - layered local base classifier
  - API-A selective defer (`gpt-5-mini`)
  - `conf49` as main operating point

Operational implication:
- it is now reasonable to build shadow economic analyses on top of the
  provisional hybrid classifier while the full deferred slice completes
- final paper-grade promotion should still wait for the merged hybrid output
  and final panel rebuild

## Literature anchors

### 1. Cohen, Malloy, and Nguyen (2020), `Lazy Prices`, Journal of Finance

Local file:
- `paper/literature/2020 - COHEN - Lazy Prices - The Journal of Finance.pdf`

What to borrow:
- use filing text as a market signal, not just as a narrative description
- test delayed incorporation, not only day-0 reaction
- build a long-short portfolio around disclosure-based credibility signals
- compare no-announcement-effect versus post-filing drift

What matters for us:
- this is the cleanest top-journal template for turning 10-K text changes into
  a market-efficiency / mispricing result
- our analog is not generic textual change; it is the credibility gap between
  AI disclosure and real AI capability / patent backing

### 2. Basnet et al. (2025), `Analyzing the market's reaction to AI narratives in corporate filings`, IRFA

Local file:
- `paper/literature/Basnet et al. - 2025 - Analyzing the market's reaction to AI narratives in corporate filings.pdf`

What to borrow:
- actionable / speculative / irrelevant narrative split
- within-firm fixed effects
- first-introduction treatment design
- Tobin's Q as a forward-looking valuation outcome
- innovation channels through R&D and patents
- peer penalty idea when competitors adopt credible AI narratives first

What matters for us:
- this is the closest published AI-disclosure analog to our own setting
- we should not copy it blindly because our novelty is the disclosure-patent
  mismatch and the stronger classifier infrastructure
- but it is the right benchmark for specification discipline

### 3. Li (2026), `AI Washing`

Local file:
- `paper/literature/AI_Washing_Mar2026.pdf`

What to borrow:
- separate short-run market reaction from longer-run performance
- explicitly model the gap between rhetoric and real investment
- use ChatGPT as a salience shock
- test institutional-investor discernment and managerial incentive channels

What matters for us:
- this is the closest direct competitor in story space
- our differentiation should be:
  - 10-K filing narrative credibility rather than earnings-call rhetoric alone
  - patent-backed or capability-backed mismatch in mandatory disclosure
  - filing-date event study and disclosure-specific drift

### 4. Brown and Tucker (2011), `Large-Sample Evidence on Firms' Year-Over-Year MD&A Modifications`, Journal of Accounting Research

Online source:
- `https://bear.warrington.ufl.edu/tucker/2010-12_MD%26A_paper.pdf`

What to borrow:
- document changes over time as information
- section-level modifications as design inspiration
- disciplined event-window and disclosure-change interpretation

### 5. You and Zhang (2009), `Financial reporting complexity and investor underreaction to 10-K information`, Review of Accounting Studies

Online source:
- `https://ideas.repec.org/a/spr/reaccs/v14y2009i4d10.1007_s11142-008-9083-2.html`

What to borrow:
- filing-date underreaction framing
- annual-report complexity as a source of delayed price incorporation
- direct link between 10-K information and post-filing return drift

### 6. Dambra, Mihov, and Sanz, `Unintended Real Effects of EDGAR: Evidence from Corporate Innovation`

Online source:
- `https://www.nber.org/system/files/working_papers/w27529/w27529.pdf`

What to borrow:
- disclosure technology / dissemination can move innovation behavior
- useful background for why market attention to disclosure can have real
  innovation consequences

### 7. Ante and Saggu (2025), `Quantifying a firm's AI engagement: Constructing objective, data-driven, AI stock indices using 10-K filings`

Online source:
- `https://www.sciencedirect.com/science/article/pii/S0040162524007637`

What to borrow:
- ChatGPT event-study validation for AI engagement signals in 10-K text
- thematic portfolio construction logic

What to borrow cautiously:
- this is useful as a nearby AI-specific market-reaction analog
- it is not a substitute for stronger finance-journal identification discipline

## First-pass empirical lanes

### Lane 1. Filing-date event study

Question:
- does the market reward credible AI disclosure and penalize mismatch at the
  filing date?

Core event date:
- SEC 10-K filing date

Main outcomes:
- `CAR[-1,+1]`
- `CAR[-2,+2]`

Main explanatory variables:
- level of AI disclosure credibility
- disclosure-patent mismatch indicator
- actionable AI narrative indicator
- interaction with post-ChatGPT period

Initial specification families:
1. filing-level cross-sectional regression of CAR on AI credibility / mismatch
2. firm fixed-effects panel around first actionable introduction
3. post-ChatGPT interaction to test whether the market reaction intensified

Why this lane is first:
- closest to Kuntara's request
- fastest path to an economics-facing result
- data requirements are clear and already partially audited

### Lane 2. Post-filing drift / lazy-prices test

Question:
- does the market initially overreact to AI narrative and then reverse, or fail
  to process low-credibility AI disclosure until later?

Main outcomes:
- buy-and-hold abnormal returns (`BHAR`) over `1`, `3`, `6`, and `12` months
- factor-adjusted portfolio returns

Main portfolio sorts:
1. long high-credibility AI adopters, short high-mismatch firms
2. long newly actionable firms, short speculative-only / irrelevant AI talkers
3. long patent-backed narrators, short disclosure-only narrators

Why this lane matters:
- this is the most direct way to quantify shareholder consequences of AI washing
- it also differentiates us from papers that stop at short-window reaction

### Lane 3. ChatGPT salience-shock design

Question:
- did the post-November-2022 environment magnify rewards to AI disclosure,
  especially for low-credibility narrators?

Preferred treatment logic:
- compare pre/post ChatGPT
- interact with ex ante disclosure credibility / mismatch
- test whether low-credibility AI narrators gain more short-run reaction but
  underperform later

Candidate specifications:
1. diff-in-diff on filing-level reaction
2. triple-difference with credibility group x post-ChatGPT x first-introduction
3. stacked event-time around filing dates in 2022-2025

Why this is useful:
- gives us identification language tied to a clear salience shock
- aligns with both stakeholder expectations and nearby AI literature

### Lane 4. Real-economy follow-through

Question:
- do credible AI narrators actually increase innovation and patenting while
  high-mismatch narrators do not?

Main outcomes:
- AI patent filings / intensity
- R&D intensity
- future productivity or profitability where feasible

Why this lane stays in scope:
- it is a natural bridge between the disclosure story and the market-reaction
  story
- it supports the interpretation of mismatch as misallocation rather than mere
  wording noise

## Recommended empirical sequence

### Step 1. Build the event-ready filing panel

Must include:
- firm identifier links to CRSP / Compustat
- SEC filing date
- source-year and filing metadata
- narrative measures
- patent-backed credibility / mismatch measures
- post-ChatGPT indicator

### Step 2. Run the first filing-date event study

Minimum version:
- daily returns
- market-adjusted CAR
- `[-1,+1]` and `[-2,+2]`
- AI credibility / mismatch as the main explanatory variable

### Step 3. Run the delayed-price lane

Minimum version:
- `1`, `3`, `6`, and `12` month BHAR or alpha
- long credible / short mismatch portfolio
- compare pre- and post-ChatGPT

### Step 4. Run the innovation follow-through lane

Minimum version:
- future patent activity and R&D intensity
- show whether credible disclosures are backed by real investment

### Step 5. Add robustness only after the first clean read

Candidate later robustness:
- factor-adjusted CAR instead of just market-adjusted CAR
- monthly long-horizon return robustness
- institutional ownership / fund flow response
- SEO or financing sensitivity

## What not to do first

Do not try to solve all of these at once:
- event study
- long-run drift
- institutional holdings
- valuation levels
- analyst response
- SEO incentives

That will slow the project and blur the first economic signal.

The first serious win is simpler:
- filing-date market reaction
- followed by delayed-price / portfolio evidence

## Immediate WRDS data pulls

Use the existing market-data posture note:
- `projects/ai_washing/docs/track_a_market_data_source_review_v1.md`

First required pulls:
1. `ccmsecd`
   - daily returns
   - prices
   - shares outstanding / market value fields needed for event study
2. `ccmfunda`
   - annual fundamentals for controls
3. factor returns / benchmark series
   - enough to compute market-adjusted or factor-adjusted abnormal returns
4. firm link table / identifier bridge
   - so SEC filing entities match CRSP / Compustat entities cleanly

Minimum event-ready outputs:
- firm-filing table with `filing_date`
- daily return panel around each filing date
- first CAR output table

## Differentiation from nearby papers

Our most defensible differentiated contribution is:
- mandatory-disclosure AI credibility, not only earnings-call AI rhetoric
- patent-backed or capability-backed mismatch as the economic signal
- filing-date event study plus delayed drift / portfolio evidence
- hybrid classifier with documented human-reliability gate rather than a loose
  text count alone

That is a better contribution than trying to out-copy the existing `AI Washing`
working paper on its own terrain.

## Decision rule

The first economics-facing result should be chosen by this order:
1. whichever lane is cleanest to implement from current data
2. whichever lane gives the clearest economic cost of AI washing
3. whichever lane most clearly differentiates us from existing AI-disclosure
   papers

Today, that points to:
1. filing-date event study
2. delayed-price / portfolio test
3. ChatGPT interaction

## Bottom line

The paper should not move forward as only a measurement paper.

The strongest next publication path is:
- use the provisional hybrid classifier to build an event-ready filing panel
- test short-window filing-date reaction to AI credibility / mismatch
- then test whether the pricing of low-credibility AI narrative reverses or
  underperforms over longer horizons

That is the most credible route to quantifying the shareholder consequences of
AI washing.
