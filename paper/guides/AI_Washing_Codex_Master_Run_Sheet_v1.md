
# AI-Washing v2: Codex-Ready Master Run Sheet
## Version date: 2026-04-11
## Purpose
This run sheet translates the current paper status, Kuntara’s feedback, and the top-tier hard gates in Rubric 2.0 into a **ranked set of concrete empirical runs** for the next revision. The goal is not to run everything. The goal is to run the **smallest set of high-payoff tests** that can move the paper from a credible predictive/measurement draft to a stronger finance paper with:
1. a sharper headline fact,
2. quantified market/economic stakes,
3. a more convincing event/identification angle,
4. stronger return and real-effects evidence, and
5. enough validation reruns to keep the original disclosure–patent backbone intact.

---

# Part I. Ground rules for Codex execution

## A. Canonical unit of observation
Use **firm-year** as the default unit of analysis for the disclosure/patent panel and **firm-filing event** or **firm-month** as the default unit for market-response and post-filing drift blocks.

## B. Canonical sample
- Public U.S. firms with annual 10-K filings.
- Preferred expanded window: **2016–2025** for disclosure-based analysis.
- Patent outcomes can use the longer patent history already available (e.g., 2014–2025) where needed for leads/lags and pre-period capability definitions.
- Keep a clean note of:
  - base ever-speaker panel size,
  - AI-talking subsample size,
  - event-study usable sample size,
  - monthly-return usable sample size,
  - firm-level cross-section size.

## C. Canonical disclosure variables
Use these exact definitions consistently across all new runs:
- **AI Focus** = log(1 + total AI-related sentences)
- **Actionable disclosure** = indicator for at least one actionable AI sentence
- **Speculative-only disclosure** = indicator for at least one speculative AI sentence and zero actionable AI sentences
- **AS ratio** = actionable-to-speculative ratio defined in the paper
- **SpecShare** = speculative share among actionable + speculative AI sentences
- **PatentMismatch** = low-credibility disclosure combined with weak contemporaneous patenting, using the exact year-t rule already fixed in the paper

## D. Canonical control set
Unless a test is explicitly a pure event-window summary, use the baseline firm controls:
- log assets
- leverage
- cash/assets
- R&D/assets
- CAPX/assets
- ROA
- sales growth
- employees

Where R&D/assets and employees create severe sample loss, report a reduced-baseline variant and note the attrition.

## E. Canonical inference defaults
- Firm-clustered standard errors for panel regressions
- Industry or industry×year FE where appropriate
- Firm and year FE for within-firm annual panel models
- For return panels with monthly data: firm and year-month FE if feasible; otherwise firm FE + calendar-time FE
- For event-study summaries: report both raw means and regression-adjusted versions

## F. Output discipline
Every run should produce four objects:
1. **analysis dataset summary** (sample size, date range, missingness)
2. **main output table/figure**
3. **one paragraph of result notes** (plain English, no hype)
4. **writer-capture sheet** with the exact metadata needed for methods/captions

For **table-centric empirical tests** (especially Tests 2–8), the main output
should default to a **journal-style table first**, not a figure first.

Minimum export set for table-centric tests:
- audit table in `.csv`
- LaTeX-ready table in `.tex`
- journal-style Word table in `.docx`
- result notes
- writer packet

Figures are still useful, but they should play a supporting role unless they add
timing or shape information that is not visible in the table itself.

The writer-capture sheet must always include:
- sample definition
- event window / horizon definition
- dependent variable definition
- key regressors definition
- fixed effects
- clustering
- winsorization or trimming
- whether variables are standardized or logged
- exact N
- key coefficient(s) / alpha(s)
- one economic magnitude sentence

---

# Part II. The eight highest-priority new tests

## Test 1. Headline stylized fact: mismatch surge through 2025
### Why this is first
This is the best current “put-down-your-coffee” fact. The current draft already shows mismatch share reaching roughly 44% in 2024. Update it through 2025 and make this the front-end descriptive anchor.

