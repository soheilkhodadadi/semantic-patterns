# Filing-Date CAR Regressions

## Scope

This note records the first pilot filing-date event regressions on the matched filing sample.
The current surface is a pipeline-validation sample, not the full paper sample.

## Sample

- matched filings: `7355`
- unique `gvkey`: `2753`
- unique `permno`: `2758`
- years: `2016-2024`
- CAR core sample: `7200`
- CAR extended sample: `4460`
- BHAR 6m core sample: `6694`

## Headline read

- car_m1_p1_yearfe_core_hc3: share_actionable=0.0010 (p=0.797), share_speculative=-0.0094 (p=0.082), N=7200.
- car_m1_p1_post_core_hc3: share_actionable=0.0045 (p=0.325), share_speculative=0.0031 (p=0.629), N=7200.
- car_m1_p1_post_extended_hc3: share_actionable=0.0073 (p=0.323), share_speculative=0.0041 (p=0.664), N=4390.
- car_m1_p1_post_core_cluster_gvkey: share_actionable=0.0045 (p=0.316), share_speculative=0.0031 (p=0.617), N=7200.
- car_m2_p2_post_core_hc3: share_actionable=0.0075 (p=0.177), share_speculative=0.0051 (p=0.504), N=7196.
- bhar_6m_post_core_hc3: share_actionable=0.0419 (p=0.072), share_speculative=0.0463 (p=0.168), N=6694.

## Notes

- This is the pilot matched-filing event-study surface, not the final full-sample paper panel.
- Year fixed effects and explicit post-ChatGPT interactions are run as separate families because post_chatgpt is close to a time dummy.
- share_irrelevant is omitted as the baseline composition share.
- Pilot p-values use a normal approximation over HC3 or cluster-robust standard errors to keep the runner lightweight and stable in this environment.
