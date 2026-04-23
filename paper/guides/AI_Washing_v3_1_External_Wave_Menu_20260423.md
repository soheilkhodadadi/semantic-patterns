# AI-Washing v3.1 External-Wave Menu

Date: 2026-04-23  
Purpose: literature-based menu of next-wave tests after the `v3.1` repositioning, with live data-feasibility checks for this project environment.

## 1. Bottom Line

The nearby literatures point in a clear direction.

If we want a more exciting and still defensible next empirical wave, the best candidates are not more transformations of the same market-return panel. The best candidates are:

- external scrutiny and disclosure enforcement;
- analyst and institutional discernment;
- managerial incentives;
- board monitoring and board human capital;
- delayed real responses that look like costly catch-up.

The current environment is strong enough to run a real second wave, but not every natural dataset is actually readable under the current WRDS account.

### Readable now in this environment

Verified by live `SELECT ... LIMIT 1` checks on 2026-04-23:

- `ibes.statsum_epsus`, `ibes.det_guidance`
- `boardex.na_board_characteristics`, `boardex.na_dir_characteristics`, `boardex.na_board_education_assoc`, `boardex.na_company_profile_details`
- `execcomp.anncomp`, `execcomp.person`
- `audit.feed25_comment_letters`, `audit.feed40_comment_letter_threads`, `audit.feed17_director_and_officer_chan`, `audit_audit_comp.f06_form_ap_filing`
- `risk.directors`, `risk_directors.rmdirectors`

### Public data feasible even without WRDS

- SEC Form 13F data sets
- SEC EDGAR correspondence / comment letters
- SEC AI-washing enforcement and speeches
- EPA greenhouse-gas reporting data for future greenwashing work

### Visible in metadata but not readable under the current WRDS account

As of 2026-04-23, direct reads failed for:

- `tr_13f.*`
- `ciq_keydev.*` / `ciq.wrds_keydev`
- `reprisk.*`
- `trucost.*`
- `dealscan.*`
- full `iss_*` governance / incentive-lab tables

That means the highest-value immediate wave should lean on `Audit Analytics + IBES + BoardEx + ExecuComp + Risk Directors`, while public SEC 13F remains the best non-WRDS substitute for ownership tests.

## 2. What The Nearby Literatures Actually Suggest

## A. AI-specific papers

### Bandyopadhyay, Mai, and Pukthuanthong (2023), "AI Narrative and Stock Mispricing"

Method lessons:

- stronger market claims are earned through multifactor benchmarking;
- non-big concentration matters;
- industry-adjusted returns matter;
- return predictability should survive a rich characteristic set.

Transferable lesson for us:

- if we reopen the market lane later, it should be through discernment and information-intermediary channels, not another generic return transformation.

Local file:

- `paper/literature/Bandyopadhyay et al. - 2023 - AI Narrative and Stock Mispricing.pdf`

### Cohen, Malloy, and Nguyen (2020), "Lazy Prices"

Method lessons:

- disclosure text can matter even with no immediate announcement effect;
- later consequences become more credible when paired with operations, later news, or distress rather than returns alone;
- presentation is strongest when the paper moves from disclosure signal to downstream firm outcomes.

Transferable lesson for us:

- the right move is to push from disclosure credibility into scrutiny, operations, and later firm actions.

Local files:

- `paper/literature/2020 - COHEN - Lazy Prices - The Journal of Finance.pdf`
- `paper/literature/2020 Lazy Prices.appendix.pdf`

### Boyuan Li (2026), "AI Washing"

Method lessons:

- separate rhetoric from implementation;
- test institutional discernment;
- test managerial incentives using CEO wealth sensitivity;
- exploit issuance windows and salient AI shocks;
- compare short-run talk rewards with longer-run implementation outcomes.

Transferable lesson for us:

- our natural analogs are board/executive incentives, sophisticated-investor response, and staffing / governance catch-up rather than more portfolio plumbing.

