# v3.1 Non-Market Rewrite Notes

Date: 2026-04-23
Status: working draft for paper revision after Packets A-C.

## 1. Core repositioning

The paper should no longer be written as if the main contribution is a strong market-underreaction result.

The stronger version of the paper now is:
- we build and audit a filing-based disclosure-credibility measure;
- that measure predicts later technology-realization patterns;
- AI-talking firms flagged as low-credibility do not receive clean market separation at filing or in stricter post-filing designs;
- but they do show economically coherent non-market consequences later, especially lower profitability and higher R&D intensity at `t+2`.

That is a cleaner and more defensible story.

## 2. Safe claim language

Use language like:
- "markets do not cleanly distinguish between higher- and lower-credibility AI disclosure at filing"
- "the market evidence is mixed and benchmark-sensitive"
- "the strongest results arise in non-market consequences rather than in abnormal-return tests"
- "low-credibility AI disclosure predicts weaker later operating performance and higher later R&D effort within the AI-talking sample"

Avoid language like:
- "the market underreacts to AI-washing"
- "the market corrects AI-washing later"
- "PatentMismatch identifies mispricing"

## 3. Proposed results order

1. Measurement and auditability
2. Descriptive rise of low-credibility AI disclosure
3. Construct validation against later AI realization
4. Real-outcome dynamics in the AI-talking sample
5. Financing / valuation refresh as a secondary consequence block
6. Mixed market-evidence section

## 4. Which new assets fit where

### Main-text candidates
- Packet B main table:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_17_real_outcome_dynamics_20260422_aiw_v3_1_test_17_real_outcome_dynamics_main_v1.docx`
- Packet B heatmap for appendix or main-text exposition:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/figures/test_17_real_outcome_dynamics_20260422_aiw_v3_1_test_17_real_outcome_dynamics_main_v1.png`
- Packet C table if the paper wants one valuation / incentive extension block:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_18_financing_incentives_refresh_20260423_aiw_v3_1_test_18_financing_incentives_refresh_main_v1.docx`

### Appendix / robustness candidates
- Packet A construct-variant screen:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/docx/test_16_construct_variant_screen_20260422_aiw_v3_1_test_16_construct_variant_screen_main_v1.docx`
- Packet A heatmap:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/figures/test_16_construct_variant_screen_20260422_aiw_v3_1_test_16_construct_variant_screen_main_v1.png`
- Packet C data-gap note:
  - `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/paper/generated/v3_1/snippets/test_18_financing_incentives_refresh_20260423_aiw_v3_1_test_18_financing_incentives_refresh_main_v1_data_gap_note.md`

## 5. Specific empirical takeaways to carry into the draft

### Packet A
- Canonical `PatentMismatch` remains usable and should stay the main construct.
- `StrictPatentMismatch` is not worth promoting.
- `ApplicationMismatch` is a sensible appendix robustness variant.
- `WeakPatentRelative` is strong mechanically, but it is a component, not the paper's main disclosure-credibility construct.

### Packet B
- This is now the strongest new consequences table.
- Canonical `PatentMismatch` predicts lower `ROA` at `t+2` and higher `R&D/assets` at `t+2`.
- `LowCredibility` alone points in the same direction on `ROA t+2`.
- `Sales growth` and `CAPX/assets` are much weaker and should not be oversold.

### Packet C
- Full-sample valuation and financing results are mostly null.
- The interesting part is concentrated in non-big valuation outcomes.
- Issuance-style financing proxies remain weak in the current panel.
- Governance should be framed as a next data wave, not as a missing regression we forgot to run.

## 6. Suggested narrative paragraph for the results section

"Taken together, the new tests shift the paper away from a strong market-underreaction framing and toward a more defensible disclosure-credibility and consequences framing. The filing-based PatentMismatch construct remains informative in later technology-realization tests and survives comparison with nearby construct variants. Within the AI-talking sample, firms flagged as low-credibility do not receive clean market separation at filing or in stricter post-filing return designs, but they do exhibit economically coherent later non-market outcomes: lower profitability and higher R&D intensity at longer horizons. This pattern is consistent with low-credibility AI disclosure being associated with weaker near-term realized capability and costlier subsequent effort to build it."

## 7. Recommended next conference-facing move

Before another empirical expansion, pause and re-score the paper from a strict-referee perspective:
- what is now the main claim;
- which tables are indispensable;
- which mixed market tables should stay but move later;
- whether one more data pull for governance / institutions is worth the time.