### Data inputs
- annual ever-speaker disclosure panel, 2016–2025
- AI-talking-year flag
- PatentMismatch
- industry code (at least SIC2 or Fama–French 12/17/49 industry mapping)

### Exact variables
- `mismatch_count_y` = count of firm-years with PatentMismatch == 1 in year y
- `mismatch_share_ai_talk_y` = count(PatentMismatch==1 & AI_talking==1) / count(AI_talking==1)
- sector counts and sector shares among AI-talking firm-years

### Baseline sample
- Main figure: all AI-talking firm-years in ever-speaker panel, 2016–2025
- Sector panel: same sample

### Required outputs
**Figure 1 (main text)**
- Panel A: annual count of mismatch firm-years and mismatch share among AI-talking firm-years
- Panel B: top six sectors by mismatch incidents, with mismatch share annotated on the bar

### What would count as exciting
- mismatch share remains very high or rises further in 2025
- surge is concentrated in economically salient sectors or in firms with weak pre-period capability

### Writer-capture sheet
- exact yearly counts
- exact 2024 and 2025 mismatch shares
- sector ranking and corresponding shares
- note whether AI-talking denominator changed materially after adding 2025

### Caption skeleton
“This figure uses the ever-speaker annual panel and restricts the denominator to AI-talking firm-years where appropriate. Panel A plots the annual count of PatentMismatch firm-years and the share of AI-talking firm-years flagged as mismatch. Panel B plots the six sectors with the highest number of mismatch incidents and annotates each bar with the mismatch share within that sector.”

### Codex instruction block
Run the yearly mismatch-incidence figure on the 2016–2025 ever-speaker panel. Use PatentMismatch exactly as defined in the paper. Output one figure with Panel A (annual count + annual mismatch share among AI-talking firm-years) and Panel B (top six sectors by mismatch count with sector mismatch shares annotated). Also output a CSV with year, mismatch_count, ai_talking_count, mismatch_share, and sector summaries.

---

## Test 2. Filing-date market reaction around 10-K release
### Why this matters
Kuntara asked directly whether the market rewards AI washers. This is the first finance-stakes block.

### Data inputs
- filing acceptance date or 10-K filing date
- CRSP daily returns
- CRSP market return or a market-model benchmark
- annual disclosure measures (`PatentMismatch`, `AS ratio`, `AI Focus`, `ActionableDisclosure`, `SpeculativeOnly`)
- baseline controls from prior fiscal year

### Event date
- event date = 10-K filing date
- if exact filing timestamp is unavailable, use the CRSP trading day corresponding to the SEC acceptance date

### Event windows
Run all of these:
- CAR[-1,+1]
- CAR[-2,+2]
- CAR[-5,+5]

### Abnormal-return baseline
**Main baseline**
- market-adjusted CAR using CRSP value-weighted market return or a market model estimated over [-250,-30]

**Robustness**
- if Fama–French factors are locally available, add FF3 or FF5 abnormal returns

### Main specifications
#### Table 1A: mean CARs by mismatch status
- AI-talking, mismatch vs non-mismatch
- report difference in means

#### Table 1B: regression
\[
CAR_{i,[a,b]} = \alpha + \beta_1 PatentMismatch_{i,t} + \beta_2 AS_{i,t} + \beta_3 AIFocus_{i,t} + X'_{i,t-1}\theta + \text{Industry FE} + \text{Filing-year FE} + \varepsilon_{i,t}
\]

### Required outputs
- one table with mean CARs and regression columns
- the table must be exported in `.csv`, `.tex`, and journal-style `.docx`
- one event-time plot around filing date only if it adds information beyond the table

### What would count as exciting
- mismatch firms get significantly positive filing-date CARs
- or there is no immediate reaction, setting up a lazy-prices style drift story

### Writer-capture sheet
- event date definition
- abnormal return model
- event windows
- sample size by window
- whether daily returns are winsorized
- coefficient on PatentMismatch and economic magnitude

