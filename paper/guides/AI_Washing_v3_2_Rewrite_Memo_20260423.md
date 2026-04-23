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
