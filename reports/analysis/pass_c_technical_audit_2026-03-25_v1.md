# Pass C Technical Audit Report V1

This report consolidates the current technical evidence behind the March 25 Pass C draft and responds directly to the three live review issues: measurement credibility, PatentMismatch reproducibility, and sample attrition. It is intended to be a paper-support artifact that can be shared with a supervisor, used to answer an external agent, or mined for direct manuscript revisions.

Reviewed draft:

- `paper/source/AI Washing - SK - 2026.03.25.3 - Pass C.docx`

Primary current source-of-truth artifacts:

- `reports/models/preliminary_results_readiness_v1.json`
- `reports/labels/irr_report.json`
- `reports/labels/irr_disagreement_diagnostic_v1.json`
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- `data/labels/v1/labels_master.parquet`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## 1. Executive Read

The manuscript now explains the measurement pipeline and the mismatch design much more clearly than earlier proposal versions. The remaining hard-gate problem is not conceptual confusion; it is missing audit evidence and missing reproducibility detail in the paper itself. The current repo already contains enough information to answer those issues, but the relevant numbers are spread across several artifacts and are not yet consolidated into a referee-facing object.

The measurement evidence is usable for a preliminary paper, but it is still preliminary rather than publication-grade. The adjudicated sentence set contains `551` labels, the human-human IRR subset contains `120` balanced items, and the current selected model reaches held-out accuracy `0.7062` with macro-F1 `0.6729`. Those are enough to report transparently, but they do not justify stronger publication-grade validation claims.

## 2. Stop-the-Line Issue 1: Compact Measurement Audit Object

### 2.1 Recommended appendix object

The paper should add one compact appendix measurement-audit object and one short pointer sentence in the main text. The appendix object can combine the current adjudicated-label counts, the IRR audit, and the selected classifier's held-out performance in one place.

### 2.2 Current measurement audit summary

| Audit component | Current source of truth | N | Key current numbers |
| --- | --- | ---: | --- |
| Adjudicated labeled sentence set | `data/labels/v1/labels_master.parquet` | 551 | Actionable 108; Speculative 99; Irrelevant 344 |
| Human-human IRR subset | `reports/labels/irr_report.json` and `data/labels/v1/irr_subset_master.csv` | 120 | Balanced subset: Actionable 40; Speculative 40; Irrelevant 40; Cohen's kappa = 0.6750; agreement = 0.7833 |
| Selected classifier held-out benchmark | `reports/evaluation/heldout_eval_prelim_v2.json` and `reports/evaluation/model_benchmark_matrix_prelim_v1.json` | 177 | Accuracy = 0.7062; macro-F1 = 0.6729; weighted-F1 = 0.7132 |

| Class | Support | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Actionable | 61 | 0.5952 | 0.8197 | 0.6897 |
| Speculative | 29 | 0.5333 | 0.5517 | 0.5424 |
| Irrelevant | 87 | 0.9365 | 0.6782 | 0.7867 |
| Macro average | 177 | 0.6884 | 0.6832 | 0.6729 |
| Weighted average | 177 | 0.7528 | 0.7062 | 0.7132 |

### 2.3 Main-text pointer sentence

Suggested sentence for Section 3.2:

> Appendix Table A1 reports the measurement audit underlying the disclosure-classification layer: the adjudicated sentence set contains 551 labeled observations, the human-human IRR subset contains 120 balanced items with Cohen's kappa of 0.675, and the selected preliminary classifier achieves held-out accuracy of 0.706 and macro-F1 of 0.673 on a 177-sentence benchmark.

### 2.4 Interpretation

Two points matter here. First, the current evidence is real and reportable: it shows an adjudicated label base, a true human-human IRR audit, and a held-out benchmark for the currently selected model. Second, the same evidence still supports only a preliminary measurement claim. The current held-out metrics remain below the repo's own publication-grade threshold, so the paper should avoid language that implies the sentence classifier is fully validated at publication standard.

## 3. Stop-the-Line Issue 2: Exact PatentMismatch Coding Rule

### 3.1 Current live coding rule

The current source of truth is the live construction in `src/semantic_ai_washing/analysis/delivery_table_payloads.py`.

Exact rule:

> `PatentMismatch_{i,t} = 1` if firm-year `i,t` is an AI-talking year, `A_S_{i,t}` lies in the bottom quartile of the year-`t` AI-talking distribution or `SpecShare_{i,t}` lies in the top quartile of that same distribution, and contemporaneous `log(1 + AI patents_{i,t})` is below the year-`t` industry-year mean of `log(1 + AI patents)`; otherwise `PatentMismatch_{i,t} = 0`.

This means:
- low `A_S` means bottom year-specific quartile among AI-talking firm-years
- high `SpecShare` means top year-specific quartile among AI-talking firm-years
- the low-credibility gate uses an OR rule
- the final `PatentMismatch` indicator requires all conditions simultaneously
- the patent weakness benchmark is the industry-year mean of contemporaneous `log(1 + AI patents)`, not a raw-count or median benchmark

### 3.2 Recommended manuscript sentence for Section 3.6

> We define `PatentMismatch_{i,t} = 1` when firm-year `i,t` is an AI-talking year, `A_S_{i,t}` falls in the bottom quartile of the year-`t` AI-talking distribution or `SpecShare_{i,t}` rises into the top quartile of that distribution, and contemporaneous `log(1 + AI patents_{i,t})` is below the year-`t` industry-year mean of `log(1 + AI patents)`; otherwise `PatentMismatch_{i,t} = 0`.

### 3.3 Naming recommendation