### Caption skeleton
“This table reports filing-date cumulative abnormal returns around annual 10-K releases. Event windows are [−1,+1], [−2,+2], and [−5,+5] trading days relative to the filing date. The main regressors are PatentMismatch, the AS ratio, and AI Focus. Controls are lagged firm characteristics. Standard errors are clustered at the firm level.”

### Codex instruction block
Build a filing-event dataset using annual 10-K filing dates and CRSP daily returns. Compute CAR[-1,+1], CAR[-2,+2], and CAR[-5,+5] using market-adjusted returns as the main baseline and a market-model robustness if feasible. Estimate both difference-in-means and regression specifications with PatentMismatch, AS ratio, AI Focus, and lagged firm controls. Output one clean table in `.csv`, `.tex`, and journal-style `.docx`. Add an event-time figure only if it adds useful timing information beyond the table.

---

## Test 3. Post-filing drift and medium-horizon return correction
### Why this matters
This is where the paper can become more finance-like: short-run reward or inattention followed by reversal/correction.

### Data inputs
- same filing-event data as Test 2
- CRSP daily or monthly returns
- disclosure measures

### Return horizons
Use these holding windows after the filing date:
- BHAR / cumulative abnormal return from day +2 to +21
- +2 to +63
- +2 to +126
- +2 to +252

If monthly returns are easier:
- month +1
- months +2 to +6
- months +2 to +12

### Main specifications
#### Table 2A: mean drift by mismatch status
#### Table 2B: regression
\[
PostReturn_{i,h} = \alpha + \beta_1 PatentMismatch_{i,t} + \beta_2 AS_{i,t} + \beta_3 AIFocus_{i,t} + X'_{i,t-1}\theta + \text{Industry FE} + \text{Filing-year FE} + \varepsilon_{i,h}
\]

### Optional stronger version
Long–short portfolio:
- long non-mismatch AI talkers
- short mismatch AI talkers
- equal-weight and value-weight
- hold for 1, 3, 6, 12 months

### What would count as exciting
- mismatch firms underperform in the months after the filing
- especially if the filing-date reaction was neutral or positive

### Writer-capture sheet
- return horizon definitions
- benchmark model
- equal-weight vs value-weight
- alpha model if estimated
- annualized spread magnitude

### Caption skeleton
“This table reports post-filing abnormal return windows following annual 10-K releases. The dependent variable is the buy-and-hold abnormal return or cumulative abnormal return over the specified post-filing horizon. The main regressors are PatentMismatch, the AS ratio, and AI Focus.”

### Codex instruction block
Using the filing-event dataset, compute post-filing abnormal returns over +2 to +21, +2 to +63, +2 to +126, and +2 to +252 trading days. Estimate regressions of post-filing abnormal returns on PatentMismatch, AS ratio, AI Focus, and lagged controls with industry and filing-year fixed effects. Also produce optional long–short portfolio spreads (non-mismatch minus mismatch among AI-talking firms) with equal- and value-weight returns.

---

## Test 4. Portfolio sorts and long–short alpha
### Why this matters
This is the clearest bridge to the AIness paper: it creates a familiar finance output and a seminar-ready number.

### Data inputs
- monthly CRSP returns
- market cap
- filing-based annual measure carried forward for up to 12 months
- `PatentMismatch`, `AS ratio`, or an ordinal disclosure-credibility score

### Main sort designs
Run all three:
1. terciles on `AS ratio`
2. terciles on `PatentMismatch` / mismatch probability score
3. double-sort on size × mismatch

### Holding periods
- rebalance monthly
- hold 1 month and 3 months as main
- optional 6 and 12 months

### Return models
- raw return
- excess return
- alpha against available factor model (if local factors exist)
- if not, use market-adjusted return and report raw spreads

### Main outputs
- one portfolio table with Q1/Q2/Q3 returns and Q3–Q1 or low–high spreads
- one size-split table or panel

### What would count as exciting
- a significant long–short spread among non-big firms
- stronger spread on the short leg (mismatch side)

