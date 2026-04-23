# AI-Washing v3.2 Rewrite Memo

Date: 2026-04-23  
Purpose: preserve the current paper-facing interpretation of the strongest `v3.1` and `v3.2` results, with placement guidance and exact output references.

## 1. Current Paper Position

The strongest version of the paper is now:

1. measurement and auditability of low-credibility AI disclosure;
2. validation against later AI realization;
3. non-market consequences and organizational response;
4. mixed, benchmark-sensitive market evidence;
5. external scrutiny that disciplines disclosure composition without silencing AI talk.

That is a stronger and more defensible story than a headline claim about market underreaction.

## 2. Keep / Demote Map

### Main-text candidates

1. `test_16_construct_variant_screen`
   - role: validation anchor for the construct
   - best use: show that the canonical construct remains preferable to looser alternatives
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_16_construct_variant_screen_20260422_aiw_v3_1_test_16_construct_variant_screen_main_v1.docx`

2. `test_17_real_outcome_dynamics`
   - role: strongest non-market consequence table
   - key read: weaker later profitability together with higher later R&D effort
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_17_real_outcome_dynamics_20260422_aiw_v3_1_test_17_real_outcome_dynamics_main_v1.docx`

3. `test_18_financing_incentives_refresh`
   - role: secondary consequence / valuation extension, especially for non-big firms
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_18_financing_incentives_refresh_20260423_aiw_v3_1_test_18_financing_incentives_refresh_main_v1.docx`

4. `test_20_comment_letter_cleanup`
   - role: strongest new `v3.2` external-scrutiny result
   - preferred use: main text if we want one external-discipline table after the real-outcomes section
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_20_comment_letter_cleanup_20260423_aiw_v3_2_test_20_comment_letter_cleanup_main_v1.docx`
   - figure: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_20_comment_letter_cleanup_20260423_aiw_v3_2_test_20_comment_letter_cleanup_main_v1.png`

### Main-text but softened

5. `test_09_factor_adjusted_alpha`
   - role: narrow market table if we keep a market section
   - required framing: equal-weight and benchmark-surviving, but not broad value-weight evidence of mispricing
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_09_factor_adjusted_alpha_20260422_aiw_v3_1_test_09_factor_adjusted_alpha_main_v1.docx`

### Appendix / robustness

