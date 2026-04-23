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

## 7. Packet E First Read

`Test 21` is now in place as the first analyst table:

- table: [test_21 analyst discernment docx](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/docx/test_21_analyst_discernment_20260423_aiw_v3_2_test_21_analyst_discernment_main_v1.docx)
- figure: [test_21 analyst discernment figure](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_2/figures/test_21_analyst_discernment_20260423_aiw_v3_2_test_21_analyst_discernment_main_v1.png)

Current read:

- `PatentMismatch` predicts lower analyst coverage at `t+1`: `-0.0823`, `p=0.004`
- `PatentMismatch` does not yet produce a clear dispersion result
- `PatentMismatch` does not yet produce a clear net-revision result

Interpretation:

- the first analyst signal looks more like `lower intermediary attention` than `higher measured analyst disagreement`
- that is still useful, because it gives a plausible reason why weak market differentiation and later cleanup can coexist
- but it is not yet the full analyst-discernment story; `test_22` and any later guidance extension still matter

Tentative placement:

- keep `test_21` as a live candidate for either the main text or high appendix
- do not lock its placement until `test_22` tells us whether analyst monitoring sharpens the interpretation

## 8. Next Dependency

The next key empirical question is whether analyst monitoring changes the later consequences of low-credibility AI disclosure. That is now the reason `test_22` matters so much.