### Writer-capture sheet
- sort variable
- breakpoint definition
- rebalance timing
- weighting scheme
- holding period
- annualized spread / alpha

### Caption skeleton
“This table reports monthly portfolio returns sorted on the disclosure-credibility measure. Portfolios are rebalanced monthly using the most recent annual filing-based signal. The table reports raw returns, excess returns, and factor-adjusted alphas where available.”

### Codex instruction block
Construct monthly portfolios sorted on AS ratio and on PatentMismatch-related credibility scores. Rebalance monthly using the latest available annual filing signal. Report equal-weight and value-weight returns, annualized spreads, and factor-adjusted alpha if local factors are available. Include a double-sort by size (NYSE median split or CRSP median split).

---

## Test 5. Small-firm / hard-to-value heterogeneity
### Why this matters
The AIness paper’s strongest cross-sectional result is concentration among non-big stocks. This is likely feasible with your current data and highly relevant for a finance audience.

### Data inputs
- monthly CRSP market cap
- disclosure measures
- returns from Tests 2 and 3
- optional turnover or illiquidity proxy if easy to compute from CRSP

### Main splits
Minimum:
- small vs big using NYSE 50th percentile breakpoint

If feasible:
- illiquid vs liquid using turnover or Amihud
- low vs high analyst-like attention proxy using size/turnover (if no IBES)

### Specifications
Run filing-date CAR and post-filing drift separately by size group, and/or interact mismatch with small-firm indicator:
\[
Y_{i} = \alpha + \beta_1 PatentMismatch_{i,t} + \beta_2 Small_{i,t} + \beta_3 PatentMismatch_{i,t}\times Small_{i,t} + X'_{i,t-1}\theta + FE + \varepsilon_i
\]

### Main outputs
- one heterogeneity table
- optional side-by-side figure for small vs big

### What would count as exciting
- any market mispricing effect is strongly concentrated among small firms
- the large-firm sample is flat or much weaker

### Writer-capture sheet
- size breakpoint method
- sample split Ns
- interaction coefficient
- economic difference across groups

### Caption skeleton
“This table reports heterogeneity by firm size. Small firms are defined as those below the NYSE 50th percentile breakpoint. The table tests whether the market-response and post-filing-drift patterns associated with AI-washing are concentrated in harder-to-value firms.”

### Codex instruction block
Create a small-vs-big split using the NYSE 50th percentile market-cap breakpoint. Re-estimate the filing-date CAR and post-filing drift regressions separately by size group and with PatentMismatch × Small interaction terms. Output one clean heterogeneity table and a compact comparison figure.

---

## Test 6. Real effects beyond patents
### Why this matters
This is the best way to connect the market tests to fundamentals. Lazy Prices uses future operating income, net income, sales, news, and bankruptcies; the AIness paper uses future sales growth and ROE.

### Data inputs
- Compustat annual data
- annual disclosure measures
- annual patent measures
- patent quality if available (citations / value proxies)

### Outcomes to run
At minimum:
- future ROA
- future sales growth
- future CAPX/assets
- future R&D/assets (if coverage is usable)

If available:
- future AI patent citations
- future patent value proxy

### Horizons
- \(t+1\)
- \(t+2\)

### Main specification
\[
Y_{i,t+h} = \alpha + \beta_1 PatentMismatch_{i,t} + \beta_2 AS_{i,t} + \beta_3 AIFocus_{i,t} + X'_{i,t}\theta + \gamma_i + \gamma_t + \varepsilon_{i,t+h}
\]

### Main outputs
- one table with multiple outcomes in panels or columns
- optional figure if one variable is especially strong

### What would count as exciting
- mismatch predicts weaker future ROA / sales growth / innovation quality even after controls and FE
- AS ratio predicts stronger future real outcomes

### Writer-capture sheet
- outcome definition
- horizon
- winsorization
- FE and clustering
- magnitude relative to mean outcome

