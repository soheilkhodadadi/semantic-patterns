# AI-Washing v3.2 Publication Roadmap

Date: 2026-04-23  
Status: Active execution roadmap for the post-`v3.1` external-wave packet sequence.  
Built from:

- `paper/guides/AI_Washing_v3_1_Referee_Memo_20260423.md`
- `paper/guides/AI_Washing_v3_1_External_Wave_Menu_20260423.md`

## 1. Purpose

`v3.1` answered the question:

"What survives if we stress-test the original market-heavy story?"

`v3.2` answers the next question:

"What additional packets can materially strengthen the paper using realistic, readable data?"

This is not a reset. It is a deeper second wave that keeps the strongest `v3.1` results and builds outward from them.

## 2. v3.2 Thesis

The working thesis for `v3.2` is:

- the filing-based AI-disclosure credibility measure is already validated enough to keep;
- the biggest remaining upside is not another return transform;
- the biggest remaining upside is to show how external scrutiny, analysts, boards, and incentives interact with low-credibility AI disclosure;
- the paper gets stronger when it shows not only that the disclosure measure predicts later outcomes, but also who notices, who disciplines it, and which firms respond.

## 3. v3.2 Lane Structure

`v3.2` is organized into four active packets and one optional future bridge.

### Packet D. Scrutiny

Goal:

- test whether low-credibility AI disclosure attracts external SEC scrutiny;
- test whether scrutiny changes subsequent disclosure composition.

Core tests:

1. `test_19_sec_comment_letter_scrutiny`
2. `test_20_comment_letter_cleanup`

Status after first pass (2026-04-23):

- `test_19` is best kept as a viability and incidence audit; AI-specific comment-letter counts are too thin for a standalone headline scrutiny-incidence result.
- `test_20` is the stronger Packet D result: among active AI disclosers, first SEC scrutiny is followed by lower speculative share, higher A/S, and lower PatentMismatch, while AI Focus rises.
- Packet D therefore currently supports a `scrutiny without silence` story: oversight does not suppress AI talk, but it can discipline disclosure composition among firms that continue to talk about AI.

### Packet E. Intermediaries

Goal:

- test whether analysts recognize or constrain low-credibility AI disclosure.

Core tests:

3. `test_21_analyst_discernment`
4. `test_22_analyst_monitoring_interaction`
5. `test_23_analyst_coverage_splits`

Status after refinement pass (2026-04-23):

- `test_21` shows a clear intermediary-attention result: mismatch firms receive lower later analyst coverage.
- `test_22` does not deliver a simple `monitoring fixes the problem` interaction.
- `test_23` sharpens the picture, but in a mixed way:
  - the later `ROA` penalty is clearer in lower-coverage firms;
  - the future AI-grant shortfall is sharper in higher-coverage firms.
- Packet E is therefore useful, but it currently supports a `heterogeneous intermediary attention` story more than a clean analyst-discipline headline.

### Packet F. Governance and Incentives

Goal:

- test whether boards, senior-leadership structure, and managerial incentives explain or moderate low-credibility AI disclosure.

Core tests:

6. `test_24_scitech_appointment_response`
7. `test_25_exec_incentive_mismatch`
8. `test_26_board_monitoring`
9. `test_27_board_tech_human_capital`

Status after first pass (2026-04-23):

- `test_24` is useful and more interesting after a size refinement than in the raw full sample.
- Full-sample appointment response is directionally positive but not precise.
- The big-firm refinement is cleaner:
  - mismatch predicts more later science/technology appointments;
- the c-level appointment cut is marginal and directionally aligned;
- the narrow technology-lead cut remains too imprecise for a headline use.
- `test_25` is one of the cleaner explanatory results in Packet F:
  - stronger lagged CEO ownership predicts more mismatch in the big-firm ExecuComp slice;
  - post-ChatGPT mismatch also rises with lagged CEO equity-award share and lagged CEO ownership;
  - the result is naturally limited to the ExecuComp-covered large-firm universe, but that is acceptable for an incentives lane.
- `test_26` gives Packet F a usable board-monitoring result:
  - broader outside-board exposure is associated with less mismatch in the matched board sample and remains directionally similar in big firms;
  - larger boards are associated with less `PatentMismatch` and less `LowCredibility` in the post-ChatGPT slice, with a corresponding increase in `A/S`;
  - governance-committee and audit-share terms are directionally supportive, but less precise than the outside-board and board-size proxies.
