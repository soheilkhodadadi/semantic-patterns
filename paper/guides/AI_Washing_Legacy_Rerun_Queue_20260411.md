# AI Washing Legacy Rerun Queue

Date: 2026-04-11

This note converts the legacy rerun block in the master run sheet into a practical queue after the first pass through Tests 1-8.

## What looks strongest so far

- Test 1: mismatch surge through time remains a core descriptive result.
- Test 3: equal-weight post-filing long-short alpha is one of the strongest finance-style results.
- Test 7: post-ChatGPT mismatch increase is a strong credibility-shock result.
- Test 8: valuation is only interesting in the non-big refinement; financing remains weak.

## Cross-cutting refinement rule

For market, valuation, and mispricing-style tests:

1. run the baseline full-sample version first
2. if the signal is weak or diluted, run the non-big refinement
3. when still relevant, run `PatentMismatch x PostChatGPT` on the non-big sample

Use the matched-sample yearly median market cap when NYSE breakpoints are not locally available, and label it as a fallback non-big screen rather than a literal NYSE breakpoint replication.

## Priority queue

### Tier 1: must-run validation backbone

1. Table B1 — updated measurement audit table
2. Table B2 — updated attrition map on the expanded 2016-2025 panel
3. Table R1 — summary statistics on the expanded main panel
4. Figure R1 — AI disclosure volume and composition over time
5. Figure R2 — AI patent coverage over time

Reason:
- these are required to stabilize the paper backbone
- they update the preliminary-era evidence to the final hybrid panel
- they are low-risk and high-value for writing

### Tier 2: best legacy reruns for the main paper story

6. Table R6 — A/S ratio x PatentMismatch at t+1
7. Table R7 — A/S ratio x PatentMismatch at t+2
8. Figure R3 — A/S-ratio quantile mismatch alignment plot
9. Figure R4 — mismatch incidence over time and by industry
10. Table R3 — disclosure composition and AI patent timing

Reason:
- these speak directly to the measurement and credibility mechanism
- they complement Tests 1, 3, 7, and 8 without duplicating them
- they are better aligned with the current paper than broad AI-focus-only reruns

### Tier 3: conditional or appendix-first reruns

11. Table R2 — AI Focus and AI patent timing
12. Table R4 — actionable disclosure timing matrix
13. Table R5 — speculative-only disclosure timing matrix
14. Table R8 — reduced-baseline determinants
15. Table A1 — full multivariate determinants
16. Table A2 — mismatch-share intensity determinants

Reason:
- useful for appendix, robustness, or measurement detail
- less likely to move the headline story than Tier 2
- some overlap with what newer tests now capture more directly

## Practical next sequence

1. Freeze Test 8 as `non-big valuation refinement`, with the `PatentMismatch x PostChatGPT` version kept as a documented follow-up rather than the main table.
2. Move to Tier 1 legacy reruns.
3. After Tier 1, run Tier 2 in the listed order.
4. Only then decide which Tier 3 reruns are worth refreshing for the appendix.

## Current recommendation on legacy overlap

- Keep broad `AI_Focus` results, but do not let them dominate the queue.
- Prioritize reruns where `PatentMismatch` or the A/S structure is central.
- Treat non-big and post-ChatGPT refinements as reusable finance-style follow-up specs whenever baseline market/valuation results are diffuse.