### Caption skeleton
“This table reports future real and innovation outcomes as a function of disclosure credibility. The dependent variables are future profitability, growth, investment, and innovation-quality measures. The key regressors are PatentMismatch, the AS ratio, and AI Focus.”

### Codex instruction block
Run annual panel regressions of future ROA, sales growth, CAPX/assets, R&D/assets, and any available patent-quality proxy on PatentMismatch, AS ratio, AI Focus, and baseline controls with firm and year fixed effects. Use horizons \(t+1\) and \(t+2\). Output one multi-panel table and a writer-capture sheet.

### Follow-up refinement note
If the first-pass real-effects table is weak or diffuse, rerun a tighter finance specification rather than forcing it into the main story. Prioritize:
- profitability-centered outcomes first (`ROA`, operating income/assets, net income/assets if available)
- cleaner investment outcomes before sparse innovation ones
- scaled changes or indicator outcomes where ratio denominators create instability
- optional post-ChatGPT interaction or post-2023 subsample if the average panel washes out a recent effect

The goal is not to make every column significant. The goal is to see whether mismatch predicts a cleaner future profitability or financing margin under a more disciplined specification.

---

## Test 7. ChatGPT shock / event path
### Why this matters
This is the cleanest currently available identification path, and Kuntara explicitly suggested it.

### Event definition
- `PostChatGPT_t = 1` for filings accepted on or after 2023-01-01
- pre period = filings through 2022
- use event-study leads/lags if possible

### Treatment definitions
Run all three, but rank them:
#### Main treatment (T1)
`LowCapability_i = 1` if firm had zero AI patents in the pre-ChatGPT window (2018–2022) and low pre-period AS ratio or no actionable disclosure.

#### Alternative treatment (T2)
`HighSpecPre_i = 1` if pre-2023 SpecShare is above industry median.

#### Alternative treatment (T3)
`Small_i = 1` if below NYSE median size, as a simple harder-to-value / easier-to-hype group.

### Outcomes
- AI Focus
- AS ratio
- PatentMismatch
- filing-date CAR
- post-filing drift

### Main specifications
#### DID
\[
Y_{i,t} = \alpha_i + \lambda_t + \beta (PostChatGPT_t \times Treated_i) + X'_{i,t-1}\theta + \varepsilon_{i,t}
\]

#### Event-study
\[
Y_{i,t} = \alpha_i + \lambda_t + \sum_{k\neq -1}\beta_k \mathbf{1}\{event\_time=k\}\times Treated_i + X'_{i,t-1}\theta + \varepsilon_{i,t}
\]

### Main outputs
- one DID table
- one pre-trend / event-study figure

### What would count as exciting
- low-capability firms increase AI talk and/or mismatch post-ChatGPT without similar implementation gains
- market rewards those firms at filing but later corrects

### Writer-capture sheet
- exact event date rule
- treatment definition(s)
- omitted event-time bin
- pre-trend test result
- interpretation of interaction coefficient

### Caption skeleton
“This table reports difference-in-differences estimates around the release of ChatGPT. Treated firms are defined using pre-period AI capability or rhetorical-tilt measures. The table tests whether the post-ChatGPT period increased AI disclosure, mismatch, and related market outcomes disproportionately in firms with weaker pre-period capability.”

### Codex instruction block
Build a ChatGPT post indicator using filings from 2023 onward. Define the main treated group as firms with zero pre-2023 AI patents and weak pre-2023 disclosure credibility. Estimate DID and event-study regressions for AI Focus, AS ratio, PatentMismatch, filing-date CAR, and post-filing drift. Output one DID table and one event-study figure with pre-trends.

---

## Test 8. Financing and valuation consequences
### Why this matters
This is the most feasible current substitute for richer analyst/institutional data and directly answers the “how much does it matter?” question.

### Data inputs
- Compustat annual financing variables
- CRSP market cap / valuation
- disclosure measures

### Outcomes
Run at least these:
- future net equity issuance / change in shares outstanding
- future external financing indicator or net financing amount
- market-to-book / Tobin’s Q
- future valuation multiple change