6. `test_19_sec_comment_letter_scrutiny`
   - role: Packet D viability and incidence audit
   - placement: appendix or short robustness paragraph only
   - reason: AI-specific comment-letter counts are too thin for a headline incidence table
   - key asset: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_19_sec_comment_letter_scrutiny_20260423_aiw_v3_2_test_19_sec_comment_letter_scrutiny_main_v1.docx`

7. `test_10`, `test_12`, `test_13`, `test_15`
   - role: market-discipline checks that narrow the claim
   - placement: appendix or discussion support
   - reason: useful for honesty and defense, but they do not support a strong pricing-anomaly statement

## 3. Packet D Definitions and Timing

### What `narrow AI` means in `test_19`

`Narrow AI scrutiny` is a conservative phrase match inside SEC comment-letter metadata and text using explicit AI terms only:

- `artificial intelligence`
- `machine learning`
- `generative ai`
- `chatgpt`
- `large language model(s)`
- `deep learning`
- `neural network(s)`
- `foundation model(s)`

This deliberately avoids vague technology language.

### What `broad AI` means in `test_19`

`Broad AI scrutiny` includes all `narrow AI` matches plus abbreviation-style references such as:

- `AI` / `A.I.`
- `LLM` / `LLMs`

So the broad definition is not a general technology bucket. It is still AI-oriented, just less conservative than the narrow phrase list.

### What the current `t:t+1` window means

For `test_19`, the annual panel row is a filing-year observation in the AI-talking universe. The outcomes are coded over the filing year and the following year:

- `any_comment_t_t1`
- `ai_comment_narrow_t_t1`
- `ai_comment_broad_t_t1`

So this is not a same-day filing-event design. It asks whether the annual disclosure state in year `t` is followed by SEC scrutiny in years `t` or `t+1`.

### Why `test_20` is more useful

`Test 20` switches from raw incidence to within-firm change around first scrutiny.

It defines an event year as the first matched comment-letter year and then uses event time:

- `t-1`: one annual observation before first scrutiny
- `t`: scrutiny year
- `t+1`, `t+2`: subsequent annual observations

The main sample keeps only `active AI disclosers`, meaning the firm talks about AI in both `t-1` and `t+1`.

That matters because it separates:

- `composition cleanup`
from
- `simple disappearance of AI disclosure`

## 4. Packet D Read

### Test 19: viability and audit

Key facts:

- matched SEC comment-letter rows: `10,244`
- matched firms: `1,001`
- annual sample counts:
  - any comment `1,104`
  - narrow AI `17`
  - broad AI `25`

Interpretation:

- there is enough density to open a scrutiny packet;
- there is not enough density for a strong AI-specific scrutiny-incidence headline;
- the right use is appendix / audit / robustness context.

Keyword-audit addendum:

- I re-checked the saved matched-comment metadata against a broader shared AI term set borrowed from the patent and sentence pipelines:
  - `natural language processing`
  - `nlp`
  - `computer vision`
  - `reinforcement learning`
  - `language model(s)`
  - plus the existing explicit AI / LLM phrases
- That broader metadata screen added `0` extra issue-phrase / taxonomy matches beyond the current `broad AI` Packet D definition.
- So the thin AI-specific incidence is not obviously an artifact of an underbroad issue-phrase screen.
- The remaining way to enlarge Packet D materially would be a manual audit of raw letter bodies, not another automatic broadening of the current metadata definition.

### Test 20: scrutiny without silence

Main sample:

- any-comment active sample: `70` firms
- AI-related active sample: `11` firms

Headline results in the main any-comment sample:

- `A/S` at `t+1`: `+0.1796`, `p=0.007`
- `SpecShare` at `t+2`: `-0.1051`, `p=0.025`
- `PatentMismatch` at `t+1`: `-0.1143`, `p=0.073`
- `AI_Focus` rises after scrutiny

Paper-facing interpretation:

- oversight is associated with cleaner disclosure composition;
- the result is not a silence effect, because AI attention remains and even rises;
- the best label is `scrutiny without silence`.

## 5. Suggested Results Flow

A stronger revised order is:

1. mismatch measure and auditability
2. rise of low-credibility AI disclosure
3. construct validation against later patents / applications
4. real-outcome dynamics
5. external scrutiny and disclosure cleanup (`test_20`)
6. non-big valuation extension
7. mixed market evidence with narrow claims only

## 6. Writing Guidance

### Safe language

- `consistent with`
- `associated with`
- `disciplines disclosure composition`
- `active AI disclosers rebalance toward more credible composition after scrutiny`
- `market evidence is mixed and benchmark-sensitive`

### Avoid

- `proves`
- `causes`
- `the market clearly underreacts`
- `SEC scrutiny directly fixes AI-washing`

## 7. Packet E Read

### Test 21. Analyst discernment

- table: [test_21 analyst discernment docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_21_analyst_discernment_20260423_aiw_v3_2_test_21_analyst_discernment_main_v1.docx)
- figure: [test_21 analyst discernment figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_21_analyst_discernment_20260423_aiw_v3_2_test_21_analyst_discernment_main_v1.png)

Read:

- `PatentMismatch` predicts lower analyst coverage at `t+1`: `-0.0823`, `p=0.004`
- `PatentMismatch` does not yet produce a clear dispersion result
- `PatentMismatch` does not yet produce a clear net-revision result

Interpretation:

- the first analyst signal looks more like `lower intermediary attention` than `higher measured disagreement`
- that is still useful, because it gives a plausible reason why weak market differentiation and later cleanup can coexist

### Test 22. Analyst monitoring interaction

- table: [test_22 analyst monitoring docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_22_analyst_monitoring_interaction_20260423_aiw_v3_2_test_22_analyst_monitoring_interaction_main_v1.docx)
- figure: [test_22 analyst monitoring figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_22_analyst_monitoring_interaction_20260423_aiw_v3_2_test_22_analyst_monitoring_interaction_main_v1.png)

Read:

- interaction on future mismatch persistence: `0.0179`, `p=0.765`
- interaction on future AI grants: `-0.2084`, `p=0.002`
- interaction on `ROA t+2`: `0.0451`, `p=0.065`

Interpretation:

- analyst coverage does not reduce future mismatch persistence
- higher coverage is associated with a weaker later `ROA` penalty for mismatch firms
- but higher coverage also makes the later AI-grant shortfall of mismatch firms look sharper, not smaller

Best current reading of Packet E:

- analysts do not deliver a clean `monitoring fixes the problem` result
- instead, the evidence looks more like `selective intermediary attention`
- mismatch firms receive less coverage overall
- when coverage is high, technological under-realization becomes more sharply visible, while the operating penalty is partly attenuated

Tentative placement:

- `test_21` is a live main-text or high-appendix candidate if we want an intermediary-attention result
- `test_22` is more naturally a high appendix or discussion table unless later tests make the mixed interaction more central to the story

### Test 23. Analyst-coverage split specifications

- table: [test_23 analyst coverage splits docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_23_analyst_coverage_splits_20260423_aiw_v3_2_test_23_analyst_coverage_splits_main_v1.docx)
- figure: [test_23 analyst coverage splits figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_23_analyst_coverage_splits_20260423_aiw_v3_2_test_23_analyst_coverage_splits_main_v1.png)

Read:

- `PatentMismatch -> ROA t+2` is strongest in the lower-attention slices:
  - lower half: `-0.0471`, `p=0.042`
  - bottom quartile: `-0.0644`, `p=0.032`
- `PatentMismatch -> Log(1 + AI grants) t+1` is strongest in the higher-attention slices:
  - upper half: `-0.2105`, `p=0.002`
  - top quartile: `-0.2369`, `p=0.028`
- `PatentMismatch -> PatentMismatch t+1` remains null across the slices

Interpretation:

- the split design sharpens Packet E, but not into a simple `more analysts fix the problem` result
- instead:
  - low-coverage firms carry the later operating penalty more clearly
  - high-coverage firms show the sharper future-grant shortfall
- the cleanest paper-facing read is therefore:
  - analysts are part of the information environment,
  - but they do not mechanically eliminate mismatch;
  - different outcome margins become visible in different attention environments

Tentative placement:

- `test_23` is a strong appendix / discussion table
- promote only if we want a richer intermediary subsection rather than a single analyst table

## 8. Next Dependency

The next key empirical question is whether governance or leadership structures explain more of the gap than analysts do. That is now the reason Packet F matters.

## 9. Packet F Read

### Test 24. Science/technology appointment response

- full-sample table: [test_24 scitech appointments docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_24_scitech_appointment_response_20260423_aiw_v3_2_test_24_scitech_appointment_response_main_v1.docx)
- big-firm refinement: [test_24 scitech appointments big docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_24_scitech_appointment_response_20260423_aiw_v3_2_test_24_scitech_appointment_response_big_v1.docx)
- figure: [test_24 scitech appointments big figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_24_scitech_appointment_response_20260423_aiw_v3_2_test_24_scitech_appointment_response_big_v1.png)

Setup:

- source: Audit Analytics `feed17_director_and_officer_chan`
- event filter: appointed roles only
- broad outcome: provider-tagged `is_scitech_pers`
- narrower outcomes:
  - c-level science/technology appointments
  - title-based technology-lead appointments

Density:

- appointment rows in the panel universe: `56,267`
- science/technology appointment rows: `1,658`
- c-level science/technology rows: `940`
- technology-lead rows: `459`

Read:

- full sample is directionally positive, but not sharp enough for a headline claim
  - `PatentMismatch -> any science/tech appointment (t+1:t+2)`: `0.0144`, `p=0.238`
  - `PatentMismatch -> c-level science/tech appointment (t+1:t+2)`: `0.0147`, `p=0.123`
- the big-firm refinement is materially cleaner
  - `PatentMismatch -> any science/tech appointment (t+1:t+2)`: `0.0398`, `p=0.022`
  - `PatentMismatch -> c-level science/tech appointment (t+1:t+2)`: `0.0256`, `p=0.060`
- the narrow technology-lead cut stays positive but not precise

Interpretation:

- this packet does not say mismatch firms immediately fix the capability gap
- it does suggest a later organizational response in bigger firms, where formal leadership additions are more feasible and more visible
- that is a useful complement to the earlier real-outcome evidence:
  - smaller firms show the clearer later operating penalty
  - bigger firms are the ones that more visibly add science/technology leadership afterward

Tentative placement:

- the big-firm refinement is a live main-text or high-appendix candidate
- the full-sample table is better as support / appendix

### Test 25. Executive incentives and low-credibility AI disclosure

- table: [test_25 exec incentives docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_25_exec_incentive_mismatch_20260423_aiw_v3_2_test_25_exec_incentive_mismatch_main_v1.docx)
- figure: [test_25 exec incentives figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_25_exec_incentive_mismatch_20260423_aiw_v3_2_test_25_exec_incentive_mismatch_main_v1.png)

Setup:

- source: ExecuComp `anncomp`
- CEO row rule: use the highest-`TDC1` CEO-designated row in each firm-year when more than one CEO row appears
- predictors are lagged one year:
  - CEO equity-award share of total compensation
  - CEO ownership percentage excluding options
  - log CEO total pay

Coverage:

- lagged CEO-linked AI-talking rows: `1,007`
- matched firms: `303`
- this is therefore a large-firm / ExecuComp-covered slice, not a full-universe result

Read:

- full matched sample is modest
- the cleaner results appear where incentive salience is highest:
  - big-firm sample:
    - `PatentMismatch -> CEO ownership pct (t-1)`: `0.1038`, `p=0.000`
  - post-ChatGPT sample:
    - `PatentMismatch -> CEO equity-award share (t-1)`: `0.1787`, `p=0.041`
    - `PatentMismatch -> CEO ownership pct (t-1)`: `0.0170`, `p=0.036`
    - `PatentMismatch -> log CEO pay (t-1)`: `0.0528`, `p=0.100`
  - post-ChatGPT `A/S` also moves in the expected inverse direction for ownership:
    - `A/S -> CEO ownership pct (t-1)`: `-0.0369`, `p=0.000`

Interpretation:

- this is one of the cleaner explanatory Packet F results so far
- stronger CEO incentive alignment with equity upside is associated with more low-credibility AI disclosure in the covered universe, especially after ChatGPT
- that gives the paper a more concrete incentives channel than the earlier financing proxies

Tentative placement:

- live main-text candidate inside Packet F
- caveat to state explicitly: this is an ExecuComp-covered, mostly larger-firm slice

### Test 26. Board monitoring and low-credibility AI disclosure

- table: [test_26 board monitoring docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_26_board_monitoring_20260423_aiw_v3_2_test_26_board_monitoring_main_v1.docx)
- figure: [test_26 board monitoring figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_26_board_monitoring_20260423_aiw_v3_2_test_26_board_monitoring_main_v1.png)

Setup:

- source: Risk Directors `rmdirectors`
- merge rule: aggregate board structure to ticker-year, lag one year, then link to the AI-talking annual panel
- primary monitoring proxies:
  - average outside public boards held by directors
  - governance committee share
  - audit committee share
  - board size

Coverage:

- board ticker-years: `19,835`
- lagged board-linked AI-talking rows: `2,269`
- matched firms: `812`
- post-ChatGPT matched rows: `1,058` before regression-level control filtering

Read:

- this packet is more useful than a generic governance appendix dump
- all-sample monitoring terms are already directionally informative:
  - `PatentMismatch -> avg outside public boards (t-1)`: `-0.0621`, `p=0.050`
  - `LowCredibility -> avg outside public boards (t-1)`: `-0.0512`, `p=0.099`
  - `LowCredibility -> governance committee share (t-1)`: `-0.1888`, `p=0.064`
- the sharper result comes in the post-ChatGPT slice:
  - `PatentMismatch -> board size (t-1)`: `-0.0736`, `p=0.002`
  - `LowCredibility -> board size (t-1)`: `-0.0765`, `p=0.002`
  - `A/S -> board size (t-1)`: `0.0643`, `p=0.007`
- the big-firm sample keeps the outside-board effect directionally similar:
  - `PatentMismatch -> avg outside public boards (t-1)`: `-0.0580`, `p=0.059`

Interpretation:

- some board-monitoring structures appear to matter for disclosure quality
- the cleaner proxies are not every committee label; they are broader monitoring capacity:
  - how externally seasoned the board is;
  - how large the board is in the post-ChatGPT period
- that gives Packet F a governance explanation that fits the current paper better than a simple market-discipline story

Tentative placement:

- strong appendix or internet-appendix candidate
- possible main-text support table if we want one dedicated governance/explanation result alongside the incentive table

### Test 27. Board technical human capital and low-credibility AI disclosure

- table: [test_27 board tech HC docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_27_board_tech_human_capital_20260423_aiw_v3_2_test_27_board_tech_human_capital_main_v1.docx)
- figure: [test_27 board tech HC figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_27_board_tech_human_capital_20260423_aiw_v3_2_test_27_board_tech_human_capital_main_v1.png)

Setup:

- source: BoardEx
- board-seat filter: supervisory and executive directors only
- narrow proxy:
  - lagged share of board members with distinctive prior technical-leadership titles
- broader proxy:
  - lagged technical-human-capital share, which adds a sparse STEM-education overlay

Coverage:

- lagged board-tech linked rows: `3,247`
- matched firms: `1,155`
- the technical-leadership proxy is the operative one; the STEM-only layer is sparse and mainly useful as a conservative add-on

Read:

- this is a supportive governance-capability result, not a dominant Packet F headline
- all-sample disclosure-quality results are directionally useful:
  - `PatentMismatch -> tech leadership share (t-1)`: `-0.4810`, `p=0.065`
  - `PatentMismatch -> tech human-capital share (t-1)`: `-0.5158`, `p=0.045`
  - `LowCredibility -> tech leadership share (t-1)`: `-0.4403`, `p=0.096`
- the big-firm slice keeps the direction and slightly sharpens one margin:
  - `LowCredibility -> tech leadership share (t-1)`: `-0.5666`, `p=0.080`
  - `A/S -> any tech human capital (t-1)`: `0.1050`, `p=0.041`
- the post-ChatGPT slice is weak, so this is not a clean late-period governance story

Interpretation:

- boards with more genuine technical human capital appear less likely to be associated with low-credibility AI disclosure
- that helps in two ways:
  - it gives the paper a capability-side robustness check beyond patents alone
  - it supports the idea that mismatch is partly about who inside the firm can credibly oversee AI claims
- but the effect is supportive rather than decisive, so it should stay below the stronger incentive and board-monitoring results

Tentative placement:

- appendix or internet appendix
- useful to cite in the main text when arguing that capability-side governance structure matters, even if the full table stays out of the main paper

## 10. Packet G Read

### Test 28. Public SEC 13F institutional discernment

- table: [test_28 public 13F docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_28_public_13f_institutional_discernment_20260423_aiw_v3_2_test_28_public_13f_institutional_discernment_main_v1.docx)
- figure: [test_28 public 13F figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_28_public_13f_institutional_discernment_20260423_aiw_v3_2_test_28_public_13f_institutional_discernment_main_v1.png)

Setup:

- source: official SEC Form 13F structured data sets
- frequency choice:
  - year-end Q4 holdings snapshots
  - linked to the annual panel through CRSP historical CUSIP mapping
- outcomes:
  - next-year 13F ownership share
  - change in next-year ownership share
  - next-year holder breadth
  - next-year holder concentration HHI

Coverage:

- CRSP-linked panel rows: `7,378`
- linked firms: `2,805`
- t+1 ownership-linked rows: `4,278`
- t+1 ownership-linked firms: `1,543`
- SEC Q4 years processed and cached: `10` (`2016` through `2025`)

Read:

- this is a useful public-data null, not a strong institutional-discernment result
- in the all-sample 13F panel:
  - `PatentMismatch -> next-year ownership share`: `0.0085`, `p=0.305`
  - `PatentMismatch -> change in ownership share`: `0.0111`, `p=0.302`
  - `PatentMismatch -> next-year holder breadth`: `-0.0079`, `p=0.648`
  - `PatentMismatch -> next-year concentration HHI`: `0.0045`, `p=0.309`
- the big-firm slice does not strengthen the expected story:
  - `PatentMismatch -> next-year ownership share`: `0.0178`, `p=0.051`
  - that is directionally opposite a simple disciplining interpretation
- the only mild directional pattern is on the disclosure-composition side:
  - higher `A/S` is associated with weaker subsequent ownership growth and lower breadth in the big-firm slice
- the post-ChatGPT split is not estimable under firm fixed effects because the ownership-linked post sample contributes only one observation per firm

Interpretation:

- public 13F ownership does not currently support a clean claim that institutional investors systematically step away from low-credibility AI disclosers
- that is still informative:
  - it limits how strongly we can lean on an institutional-discernment story
  - it keeps the paper honest by showing that not every intermediary/ownership channel disciplines the behavior in a clean way
- this packet is therefore better as a boundary result than as a main-text mechanism table

Tentative placement:

- appendix or internet appendix
- useful to reference briefly in the main text if we want to say we also checked public institutional ownership and did not find strong discernment there

## 11. Packet H Read

### Test 29. SEC AI-washing enforcement salience DID

- table: [test_29 enforcement DID docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_29_sec_ai_washing_enforcement_did_20260423_aiw_v3_2_test_29_sec_ai_washing_enforcement_did_main_v1.docx)
- figure: [test_29 enforcement DID figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_29_sec_ai_washing_enforcement_did_20260423_aiw_v3_2_test_29_sec_ai_washing_enforcement_did_main_v1.png)
- writer packet: [test_29 writer packet](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/writer_packets/test_29_sec_ai_washing_enforcement_did_20260423_aiw_v3_2_test_29_sec_ai_washing_enforcement_did_main_v1_writer_packet.md)

Setup:

- public event anchor: SEC AI-washing enforcement actions on March 18, 2024
- main treatment fixed in `2022` among firms that talk about AI and are already flagged as `PatentMismatch`
- alternative treatments fixed in `2022`:
  - `LowCredibility`
  - `ApplicationMismatch`
- post period:
  - `2024-2025`
- placebo / pretrend year:
  - `2023`

Coverage:

- analysis sample: `8,055` firm-years across `1,611` firms
- main treated firms: `457`

Read:

- main-treatment post-2024 DID:
  - `SpecShare`: `-0.0839`, `p<0.001`
  - `A/S`: `0.2907`, `p<0.001`
  - `PatentMismatch`: `-0.3121`, `p<0.001`
  - `AI_Focus`: `-0.1044`, `p=0.110`
- alternative treatment definitions are directionally consistent:
  - `LowCredibility in 2022`
    - `SpecShare`: `-0.1215`, `p<0.001`
    - `A/S`: `0.3368`, `p<0.001`
    - `PatentMismatch`: `-0.2606`, `p<0.001`
  - `ApplicationMismatch in 2022`
    - `SpecShare`: `-0.1042`, `p<0.001`
    - `A/S`: `0.3155`, `p<0.001`
    - `PatentMismatch`: `-0.2634`, `p<0.001`

Interpretation:

- this is a useful regulatory-salience result:
  - after the SEC's March 18, 2024 AI-washing actions, pre-exposed firms look more likely to rebalance disclosure toward less speculative and more credible composition
- importantly, `AI_Focus` does not fall much
  - so the evidence is more `cleanup without silence` than `stop talking about AI`
- the main caveat is that the `2023` placebo coefficients are already directional for the composition outcomes
  - that means this should not be written as a clean causal enforcement-DID
  - the right paper-facing label is `regulatory salience / acceleration`

Tentative placement:

- strong appendix or supporting main-text extension
- promote only if paired with explicit pretrend discipline in the text
