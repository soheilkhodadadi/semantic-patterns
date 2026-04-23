# AI-Washing v3.1 Publication Upgrade Roadmap

Date: 2026-04-22  
Status: Active execution roadmap  
Supersedes for market-identification work: `paper/guides/AI_Washing_Codex_Master_Run_Sheet_v1.md` only in the sense of sequencing the next wave. Historical test IDs and outputs remain valid and should not be deleted.

## 1. Purpose

This roadmap turns the current diagnosis into a stable execution plan for the next paper revision.

The goal of `v3.1` is not to immediately rewrite the paper. The goal is to strengthen the market-results block until we know whether the paper can support a stronger pricing interpretation or should instead lean more heavily on measurement + validation + suggestive market consequences.

The roadmap therefore has four jobs:

1. stabilize the working lane so scripts, outputs, and paper assets are easier to track;
2. run the highest-value Tier 1 tests that directly address endogeneity and benchmark-misspecification concerns;
3. decide whether the market-results block survives strongly enough to justify Tier 2 identification upgrades;
4. only after that, update the manuscript narrative and claims.

## 2. Current Bottom Line

### What the paper already supports well

- a scalable, audited measure of low-credibility AI disclosure in annual 10-K filings;
- a rapid rise in `PatentMismatch`, especially after 2022;
- limited immediate filing-date differentiation at the 10-K event;
- later return and valuation patterns that are suggestive of delayed incorporation, especially outside the largest firms;
- strong construct validation because the disclosure composition predicts weaker later AI patent realization.

### What the paper does not yet support in strong form

- a clean claim that markets underreact to AI-washing;
- a clean claim that later abnormal returns are causal correction of AI-washing mispricing;
- a clean claim that the post-filing spread is not simply absorbed by firm characteristics, industry cycles, or the patent-capability component itself.

### Working claim posture for `v3.1`

Until the new tests are run, use this interpretation discipline:

- `PatentMismatch` is a validated disclosure-credibility measure.
- The market-response results are currently suggestive, not dispositive.
- The paper should say returns are `consistent with delayed incorporation` rather than claiming `market inefficiency` or `market correction` in a hard causal sense.

## 3. Phase 0: Workflow Stabilization Before New Tests

### Objective

Create one canonical `v3.1` lane so we stop mixing older and newer runs in memory.

### Keep unchanged

- existing historical run outputs in `paper/generated/`;
- existing heavy artifacts in `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/`;
- current manuscript source in `paper/full paper/ai_washing_v3.0/`.

### New canonical working lanes

Repo-light lane:

- roadmap and project maps: `paper/guides/`
- paper-facing generated exports for the new wave: `paper/generated/v3_1/`
- code and drivers: `src/semantic_ai_washing/analysis/`
- one-driver-per-paper-test scripts: `src/semantic_ai_washing/analysis/publication_runs/`

Heavy DataWork lane:

- canonical `v3.1` runtime root: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/`
- run registry and manifests: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/run_registry/`
- heavy run outputs: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/test_runs/`
- downloaded factor inputs: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/factor_inputs/`
- audit summaries and diagnostics: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/audit/`
- mirrored paper assets if needed: `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/paper_assets/`

### Naming contract for all new runs

Use:

- `test_id`: stable logical test family
- `run_id`: `YYYYMMDD_aiw_v3_1_<test_id>_<spec_id>_v1`

Example:

- `20260422_aiw_v3_1_test_09_factor_alpha_ff5_umd_v1`

### Output contract for every new empirical run

Each new test should emit, at minimum:

1. `dataset_summary.json`
2. `main_table.csv`
3. `main_table.tex`
4. `main_table.docx`
5. `result_notes.md`
6. `writer_packet.json`
7. `run_manifest.json`

If the test is figure-centric, add:

- `main_figure.png`
- `main_figure_series.csv`

### Phase-0 coding tasks

1. create the `v3.1` output roots above;
2. add a project-map guide so the canonical paths are explicit;
3. when we start coding, point all new `v3.1` drivers to the new DataWork test root rather than the older shared `derived/test_runs/` lane.

## 4. Canonical Inputs for the `v3.1` Lane

Unless a later refresh changes them, treat these as the current canonical datasets:

### Annual disclosure / patent panel

- `data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet`

### Filing-event estimation sample

- `data/processed/panel/filing_event_estimation_sample_hybrid_api_a_conf49_v1.parquet`

### Filing-event daily returns

- `data/interim/market/filing_event_returns_daily_hybrid_api_a_conf49_v1.parquet`

### Monthly CRSP returns / index

- `data/interim/market/wrds_crsp_msf_full_sample_v1.parquet`
- `data/interim/market/wrds_crsp_msi_full_sample_v1.parquet`

### Annual market features

- `data/interim/market/annual_market_features_ever_speaker_2016_2025_hybrid_api_a_conf49_v1.csv`

### Backbone-building scripts already available

- `src/semantic_ai_washing/analysis/build_refresh_ever_speaker_panel.py`
- `src/semantic_ai_washing/analysis/build_full_sample_wrds_backbone.py`
- `src/semantic_ai_washing/analysis/build_filing_event_spine.py`
- `src/semantic_ai_washing/analysis/build_event_return_windows.py`
- `src/semantic_ai_washing/analysis/run_filing_event_regressions.py`

## 5. Tier 1: Highest-Value Market-Identification Package

These are the first tests to run. They are ranked by payoff, not by glamour.

### Test 09. Richer factor-adjusted portfolio alpha

#### Question
Does the existing post-filing long-short spread survive once we move beyond a market-only benchmark?

#### Why this is first
This is the fastest direct answer to the strongest referee criticism of current Table 3.

#### Required data

- monthly portfolio return series already built from the filing-event sample;
- factor files from the Ken French Data Library;
- if available later, momentum and any higher-order benchmark expansions.

#### Planned specifications

- CAPM
- FF3
- FF5
- FF5 + UMD
- equal-weight and value-weight
- full sample and non-big refinement if the baseline is diffuse

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_09_factor_adjusted_alpha.py`

#### Decision rule

- If alpha survives FF5 + UMD, the market block gets materially stronger.
- If alpha survives only in equal-weight / non-big space, keep the claim narrower and tie it to hard-to-value firms.
- If alpha dies once factors are added, the market block becomes supporting evidence rather than a headline causal claim.

### Test 10. Industry-adjusted and characteristic-adjusted post-filing returns

#### Question
Is the post-filing spread still visible after absorbing industry AI cycles and obvious stock characteristics?

#### Required data

- filing-event sample;
- monthly returns;
- annual controls already in the panel;
- industry mapping;
- factor or benchmark inputs if needed.

#### Planned variants

- industry-adjusted return version;
- industry-by-time residualized return version;
- characteristic-adjusted version if we can build a clean benchmark set.

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_10_adjusted_post_filing_returns.py`

#### Decision rule

- If the signal survives industry adjustment, it is less likely to be an industry AI cycle artifact.
- If it survives characteristic adjustment, it is much harder to dismiss as a generic small-growth-speculative-firm effect.

### Test 11. Horse-race decomposition of `PatentMismatch`

#### Question
Is the return pattern coming from low-credibility disclosure, from weak patent capability, or from the interaction of the two?

#### Why this is critical
This is the highest-value identification test that the current draft does not yet frontally answer.

#### Required variables

- disclosure-side credibility component;
- patent-side weakness component;
- combined `PatentMismatch` state;
- core controls.

#### Planned specifications

- disclosure component alone;
- patent weakness component alone;
- both together;
- interaction / combined state;
- outcome versions for filing-date CAR and post-filing return horizons.

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_11_mismatch_component_horse_race.py`

#### Decision rule

- If only the patent-weakness component matters, then the AI-washing interpretation has to be softened.
- If the interaction or combined state matters most, that strongly supports the paper’s theory.

### Test 12. Controlled predictive return regressions

#### Question
Is post-filing return predictability subsumed by standard observables?

#### Target control family

- size
- book-to-market or closest feasible valuation proxy
- momentum / prior returns
- beta if feasible
- profitability
- investment
- turnover / illiquidity if feasible
- R&D/assets
- prior patents / prior AI patents

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_12_predictive_return_controls.py`

#### Notes

This is the closest step toward the “not subsumed by observables” standard used in stronger mispricing papers.

#### Decision rule

- If `PatentMismatch` survives the fuller control set, the market-results block becomes substantially more persuasive.
- If it does not, the paper should reposition toward real-outcomes validation and away from a stronger mispricing claim.

### Test 13. Event-time diagnostic path around the filing

#### Question
Is the later spread a post-filing pattern, or does it already exist before the filing?

#### Planned output

- pre/post event-time chart centered at the filing date;
- table of cumulative windows before and after the filing;
- split by mismatch status;
- optionally split by non-big.

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_13_pre_post_event_path.py`