If you have only Compustat basics:
- change in common shares outstanding
- sale of common and preferred stock / total assets
- net equity issuance proxy
- market-to-book

### Main specifications
\[
FinancingOrValue_{i,t+h} = \alpha + \beta_1 PatentMismatch_{i,t} + \beta_2 AS_{i,t} + \beta_3 AIFocus_{i,t} + X'_{i,t}\theta + \gamma_i + \gamma_t + \varepsilon_{i,t+h}
\]

Run for:
- \(h = 0\) contemporaneous valuation
- \(h = +1\) future issuance / financing

### Main outputs
- one table with financing outcomes
- one table or panel with valuation outcomes

### What would count as exciting
- mismatch firms have higher valuation multiples or raise more equity than their later patent output warrants
- or the effect is concentrated post-ChatGPT

### Writer-capture sheet
- financing variable definitions
- timing (same year vs next year)
- FE and clustering
- economic magnitude in percentage-point or standard-deviation terms

### Caption skeleton
“This table reports financing and valuation consequences associated with disclosure credibility. The dependent variables are annual measures of valuation and external financing. The key regressors are PatentMismatch, the AS ratio, and AI Focus.”

### Codex instruction block
Using Compustat and CRSP annual variables, estimate valuation and financing regressions on PatentMismatch, AS ratio, and AI Focus. Use market-to-book (or Tobin’s Q) as the valuation outcome and one or more equity-issuance / financing proxies as the financing outcomes. Include firm and year fixed effects where feasible, or industry and year fixed effects if the outcome is too sparse in panel form. Output one valuation table and one financing table.

### Follow-up refinement note
If the first-pass valuation/financing table is weak, rerun a non-big-firm refinement before freezing it. The closest guide from the AI Narrative and Stock Mispricing paper is a split below versus above the NYSE 50th percentile market-value breakpoint, with the economically interesting patterns concentrated among non-big firms. If local NYSE breakpoints are unavailable, use the matched-sample yearly median market cap as the fallback screen and label it clearly as a non-big refinement rather than a literal NYSE breakpoint replication.

Where economically relevant, also run a `PatentMismatch × PostChatGPT` interaction version on the non-big sample. With firm and year fixed effects, the standalone post dummy is absorbed, so the useful refinement is the interaction term. Treat this as a cross-cutting follow-up spec for valuation and other mispricing-style tests rather than a one-off exception for Test 8.

---

# Part III. Required validation reruns from the current paper
These are not the new “headline” tests, but they must be rerun on the expanded 2016–2025 panel so the paper’s validation backbone stays current.

## Legacy core reruns (main text candidates)
1. **Figure R1** — AI disclosure volume and composition over time (update through 2025)
2. **Figure R2** — AI patent coverage over time (update through 2025)
3. **Table R1** — summary statistics on the expanded main panel
4. **Table R2** — AI Focus and AI patent timing
5. **Table R3** — disclosure composition and AI patent timing
6. **Table R4** — actionable disclosure timing matrix
7. **Table R5** — speculative-only disclosure timing matrix
8. **Table R6** — AS ratio × PatentMismatch at \(t+1\)
9. **Table R7** — AS ratio × PatentMismatch at \(t+2\)
10. **Figure R3** — AS-ratio quantile mismatch alignment plot
11. **Figure R4** — mismatch incidence over time and by industry
12. **Table R8** — reduced-baseline determinants

## Legacy appendix reruns
13. **Table A1** — full multivariate determinants
14. **Table A2** — mismatch-share intensity determinants
15. **Table B1** — updated measurement audit table (replace old accuracy with the new ~85% accuracy / updated kappa)
16. **Table B2** — updated attrition map on the expanded 2016–2025 panel

## Required robustness companion to satisfy Rubric 2.0
17. **Classifier-risk table or appendix block**
   - high-confidence subset rerun of one or two key tables
   - human-labeled subset rerun if feasible
   - exact thresholds and sample size