Use `A_S` in equations, tables, and code references. In prose, define it once as the actionable-to-speculative ratio. Avoid switching between `AS`, `A/S`, and verbal labels without a stable first definition. The cleanest policy is:
- equation/table symbol: `A_S`
- prose label: actionable-to-speculative ratio

## 4. Major Issue: Sample Attrition

### 4.1 What is happening

The current paper no longer has a mysterious hidden sample problem, but it does have several different sample logics that the reader should not be left to infer. The main ever-speaker panel contains `18,741` firm-year observations across `2,254` firms in the regression-ready file, and `6,152` of those observations are AI-talking firm-years. Sample sizes then change for three mechanical reasons:

1. horizon-specific timing outcomes are unavailable at the start or end of the annual panel
2. some controls, especially `R&D/assets`, are materially incomplete
3. the determinants tables collapse the panel to baseline 2016 firm characteristics rather than staying in firm-years

### 4.2 Attrition map by empirical block

| Empirical block | Observations | Main reason for shrinkage |
| --- | ---: | --- |
| Regression-ready ever-speaker panel | 18,741 | All ever-speaker firm-years, 2016-2024, with baseline control backbone. |
| AI-talking firm-years inside ever-speaker panel | 6,152 | Composition and mismatch constructs are only economically meaningful when AI disclosure is observed. |
| Table 2 / 3, t-2 horizon | 7,760 | Outcome requires lag-2 patent availability plus complete controls. |
| Table 2 / 3, t+1 horizon | 7,513 | Outcome requires lead-1 patent availability plus complete controls. |
| Table 2 / 3, t+2 horizon | 6,300 | Outcome requires lead-2 patent availability plus complete controls. |
| Table 4 / 4B timing matrices | 5,395 | Strongest drop because each regression includes patent timing terms from t-2 through t+2 simultaneously. |
| Table 6, mismatch at t+1 | 7,513 | One-horizon ever-speaker regression; PatentMismatch is coded as zero outside AI-talking years rather than inducing a talk-only sample. |
| Table 6B, mismatch at t+2 | 6,300 | Longer-horizon counterpart; later years drop out mechanically. |
| Table 7 full multivariate | 922 | 2016 baseline firm cross-section plus missingness in R&D/assets and employees. |
| Table 7C reduced multivariate | 1,790 | Reduced baseline set recovers most of the firm sample by omitting sparse R&D/assets and employees. |

### 4.3 Current nonmissing counts that drive the shrinkage

- Patent-timing availability:
  - `t-2`: `15,029`
  - `t-1`: `16,934`
  - `t`: `18,741`
  - `t+1`: `16,623`
  - `t+2`: `14,388`
- Key control availability in the regression-ready ever-speaker panel:
  - `ln_assets`: `18,741`
  - `leverage`: `18,682`
  - `cash`: `18,740`
  - `rd_intensity`: `10,926`
  - `capx_at`: `18,664`
  - `roa`: `18,717`
  - `sales_growth`: `15,785`
  - `emp`: `17,964`
- Baseline 2016 determinants sample:
  - baseline firms: `1,807`
  - 2016 `rd_intensity` available for `1,006` firms
  - 2016 `emp` available for `1,679` firms

### 4.4 Suggested manuscript sentence

> Sample sizes vary across empirical blocks for mechanical reasons tied to the panel design and the required covariate set. The main ever-speaker panel contains 18,741 firm-year observations, but timing regressions lose observations at the beginning and end of the sample when lagged or lead AI patent outcomes are unavailable, and all regressions additionally use complete cases on the baseline controls. The distributed-lag timing matrices impose the strongest requirement because they include patent outcomes from `t-2` through `t+2` simultaneously, while the determinants tables use a different design that collapses the panel to 2016 baseline firm characteristics, making missing `R&D/assets` and employment the main source of cross-sectional attrition.

## 5. Additional Technical Notes Worth Flagging

1. The current measurement evidence is preliminary rather than publication-grade.
   - Current held-out accuracy is `0.7062` and macro-F1 is `0.6729`.
   - Current overall IRR kappa is `0.6750`.
   - Those are reportable, but the manuscript should not claim fully validated publication-grade measurement.
2. The draft should explicitly point to the measurement-audit appendix object.
   - Right now the methodology section explains the gates well but still makes the reader trust the audit more than inspect it.
3. The mismatch rule is ready to state exactly now.
   - This is a writing fix, not a modeling blocker.
4. The determinants tables should distinguish substantive variation from missing-data variation.
   - The fuller determinants variants remain useful because the negative `R&D/assets` slope is informative.
   - The reduced variants remain useful because they protect against over-interpreting a heavily reduced complete-case sample.

## 6. Recommended Next Manuscript Edits

1. Add a compact appendix measurement-audit table and point to it once in Section 3.2.
2. Replace the current verbal description in Section 3.6 with the exact `PatentMismatch` rule above.
3. Add one explicit sample-attrition paragraph in the data/results section.
4. Keep the fuller determinants appendix tables in the package because the `R&D/assets` result is substantively informative even if it is not the cleanest main-text multivariate object.

## 7. Current Best Supporting Files

- Main paper draft:
  - `paper/source/AI Washing - SK - 2026.03.25.3 - Pass C.docx`
- Current preliminary draft build:
  - `output/doc/ai_washing_preliminary_draft.docx`
- Measurement audit sources:
  - `reports/models/preliminary_results_readiness_v1.json`
  - `reports/labels/irr_report.json`
  - `reports/labels/irr_disagreement_diagnostic_v1.json`
  - `reports/evaluation/heldout_eval_prelim_v2.json`
  - `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- Mismatch construct note:
  - `reports/analysis/patent_mismatch_construct_v1.md`

This report is the current paper-support audit for the March 25 Pass C draft.