#### Decision rule

- If the pattern is visibly pre-existing, we should stop describing it as delayed correction.
- If the pattern opens meaningfully after the filing, the market block gains credibility.

## 6. Tier 2: Identification Upgrades, Conditional on Tier 1

Run Tier 2 only after the Tier 1 package has been reviewed.

### Test 14. First-mismatch / within-firm onset design

#### Question
What happens when a firm first transitions into a mismatch state?

#### Motivation
This is the cleanest bridge toward a within-firm interpretation.

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_14_first_mismatch_onset.py`

#### Outcomes to prioritize

- filing-date CAR around the onset-year filing;
- post-filing return windows;
- forward valuation changes rather than contemporaneous levels where feasible.

### Test 15. Matched AI-talking comparison sample

#### Question
Among similar AI-talking firms, do mismatch firms still behave differently?

#### Matching dimensions

- year
- industry
- size
- valuation proxy
- profitability
- investment
- prior patents / AI patent history
- prior returns

#### Proposed driver

- `src/semantic_ai_washing/analysis/publication_runs/test_15_matched_ai_talking_sample.py`

#### Warning
Matching helps, but it is not a full causal solution. Use it as a strengthening layer, not as a magic bullet.

## 7. Tier 3: Mechanism and Triangulation, If Needed

These are useful after Tier 1 and Tier 2 determine what survives.

### Candidates

- non-big / information-friction refinements as reusable overlays;
- analyst-coverage or institutional-ownership discernment tests if data are available;
- financing / issuance incentives beyond the current Table 8 setup;
- incentive and governance heterogeneity in the spirit of related AI-disclosure papers.

### Rule

Do not run Tier 3 just because it sounds rich. Run it only if it sharpens the final story that survives Tier 1.

## 8. Writing Sequence After Evidence, Not Before

### Writing changes that should wait

Do not fully rewrite the abstract, introduction, results, and conclusion until Tier 1 has been evaluated.

### Writing changes that can be prepared early

Prepare a note of planned rhetorical changes:

- move construct validation earlier in the results flow;
- demote hard underreaction language unless stronger evidence survives;
- present market results as suggestive and then show the stricter tests;
- let the strongest surviving evidence determine the final paper’s headline.

### Safe provisional language

Use phrases such as:

- `consistent with delayed incorporation`
- `suggestive market consequences`
- `not cleanly distinguished at the filing date`

Avoid phrases such as:

- `the market underreacts`
- `the market corrects AI-washing`
- `causal evidence of market inefficiency`

## 9. Execution Order

### Batch 0: workflow stabilization

1. finalize this roadmap and project map;
2. point the next tests to the `v3.1` runtime roots;
3. download or stage factor inputs.

### Batch 1: must-run Tier 1 core

1. Test 09: factor-adjusted alpha
2. Test 11: mismatch-component horse race
3. Test 12: controlled predictive return regressions
4. Test 13: pre/post event path

### Batch 2: adjustment layer

5. Test 10: industry-adjusted / characteristic-adjusted return versions
6. review the combined market-evidence package

### Batch 3: identification upgrade if warranted

7. Test 14: first-mismatch onset
8. Test 15: matched AI-talking design

### Batch 4: writing and paper restructuring

9. rewrite abstract / introduction / results / conclusion
10. update result ordering and appendix map
11. create the next paper package

## 10. Definition of Done for `v3.1` Tier 1

Tier 1 is complete only when:

- all new tests have stable drivers;
- each test emits the full output contract;
- the `v3.1` lane has a clear registry of runs and surviving assets;
- we have a written verdict on whether the market block supports:
  - strong pricing language,
  - narrow suggestive language, or
  - appendix-only status.

## 11. Immediate Next Step

The next operational task after this roadmap is:

1. create the `v3.1` run scaffolds;
2. fetch and stage factor data for Test 09;
3. implement Test 09 first, because it gives the quickest read on whether the existing market block survives stronger benchmarking.