This is required because Rubric 2.0 treats misclassification sensitivity as a hard gate for a measurement paper.

---

# Part IV. Suggested revised paper map if the core tests work

## Main text
1. Abstract + intro lead with mismatch surge and market consequences
2. Figure 1 — mismatch surge through 2025
3. Table 1 — filing-date CARs
4. Figure 2 — post-filing drift
5. Table 2 — drift / BHAR / long–short alpha
6. Table 3 — small-firm heterogeneity
7. Table 4 — real effects
8. Table 5 — ChatGPT DID
9. Table 6 — financing / valuation consequences
10. Validation section:
   - current Table R2 / R3 / R6 / R7 as supporting evidence on credibility measurement

## Appendix
- timing matrices
- additional FE / trims
- additional event windows
- classifier sensitivity
- determinants tables
- attrition and audit tables

---

# Part V. Minimum information each run must return for writing
For each test, save a one-page “writer packet” with these fields:

## Metadata block
- Test name
- Date run
- Script path / notebook / Codex job name
- Input panel filename(s)
- Unit of observation
- Sample filters
- Date range
- N

## Variable block
- dependent variable definition
- key regressor definition
- treatment / event definition if any
- control set
- transformations (log, winsorization, standardization)

## Estimation block
- model equation
- fixed effects
- clustering
- weighting
- benchmark / abnormal return model

## Result block
- key coefficient(s)
- t-stat / standard error
- economic magnitude
- one-sentence interpretation
- whether this is a candidate for main text / appendix / discard

## Caption block
- 3–5 sentence ready-to-use caption text
- note on sample
- note on standard errors / significance coding

---

# Part VI. Execution order for the next 7–10 days

## Wave 1 — highest expected payoff
1. Figure R4 / updated mismatch surge through 2025
2. Test 2 filing-date CAR
3. Test 3 post-filing drift
4. Test 5 size heterogeneity
5. Test 7 ChatGPT DID

## Wave 2 — second layer
6. Test 6 real effects
7. Test 8 financing/valuation
8. Portfolio sort block from Test 4

## Wave 3 — validation refresh
9. Legacy reruns R1–R8
10. Appendix reruns A1–A2, B1–B2
11. High-confidence / human-labeled robustness block

---

# Part VII. Simple “send-to-Codex” prompts

## Prompt 1 — mismatch surge
Run the updated mismatch-incidence figure on the 2016–2025 ever-speaker panel. Use PatentMismatch exactly as defined in the paper. Output one figure with Panel A (annual mismatch count + annual mismatch share among AI-talking firm-years) and Panel B (top six sectors by mismatch count with sector mismatch shares annotated). Also export a CSV with year, mismatch_count, ai_talking_count, mismatch_share, and sector summaries.

## Prompt 2 — filing-date CAR
Build a filing-event dataset using annual 10-K filing dates and CRSP daily returns. Compute CAR[-1,+1], CAR[-2,+2], and CAR[-5,+5] using market-adjusted returns as the main baseline and a market-model robustness if feasible. Estimate difference-in-means and regression specifications with PatentMismatch, AS ratio, AI Focus, and lagged firm controls. Output one clean table, one event-window summary CSV, and one writer packet.

## Prompt 3 — post-filing drift
Using the filing-event dataset, compute post-filing abnormal returns over +2 to +21, +2 to +63, +2 to +126, and +2 to +252 trading days. Estimate regressions of post-filing abnormal returns on PatentMismatch, AS ratio, AI Focus, and lagged controls with industry and filing-year fixed effects. Also produce optional long–short portfolio spreads (non-mismatch minus mismatch among AI-talking firms).

## Prompt 4 — size heterogeneity
Create a small-vs-big split using the NYSE 50th percentile market-cap breakpoint. Re-estimate the filing-date CAR and post-filing drift regressions separately by size group and with PatentMismatch × Small interaction terms. Output one heterogeneity table and a compact comparison figure.