- `test_27` is a supportively useful BoardEx result rather than a headline one:
  - lagged board technical human-capital share is associated with less mismatch in the matched sample;
  - the narrow technical-leadership share is also directionally negative for `LowCredibility`, especially in big firms;
  - the effect weakens in the post-ChatGPT slice, so this lane is better for appendix / internet appendix than for the core Packet F text.
- Packet F therefore has a viable `organizational catch-up in bigger firms` opening, and that justifies continuing to incentives and board structure rather than stopping here.
- Packet F is now strong enough to justify continuing, but the next tests should stay disciplined:
  - keep governance results in the paper only where they sharpen explanation rather than add noise;
  - prefer the cleaner incentive, board-monitoring, and narrow board-tech proxies over a long list of weak committee-detail specifications.

### Packet G. Ownership

Goal:

- test whether institutional ownership discriminates against low-credibility AI disclosure using public SEC 13F data rather than blocked WRDS ownership tables.

Core test:

10. `test_28_public_13f_institutional_discernment`

Status after first pass (2026-04-23):

- `test_28` is a disciplined public-data build, but it does not produce a strong institutional-discernment result.
- In the matched 13F sample:
  - `PatentMismatch` is essentially null for next-year ownership share, ownership change, holder breadth, and holder concentration;
  - the only directional signal is that higher `A/S` is associated with weaker subsequent ownership growth and slightly lower breadth in the big-firm slice.
- The post-ChatGPT split is not estimable under firm fixed effects because the ownership-linked post sample contributes only one observation per firm.
- Packet G therefore currently works as a useful null / boundary result rather than a headline empirical contribution.

### Packet H. Optional Bridge / Future Work

Goal:

- preserve high-value spillovers for the current paper or future greenwashing projects.

Candidate tests:

11. `test_29_sec_ai_washing_enforcement_did`
12. `test_30_capital_raising_timing`
13. `test_31_greenwashing_claims_vs_actions_bridge`
14. `test_32_market_reaction_in_issue_windows`
15. `test_33_post_enforcement_market_split`

Status after first pass (2026-04-23):

- `test_29` is stronger than a pure bridge test and is worth keeping.
- The main result is a clear post-2024 disclosure-composition cleanup among firms already exposed to low-credibility AI disclosure in 2022:
  - lower `SpecShare`
  - higher `A/S`
  - lower `PatentMismatch`
  - little evidence that firms simply stop talking about AI
- Alternative pre-shock exposure definitions using `LowCredibility` and `ApplicationMismatch` give the same directional pattern.
- The important limitation is that `2023` placebo coefficients are already directional for the composition outcomes.
- Packet H therefore currently supports a `regulatory salience / acceleration` story rather than a clean causal enforcement-DID claim.
- This makes `test_29` a useful paper-facing extension, but one that should be written with explicit pretrend discipline.
- `test_30` is also worth keeping and is cleaner than the older broad financing-outcome lane.
- Around first large equity-issuance windows:
  - `LowCredibility`, `ApplicationMismatch`, and `PatentMismatch` rise sharply into the issuance year;
  - those credibility-deterioration measures partly unwind in the following year;
  - `AI_Focus` keeps rising through and after the issue year.
- Packet H therefore now contributes two distinct paper-facing extensions:
  - regulatory salience and cleanup after SEC attention;
  - financing-window timing consistent with temporary promotional intensification rather than silence.
- `test_32` is now complete and gives the best narrow market follow-on to Test 30.
- In filing-year return regressions, outside issue windows `PatentMismatch` predicts weaker `BHAR[+2,+63]`, but the `PatentMismatch × IssueWindow` interaction is positive and significant:
  - full sample: `+0.0716`, `p=0.038`
  - non-big sample: `+0.0918`, `p=0.068`
- Filing-date `CAR[-1,+1]` remains null, so the useful signal is again in the short post-filing window rather than the immediate event reaction.
- Packet H therefore now contributes a third, narrower market result:
  - the mismatch-return relation is materially less negative inside financing windows than outside them.
- Follow-on checklist after Tests 29 and 30:
  - narrow the market block using these new event definitions rather than broad full-sample sorts;
  - issue-window market interactions are now done and worth keeping;
  - a quick direct post-enforcement market screen was weak and limited by 2024-only return coverage, so formalizing that result is currently low priority;
  - postpone the greenwashing bridge until after the next repositioning checkpoint.

## 4. Tiering and Priority

## Empirical Closeout Status

Closeout note:

- [AI_Washing_v3_2_Empirical_Closeout_20260423.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/guides/AI_Washing_v3_2_Empirical_Closeout_20260423.md)