Local file:

- `paper/literature/AI Washing Boyuan Li Mar2026.pdf`

### Donelson, Kim, Kim, and Yip (2025), "Strategic AI Disclosures"

Method lessons:

- compare disclosure to independent implementation data;
- link washers to weaker governance and financing needs;
- test ownership consequences using specialized investors;
- test labor / employment consequences.

Transferable lesson for us:

- governance and oversight are central, not auxiliary.

Source:

- [SSRN abstract page](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5265257)

## B. Greenwashing and adjacent disclosure literatures

### "Greenwashing in environmental, social and governance disclosures" (Research in International Business and Finance, 2020)

Method lessons:

- define washing as disclosure quantity outrunning actual performance;
- test independent directors, institutional investors, and scrutiny as deterrents;
- keep governance as determinants, not just consequences.

Transferable lesson for us:

- board monitoring and outside scrutiny deserve their own packet.

Source:

- [ScienceDirect page](https://www.sciencedirect.com/science/article/abs/pii/S0275531919309523)

### "Analyst coverage and greenwashing" papers

Method lessons:

- analyst coverage can be treated as an external monitor;
- the strongest versions use IVs or quasi-natural experiments such as brokerage closures / mergers;
- dispersion, revisions, and monitoring heterogeneity matter.

Transferable lesson for us:

- analysts are one of the best next tests because we have direct access to IBES.

Sources:

- [MDPI paper on analyst coverage and ESG greenwashing](https://www.mdpi.com/2071-1050/17/24/11138)
- [ScienceDirect paper on analyst coverage and greenwashing](https://www.sciencedirect.com/science/article/pii/S1059056024004155)

### "What drives stock market reactions to greenwashing?" (Finance Research Letters, 2025)

Method lessons:

- build allegation-based events carefully;
- code severity and materiality;
- expect heterogeneity by size and case type rather than uniform average effects.

Transferable lesson for us:

- if we ever reopen a market event lane, allegation / scrutiny events are better than another long-horizon filing drift test.

Source:

- [Open-access article page](https://www.sciencedirect.com/science/article/pii/S1544612325020495)

### Greenwashing measurement reviews

Method lessons:

- the dominant empirical families are:
  - talk-versus-walk discrepancy;
  - allegation / controversy event studies;
  - governance and monitoring determinants;
  - later financing, innovation, or operating consequences.

Transferable lesson for us:

- our next-wave menu should mirror those four families rather than improvising one-off robustness checks.

Sources:

- [Quantifying firm-level greenwashing: a systematic literature review](https://www.sciencedirect.com/science/article/pii/S0301479724033851)
- [Greenwashing prevention in ESG disclosures: a bibliometric analysis](https://www.sciencedirect.com/science/article/pii/S0275531924005130)

## 3. Data Feasibility Matrix

| Data family | What it supports | Status in this environment | Evidence |
| --- | --- | --- | --- |
| `IBES` | analyst coverage, forecast dispersion, guidance, revisions | Readable now | `ibes.statsum_epsus`, `ibes.det_guidance` |
| `BoardEx` | board human capital, director networks, board structure, senior-manager backgrounds | Readable now | `na_board_characteristics`, `na_dir_characteristics`, `na_board_education_assoc`, `na_company_profile_details` |
| `ExecuComp` | CEO equity incentives, delta/vega-style proxies, ownership sensitivity | Readable now | `anncomp`, `person` |
| `Audit Analytics` | SEC comment letters, officer/director changes, filing-level audit / disclosure follow-up | Readable now | `feed25_comment_letters`, `feed40_comment_letter_threads`, `feed17_director_and_officer_chan`, `f06_form_ap_filing` |
| `Risk Directors` | director classification, board committees, monitoring structure | Readable now | `risk.directors`, `risk_directors.rmdirectors` |
| SEC public 13F | institutional ownership, ownership changes, concentration, specialist investors | Public alternative | [SEC Form 13F data sets](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets) |
| SEC EDGAR correspondence | public comment-letter threads and responses | Public alternative | [How to search EDGAR correspondence](https://www.sec.gov/answers/how-to-search-for-edgar-correspondence) |
| SEC enforcement / speeches | regulatory-shock designs | Public alternative | [AI-washing enforcement release](https://www.sec.gov/newsroom/press-releases/2024-36) |
| `tr_13f` on WRDS | ownership tests | Not readable now | schema visible, direct select denied |
| `ciq_keydev` on WRDS | key developments / regulatory event screens | Not readable now | table visible, direct select denied |
| `reprisk` on WRDS | controversy / misleading-communication incidents | Not readable now | table visible, direct select denied |
| `trucost` on WRDS | claims-vs-performance decoupling for greenwashing | Not readable now | table visible, direct select denied |
| `dealscan` on WRDS | loan spreads, covenants, bank discipline | Not readable now | table visible, direct select denied |
| full `ISS` governance tables | governance scores, incentive-lab fields | Not readable now | metadata visible, direct select denied |

## 4. Ranked Menu Of Plausible Next Tests

The list below is ranked by:

- relevance to the current AI-washing story;
- likelihood of producing interpretable results;
- feasibility with our actual access;
- usefulness at a strict conference or referee stage.

## Rank 1. AI-specific SEC comment-letter scrutiny

Question:

- are low-credibility AI disclosers more likely to attract SEC comment-letter scrutiny?

Design:

- link `PatentMismatch` / `LowCredibility` to later AI-related comment-letter incidence;
- use comment-letter text and issue tags to identify AI, automation, technology-risk, or disclosure-basis themes.

Why it is valuable:

- direct test of external disclosure scrutiny;
- much cleaner than another generic market reaction test;
- highly legible to referees.

Data:

- `audit.feed25_comment_letters`
- `audit.feed40_comment_letter_threads`
- public EDGAR correspondence as backup

Priority:

- very high

## Rank 2. Disclosure cleanup after comment letters

Question:

- after receiving AI-related SEC scrutiny, do firms reduce speculative AI language, reduce mismatch, or rebalance toward more credible disclosure?

Design:

- within-firm before/after event design around first AI-related comment-letter thread;
- outcomes: `SpecShare`, `A_S`, `PatentMismatch`, `AI_Focus`.

Why it is valuable:

- turns scrutiny into a dynamic disclosure-response test;
- directly addresses whether oversight disciplines the narrative.

Data:

- same as Rank 1 plus the existing filing panel

Priority:

- very high

## Rank 3. Analyst discernment: forecast dispersion and revisions

Question:

- do analysts treat mismatch firms as harder to value?
- do mismatch filings predict higher forecast dispersion, more negative revisions, or worse guidance reception?

Design:

- panel regressions of next-quarter / next-year analyst dispersion, revisions, and guidance outcomes on `PatentMismatch`, `A_S`, and `LowCredibility`;
- heterogeneity by non-big firms and prior patent stock.

Why it is valuable:

- keeps the information-intermediary angle without overclaiming a return anomaly;
- well aligned with the greenwashing analyst-monitoring literature.

Data:

- `ibes.statsum_epsus`
- `ibes.det_guidance`
- existing firm panel

Priority:

- very high

## Rank 4. Analyst coverage as an external monitor

Question:

- does stronger analyst coverage attenuate future mismatch, or attenuate the link between mismatch and later weak outcomes?

Design:

- interaction tests using analyst coverage level;
- later extension could use coverage shocks or brokerage disruptions if needed.

Why it is valuable:

- directly mirrors the greenwashing-monitoring literature;
- feasible with currently readable data.

Data:

- `ibes.statsum_epsus`

Priority:

- high

## Rank 5. Science/technology leadership appointments as costly catch-up

Question:

- do mismatch firms later appoint science/technology officers or directors, consistent with delayed catch-up?

Design:

- use officer/director change records to identify later `is_scitech_pers` appointments, CTO-like roles, or science/tech board additions after mismatch;
- event windows at `t+1` and `t+2`.

Why it is valuable:

- this could become one of the more exciting non-market results;
- it turns the story from "weak future patents" into "later costly organizational response."

Data:

- `audit.feed17_director_and_officer_chan`
- existing panel

Priority:

- high

## Rank 6. Executive incentives and narrative inflation

Question:

- are firms with stronger equity-based managerial incentives more likely to engage in low-credibility AI disclosure?

Design:

- test CEO equity sensitivity / ownership / option exposure against mismatch and post-ChatGPT shifts;
- use firm fixed effects where feasible.

Why it is valuable:

- close analog to Boyuan Li's incentive design;
- likely more publishable than another financing proxy table.

Data:

- `execcomp.anncomp`
- `execcomp.person`

Priority:

- high

## Rank 7. Board monitoring and committee structure

Question:

- do more independent or more intensively monitored boards reduce mismatch?
- do audit / compensation / governance committees attenuate mismatch consequences?

Design:

- use director classification, committee memberships, outside-board load, and board composition;
- test both determinants and moderators.

Why it is valuable:

- strongly supported by the greenwashing governance literature;
- directly addresses a remaining referee question.

Data:

- `risk_directors.rmdirectors`
- `risk.directors`

Priority:

- high

## Rank 8. Board AI / tech human capital

Question:

- does director human capital in technical or technology-adjacent roles reduce mismatch or speed later real realization?

Design:

- build board expertise proxies from prior roles, listed associations, education associations, and senior-manager backgrounds in BoardEx.

Why it is valuable:

- more novel than a generic governance score;
- could become a distinctive mechanism result.

Data:

- `boardex.na_board_characteristics`
- `boardex.na_dir_characteristics`
- `boardex.na_board_education_assoc`
- `boardex.na_board_listed_assoc`
- `boardex.na_company_profile_sr_mgrs`

Priority:

- high but more construction-heavy

## Rank 9. SEC AI-washing enforcement shock DID

Question:

- after the SEC's March 18, 2024 AI-washing enforcement actions and related speeches, do high-mismatch firms reduce speculative disclosure or change its composition?

Design:

- simple staggered annual DID using 2024 and 2025 filings;
- outcomes: `SpecShare`, `A_S`, `PatentMismatch`, maybe disclosure verbosity.

Why it is valuable:

- very cheap to run;
- gives a policy / regulatory-salience angle;
- useful even if effects are modest.

Data:

- existing filing panel
- public event dates from SEC

Priority:

- medium-high

## Rank 10. Institutional discernment using public SEC 13F data

Question:

- do institutional investors reduce exposure to mismatch firms, or avoid them relative to more credible AI disclosers?

Design:

- ownership-level panel or change-in-ownership panel using official SEC 13F data;
- focus first on broad ownership and concentration, then specialized tech investors if feasible.

Why it is valuable:

- conceptually strong;
- close analog to the AI-washing and greenwashing investor-monitoring literatures;
- still possible even though WRDS `tr_13f` is not readable here.

Data:

- [SEC Form 13F data sets](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets)

Priority:

- medium-high, but heavier pipeline cost

## Rank 11. Capital-raising timing and disclosure opportunism

Question:

- does low-credibility AI disclosure intensify before financing events?

Design:

- start with existing share-issuance proxies and extend only if needed;
- if a better offerings source becomes available later, revisit as a dedicated packet.

Why it is valuable:

- ties the disclosure story to clear managerial incentives;
- but less urgent than the scrutiny / analyst / governance lane.

Data:

- existing Compustat-style issuance proxies now
- optional future public or WRDS offering data later

Priority:

- medium

## Rank 12. Future greenwashing bridge: claims-versus-actions design

Question:

- for a future greenwashing project, can we replicate the same discrepancy logic with environmental claims and realized environmental performance?

Design:

- pair textual or report-based environmental claims with facility emissions, carbon disclosures, or ESG incident data;
- event or panel consequences follow only after the discrepancy measure is validated.

Why it is valuable:

- directly reusable for later greenwashing work;
- methodologically parallel to the current AI paper.

Data options:

- public EPA GHGRP data
- public CDP data access where feasible
- Trucost / RepRisk only if access is expanded later

Sources:

- [EPA GHGRP](https://www.epa.gov/ghgreporting)
- [CDP data page](https://www.cdp.net/en/data)

Priority:

- medium for the current AI paper, high for the future greenwashing pipeline

## 5. What I Would Run First

If we want the best combination of upside, defensibility, and realistic effort, I would stage the next wave in this order:

1. SEC comment-letter scrutiny
2. Disclosure cleanup after comment letters
3. Analyst discernment packet
4. Science/technology appointment response
5. Executive incentives
6. Board monitoring / board human capital

That sequence is better than starting with public 13F because:

- it uses data we can already read right now;
- it produces cleaner mechanism evidence;
- it is more likely to sharpen the paper than another market-return extension.

## 6. Suggested Packetization

To keep the next wave stable and versioned, I would packet it like this:

- `packet_d_scrutiny`
  - `test_19_sec_comment_letter_scrutiny`
  - `test_20_comment_letter_cleanup`
- `packet_e_intermediaries`
  - `test_21_analyst_discernment`
  - `test_22_analyst_monitoring_interaction`
- `packet_f_governance`
  - `test_23_scitech_appointment_response`
  - `test_24_exec_incentive_mismatch`
  - `test_25_board_monitoring`
  - `test_26_board_tech_human_capital`
- `packet_g_public_ownership`
  - `test_27_public_13f_institutional_discernment`

## 7. Decision Rule Before We Start Running Them

The clean rule is:

- run the readable-now packets first;
- only open the public 13F lane after we finish the scrutiny and analyst packets;
- do not open blocked WRDS datasets unless access actually changes.

That keeps the next empirical wave ambitious without making it fragile.

## 8. Source List

Local sources:

- `paper/literature/Bandyopadhyay et al. - 2023 - AI Narrative and Stock Mispricing.pdf`
- `paper/literature/2020 - COHEN - Lazy Prices - The Journal of Finance.pdf`
- `paper/literature/2020 Lazy Prices.appendix.pdf`
- `paper/literature/AI Washing Boyuan Li Mar2026.pdf`

External sources:

- [Strategic AI Disclosures (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5265257)
- [Greenwashing in environmental, social and governance disclosures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919309523)
- [Analyst coverage and ESG greenwashing (MDPI)](https://www.mdpi.com/2071-1050/17/24/11138)
- [Analyst coverage and greenwashing (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S1059056024004155)
- [What drives stock market reactions to greenwashing?](https://www.sciencedirect.com/science/article/pii/S1544612325020495)
- [Quantifying firm-level greenwashing: a systematic literature review](https://www.sciencedirect.com/science/article/pii/S0301479724033851)
- [Greenwashing prevention in ESG disclosures: a bibliometric analysis](https://www.sciencedirect.com/science/article/pii/S0275531924005130)
- [SEC Form 13F data sets](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets)
- [How to Search for EDGAR Correspondence](https://www.sec.gov/answers/how-to-search-for-edgar-correspondence)
- [SEC AI-washing enforcement release](https://www.sec.gov/newsroom/press-releases/2024-36)
- [Chair Gary Gensler on AI Washing](https://www.sec.gov/newsroom/speeches-statements/sec-chair-gary-gensler-ai-washing)
- [EPA GHGRP](https://www.epa.gov/ghgreporting)
- [CDP data page](https://www.cdp.net/en/data)