## Prompt 5 — ChatGPT DID
Build a ChatGPT post indicator using filings from 2023 onward. Define the main treated group as firms with zero pre-2023 AI patents and weak pre-2023 disclosure credibility. Estimate DID and event-study regressions for AI Focus, AS ratio, PatentMismatch, filing-date CAR, and post-filing drift. Output one DID table, one event-study figure with pre-trends, and one writer packet.

## Prompt 6 — real effects
Run annual panel regressions of future ROA, sales growth, CAPX/assets, R&D/assets, and any available patent-quality proxy on PatentMismatch, AS ratio, AI Focus, and baseline controls with firm and year fixed effects. Use horizons \(t+1\) and \(t+2\). Output one multi-panel table and one writer packet.

## Prompt 7 — financing / valuation
Using Compustat and CRSP annual variables, estimate valuation and financing regressions on PatentMismatch, AS ratio, and AI Focus. Use market-to-book (or Tobin’s Q) as the valuation outcome and one or more equity-issuance / financing proxies as the financing outcomes. Output one valuation table, one financing table, and one writer packet.

## Prompt 8 — validation refresh
Rerun the current validation backbone on the expanded 2016–2025 panel: summary stats, AI Focus timing, composition timing, actionable timing matrix, speculative timing matrix, AS ratio × PatentMismatch at \(t+1\) and \(t+2\), mismatch alignment figure, mismatch incidence figure, reduced determinants, full determinants, mismatch-share intensity determinants, measurement audit, and attrition map. Also produce a high-confidence classification subset version for at least one main mismatch regression and one composition regression.

---

# Part VIII. Parked Robustness Additions

These are intentionally parked so they are not forgotten, but they should not
derail the main execution sequence in Part VI.

## Robustness R-P1 — application-based PatentMismatch companion

After the main grant-based mismatch sequence is complete, build a companion
`PatentMismatch` construct using the true pregrant application series
(`applications_ai`) rather than the grant series (`patents_ai`).

Recommended posture:
- keep the grant-based mismatch construct as the main full-span result for the
  current paper sequence
- run the application-based mismatch as an appendix robustness or side-by-side
  companion
- likely use a safer truncated window (for example `2018–2023` or `2018–2024`)
  because the application series is still affected by publication-lag censoring
  in the latest years

## Robustness R-P2 — early-year mismatch stability diagnostic

Keep the full `2016–2025` yearly mismatch audit in the run bundle, but for the
paper-facing figure use `2018–2025` as the plotted window unless a later
robustness design resolves the early-year instability.

Reason:
- in `2016–2017`, the contemporaneous patent benchmark is too sparse
- the within-year low-credibility cutoff becomes mechanically unstable
- the early spike should be treated as a diagnostics issue, not as a headline
  economic result

If later useful, produce one appendix diagnostics table with:
- yearly AI-talking denominator
- yearly mismatch share
- yearly low-credibility share
- yearly weak-patent-relative share
- yearly AI patent count / any-patent share

## Robustness R-P3 — small-firm portfolio companion to Test 4

After the main Test 4 portfolio-sort sequence is frozen, add one appendix
portfolio companion that explicitly asks whether the long-credible / short-mismatch
spread is concentrated in smaller firms.

Recommended posture:
- keep the main Test 4 table focused on the broad cross-section plus the core
  size-split panel
- then run one companion portfolio table using a small-versus-big partition
  directly inside the strategy construction
- preferred implementation is:
  - define `Small = 1` using the monthly active-sample median lagged market cap
    when NYSE breakpoints are unavailable locally
  - within `Small = 1` and `Small = 0`, form the long-credible / short-mismatch
    spread separately
  - report equal-weight as the primary companion and value-weight as the
    robustness companion
- if useful, add an even sharper appendix cut using the bottom quartile of size
  versus the top quartile of size, but do not let that replace the cleaner
  median-split version

Reason:
- the current return evidence is visibly stronger in equal-weight space
- a direct small-firm portfolio companion can show whether the spread is
  genuinely a hard-to-value / small-firm phenomenon rather than a broad market
  pricing effect
