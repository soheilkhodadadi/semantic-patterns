# First Filing-Date CAR Regressions V1

## Scope

This note records the first pilot filing-date event regressions on the matched filing sample.
The current surface is a pipeline-validation sample, not the full paper sample.

## Sample

- matched filings: `54`
- unique `gvkey`: `14`
- unique `permno`: `14`
- years: `2021-2024`
- CAR core sample: `54`
- CAR extended sample: `42`
- BHAR 6m core sample: `52`

## Headline read

- car_m1_p1_yearfe_core_hc3: share_actionable=0.0043 (p=0.942), share_speculative=-0.1306 (p=0.382), N=54.
- car_m1_p1_post_core_hc3: share_actionable=-0.0170 (p=0.812), share_speculative=-0.2043 (p=0.339), N=54.
- car_m1_p1_post_extended_hc3: share_actionable=0.0151 (p=0.881), share_speculative=-0.3512 (p=0.162), N=42.
- car_m1_p1_post_core_cluster_gvkey: share_actionable=-0.0170 (p=0.621), share_speculative=-0.2043 (p=0.322), N=54.
- car_m2_p2_post_core_hc3: share_actionable=-0.0658 (p=0.507), share_speculative=-0.1682 (p=0.529), N=54.
- bhar_6m_post_core_hc3: share_actionable=-0.2847 (p=0.492), share_speculative=-0.6386 (p=0.326), N=52.

## Notes

- This is the pilot matched-filing event-study surface, not the final full-sample paper panel.
- Year fixed effects and explicit post-ChatGPT interactions are run as separate families because post_chatgpt is close to a time dummy in the 2021-2024 pilot sample.
- share_irrelevant is omitted as the baseline composition share.