Current recommendation:

- the empirical lane is ready to close
- `test_29` is main-text safe with disciplined framing
- `test_31` remains deferred
- any further empirical work should clear a high bar and beat one of the current main-text keepers

## Tier 1: Run first

These are the highest-value tests with the best combination of upside and feasibility.

1. `test_19_sec_comment_letter_scrutiny`
2. `test_20_comment_letter_cleanup`
3. `test_21_analyst_discernment`
4. `test_22_analyst_monitoring_interaction`
5. `test_23_analyst_coverage_splits`

## Tier 2: Run after first results are in

These are likely valuable, but should use what we learn from Tier 1.

6. `test_24_scitech_appointment_response`
7. `test_25_exec_incentive_mismatch`
8. `test_26_board_monitoring`
9. `test_27_board_tech_human_capital`

## Tier 3: Open only after a deliberate checkpoint

These are useful but heavier or more optional.

10. `test_28_public_13f_institutional_discernment`
11. `test_29_sec_ai_washing_enforcement_did`
12. `test_30_capital_raising_timing`
13. `test_31_greenwashing_claims_vs_actions_bridge`
14. `test_32_market_reaction_in_issue_windows`

## 5. Packet Logic

The sequencing is intentional.

### Why Packet D first

If comment-letter scrutiny works, it gives the paper something the current version lacks:

- an external enforcement / scrutiny result;
- a reason markets may look mixed while regulators still care;
- a dynamic disclosure-adjustment channel.

That is high-value and highly legible.

### Why Packet E second

Analysts are the cleanest next information-intermediary test because:

- the data are readable now;
- the literature already treats them as monitors;
- they let us test discernment without overclaiming a return anomaly.

### Why Packet F third

Governance and incentives are more construction-heavy and easier to overdo.
They should be guided by what we learn from scrutiny and analyst evidence.

### Why Packet G later

Public 13F is feasible, but it is a new ingestion lane.
It should not slow down higher-value readable-now tests.

## 6. What Success Looks Like

The best-case `v3.2` paper is no longer just:

- validated text measure;
- weaker later outcomes;
- mixed market evidence.

The best-case `v3.2` paper becomes:

- validated disclosure-credibility measure;
- later real-outcome consequences;
- SEC scrutiny is more likely for low-credibility AI disclosure;
- disclosure adjusts after scrutiny;
- analysts and/or boards partially discipline the behavior;
- stronger incentives and weaker oversight help explain why the behavior occurs.

That is a much stronger paper.

## 7. Stop / Go Rules

To keep the project disciplined, each packet has a stop/go rule.

### Packet D stop/go

Proceed with Packet E regardless, but:

- if AI-specific scrutiny counts are too thin, keep `test_19` as an audit-plus-pilot and shift more weight to `test_20` or a broader technology-scrutiny variant.

### Packet E stop/go

- if analyst discernment is strong, the market section can be rewritten around intermediary attention rather than returns;
- if analyst results are weak, do not force analyst-monitoring rhetoric and shift more emphasis to governance/incentives.

### Packet F stop/go

- if governance and incentive tests do not differentiate cleanly, keep only the strongest one or two and do not turn the paper into a governance omnibus.

### Packet G stop/go

- open only if Tier 1 and Tier 2 are already stable and we still want one additional investor-discernment extension.

## 8. Operational Lane

`v3.2` should use separate roots from `v3.1`.

Source-of-truth outputs:

- `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/`

Paper-facing outputs:

- `paper/generated/v3_2/`

The manuscript remains in:

- `paper/full paper/ai_washing_v3.0/`

until the `v3.2` evidence wave is mature enough to justify a fresh writing pass.

## 9. Writing Implications

We still do not rewrite the paper fully yet.

But `v3.2` is now explicitly targeting stronger sections for the later manuscript revision:

- scrutiny / enforcement
- information intermediaries
- governance and incentives

Those sections will sit between:

- the core validation block
- and the later mixed market-evidence block

## 10. Immediate Next Steps

1. create the `v3.2` operational run sheet with exact contracts;
2. scaffold Packet D;
3. run `test_19_sec_comment_letter_scrutiny`;
4. evaluate event counts and match quality;
5. decide whether `test_20` should remain narrow AI scrutiny or broaden to technology/disclosure scrutiny.

## 11. Definition of Done For v3.2 Planning

The planning phase is complete when:

- the packet sequence is fixed;
- each test has a named contract;
- the output lane is versioned;
- Packet D has started.
