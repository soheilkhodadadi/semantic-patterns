# AI-Washing v3.2 Operational Run Sheet

Date: 2026-04-23  
Purpose: operational test sheet for the `v3.2` external-wave packet sequence.

## 1. Global Output Contract

Every `v3.2` test should write:

- one source-of-truth run folder under  
  `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/<test_id>/<run_id>/`
- one `run_manifest.json`
- one main table in:
  - `paper/generated/v3_2/docx/`
  - `paper/generated/v3_2/latex/`
  - `paper/generated/v3_2/tables/`
- one writer packet in:
  - `paper/generated/v3_2/writer_packets/`
- one result-notes snippet in:
  - `paper/generated/v3_2/snippets/`

Add a figure only when it materially improves interpretation.

## 2. v3.2 Naming Rule

Use:

- `TEST_ID = test_XX_descriptive_name`
- `run_id = YYYYMMDD_aiw_v3_2_<test_id>_main_v1`

If we rerun with a real methodological change, bump `main_v2`, not a silent overwrite.

## 3. Packet D: Scrutiny

## Test 19. `test_19_sec_comment_letter_scrutiny`

Question:

- are low-credibility AI disclosers more likely to attract later SEC comment-letter scrutiny?

Minimum inputs:

- annual ever-speaker panel
- `PatentMismatch`, `LowCredibility`, `A_S`, `AI_Focus`
- Audit Analytics `feed25_comment_letters`
- Audit Analytics `feed40_comment_letter_threads`

Preferred identification:

- firm-year panel inside the AI-talking universe
- later scrutiny incidence over `t+1` and `t+2`
- firm-level or industry-level absorbed regressions depending on event density

Minimum outputs:

- event-count audit by year and by scrutiny definition
- main table with at least:
  - narrow AI-scrutiny incidence
  - broader technology/disclosure scrutiny incidence if needed
- one short figure showing event counts through time
- writer packet explaining event-definition choices

Go / no-go criterion:

- if the narrow AI event count is thin, preserve the audit and switch the main incidence result to the broader technology/disclosure scrutiny definition.

## Test 20. `test_20_comment_letter_cleanup`

Question:

- after scrutiny, does disclosure become more credible?

Minimum inputs:

- matched scrutiny event file from Test 19
- annual filing panel with `SpecShare`, `A_S`, `PatentMismatch`, `AI_Focus`

Preferred identification:

- within-firm before/after event design
- lead/lag event-time table
- at least one narrow and one broad scrutiny definition

Minimum outputs:

- one dynamic table
- one event-time figure
- writer packet with interpretation discipline

Go / no-go criterion:

- only promote to main text if the post-scrutiny shift is both directionally coherent and not entirely driven by one extreme year.

## 4. Packet E: Intermediaries

## Test 21. `test_21_analyst_discernment`

Question:

- do analysts treat low-credibility AI disclosers as harder to value or more uncertain?

Minimum inputs:

- annual panel
- IBES summary history
- optionally IBES guidance

Primary outcomes:

- analyst coverage
- forecast dispersion
- mean forecast revision
- guidance response where feasible

Minimum outputs:

- one table with at least two outcome families:
  - attention / coverage
  - uncertainty / dispersion / revisions
- one figure on coverage or dispersion by mismatch status
- writer packet

Go / no-go criterion:

- promote if either dispersion or revisions respond coherently, even if pure coverage is flat.

## Test 22. `test_22_analyst_monitoring_interaction`

Question:

- does stronger analyst coverage attenuate mismatch or attenuate its later consequences?

Minimum inputs:

- annual panel
- analyst coverage measure from Test 21

Preferred identification:

- interaction between mismatch and coverage
- outcomes can include future patents, `ROA t+2`, or scrutiny incidence

Minimum outputs:

- one interaction table
- writer packet with substitution-versus-monitoring interpretation

Go / no-go criterion:

- keep only if the interaction is more informative than the level effect in Test 21.

## Test 23. `test_23_analyst_coverage_splits`

Question:

- do the later consequences of mismatch concentrate in low-coverage firms, high-coverage firms, or both?

Minimum inputs:

- annual panel
- analyst coverage measure from Test 21

Preferred identification:

- same-year coverage buckets
- at minimum:
  - lower half vs upper half
  - bottom quartile vs top quartile
- re-estimate the canonical consequence regressions within each slice

Primary outcomes:

- future mismatch persistence
- future AI grants
- later `ROA`

Minimum outputs:

- one split-sample table
- one coefficient-comparison figure
- writer packet explaining whether the split sharpened or complicated the analyst story

Go / no-go criterion:

- keep if the slice design reveals a cleaner attention or monitoring pattern than the interaction-only specification.

## 5. Packet F: Governance and Incentives

## Test 24. `test_24_scitech_appointment_response`

Question:

- do mismatch firms later add science/technology leadership?

Minimum inputs:

- annual panel
- Audit Analytics `feed17_director_and_officer_chan`

Primary outcomes:

- later appointments flagged as science/technology
- CTO / technology-lead appointment variants if identifiable

Minimum outputs:

- one table for appointment incidence
- one figure for event timing
- writer packet framing this as costly catch-up rather than clean causality

## Test 25. `test_25_exec_incentive_mismatch`

Question:

- do stronger executive equity incentives predict low-credibility AI disclosure?

Minimum inputs:

- annual panel
- ExecuComp annual compensation data

Primary outcomes:

- mismatch level
- post-ChatGPT change in mismatch

Minimum outputs:

- one determinants table
- one interaction / heterogeneity table if justified
- writer packet

Status after first live run (2026-04-23):

- usable and stronger than the earlier financing-proxy lane
- best signals are:
  - big-firm `PatentMismatch` on lagged CEO ownership pct
  - post-ChatGPT `PatentMismatch` on lagged CEO equity-award share and lagged CEO ownership pct
- current placement: live Packet F main-text candidate, with explicit note that the evidence is limited to the ExecuComp-covered universe

## Test 26. `test_26_board_monitoring`

Question:

- do board monitoring structure and committee composition reduce low-credibility AI disclosure?

Minimum inputs:

- annual panel
- Risk Directors

Primary predictors:

- committee membership
- outside-board load
- female director share where stable
- monitoring classification variables

Minimum outputs:

- one determinants table
- one moderation table if usable

Status after first live run (2026-04-23):

- usable without needing a second board-data wave
- cleanest predictors are:
  - lagged average outside public boards
  - lagged board size
- governance-committee and audit-share terms are directionally helpful, but less precise
- current placement: strong appendix or internet-appendix candidate, with an upgrade path to main-text support if Packet F remains central

## Test 27. `test_27_board_tech_human_capital`

Question:

- does board technical human capital reduce mismatch or speed later realization?

Minimum inputs:

- annual panel
- BoardEx director and education / association tables

Primary constructs:

- director technology-role history
- board technical exposure index
- optional senior-manager technical background index

Minimum outputs:

- one construct-audit table
- one main regression table
- one figure if the construct has an interesting distribution

Go / no-go criterion:

- only keep if the constructed board-tech proxy is interpretable and not too sparse.

Status after first live run (2026-04-23):

- keep, but as a supportive capability-governance result rather than a headline table
- the narrow technical-leadership proxy is interpretable and the better specification
- the broader board-tech-human-capital share is directionally stronger for `PatentMismatch`, but the STEM layer is sparse
- current placement: appendix or internet appendix, with the option to reference it in the main text as a capability-side robustness result

## 6. Packet G: Public Ownership

## Test 28. `test_28_public_13f_institutional_discernment`

Question:

- do institutional investors reduce exposure to low-credibility AI disclosers?

Minimum inputs:

- annual panel
- public SEC 13F ingestion lane

Primary outcomes:

- ownership level
- ownership change
- ownership concentration

Minimum outputs:

- one ownership table
- one concentration or change figure
- writer packet with data-pipeline caveat

Go / no-go criterion:

- only start after Packet D and Packet E are complete.

Status after first live run (2026-04-23):

- build succeeded and the public 13F ingestion lane is now cached through 2025 Q4
- linkage coverage:
  - CRSP-linked panel rows: `7,378`
  - t+1 ownership-linked rows: `4,278`
- empirical read:
  - `PatentMismatch` is broadly null for next-year ownership share, ownership change, holder breadth, and concentration
  - the big-firm slice shows a weak positive level association for next-year ownership share, not a disciplining result
  - the post-ChatGPT split is not estimable with firm fixed effects because there is no within-firm predictor variation in the ownership-linked post sample
- current placement: appendix / boundary-result table unless a later ownership refinement yields a cleaner discernment signal

## 7. Packet H: Optional / Deferred

## Test 29. `test_29_sec_ai_washing_enforcement_did`

Cheap policy-salience extension around the March 18, 2024 SEC AI-washing actions.

Status after first live run (2026-04-23):

- build succeeded and the policy-salience lane is now versioned in `v3_2`
- design used:
  - treatment fixed in `2022` among AI-talking firms
  - `2023` kept as a placebo / pretrend year
  - `2024-2025` treated as the post-enforcement period after the SEC's March 18, 2024 actions
- coverage:
  - analysis sample: `8,055` firm-years across `1,611` firms
  - main treated firms: `457`
- empirical read:
  - strong post-2024 cleanup in disclosure composition for pre-exposed firms
  - main-treatment DID estimates:
    - `SpecShare`: `-0.0839` (`p<0.001`)
    - `A/S`: `0.2907` (`p<0.001`)
    - `PatentMismatch`: `-0.3121` (`p<0.001`)
  - alternative treatment definitions (`LowCredibility`, `ApplicationMismatch`) deliver the same directional pattern
  - `AI_Focus` does not fall materially
  - the `2023` placebo coefficients are already directional for composition outcomes, so this is not a clean causal enforcement estimate
- current placement: strong supporting regulatory-salience extension; promote only with explicit language that the result looks like acceleration / cleanup after salience rather than a fully clean DID

## Test 30. `test_30_capital_raising_timing`

Only reopen if we still want a financing-opportunism angle after Packet F.

Status after first live run (2026-04-23):

- build succeeded and the timing/opportunism lane is now versioned in `v3_2`
- design used:
  - first large equity-issuance event per firm
  - issue rule: `Issue>5%` when next-year CRSP shares-outstanding growth exceeds 5%
  - event year `0` is the disclosure year before that issuance window
  - sample focuses on active AI issuers that continue talking about AI in year `0` and year `+1`
- coverage:
  - first issue-event firms: `2,105`
  - active AI issue-event firms: `367`
  - non-big active AI issue-event firms: `251`
- empirical read:
  - low-credibility disclosure intensifies into the issuance window and then partly unwinds afterward
  - all active AI issuers:
    - `LowCredibility`: `+0.2334` from `t-1` to event year, then `-0.1063` from event year to `t+1`
    - `PatentMismatch`: `+0.1787` into event year, then `-0.0926` after issuance
    - `SpecShare`: `+0.1187` into event year
    - `AI_Focus`: keeps rising before and after issuance
  - the non-big sample retains the same rise-then-partial-unwind pattern
- current placement: stronger than the earlier broad financing-outcome regressions; good supporting financing-opportunism extension with clear timing interpretation

## Test 31. `test_31_greenwashing_claims_vs_actions_bridge`

Status after closeout review (2026-04-23):

- reviewed conceptually against nearby greenwashing methods
- not a current-paper blocker
- current recommendation: defer to future work

Reason:

- the current paper already has a claims-actions / decoupling logic through:
  - text-based disclosure composition
  - later AI patent realization
  - scrutiny-driven cleanup
  - financing-window deterioration and partial unwind
- a greenwashing bridge would now be more useful for a later cross-domain project than for the current rewrite

## Packet H follow-on checklist

1. `test_32_market_reaction_in_issue_windows`
   - status: completed on `2026-04-23`
   - design:
     - filing-event returns collapsed to one firm-year observation
     - merged to annual `IssueWindow` from Test 30
     - interaction regressions for:
       - `CAR[-1,+1]`
       - `BHAR[+2,+63]`
       - `BHAR[+2,+252]`
   - coverage:
     - merged filing-year rows: `4,455`
     - firms: `1,605`
     - issue-window rows: `1,138`
   - key read:
     - outside issue windows, `PatentMismatch` predicts weaker `BHAR[+2,+63]`: `-0.0272` (`p=0.004`)
     - inside issue windows, the negative relation compresses:
       - `PatentMismatch × IssueWindow`: `+0.0716` (`p=0.038`)
       - non-big: `+0.0918` (`p=0.068`)
     - filing-date `CAR[-1,+1]` remains null
   - current placement:
     - supporting market refinement alongside Test 30

2. `test_33_post_enforcement_market_split`
   - screened informally on `2026-04-23`, not yet formalized
   - quick read:
     - direct market DID using pre-2022 mismatch exposure and filing-year returns is weak / mostly null
     - `BHAR[+2,+252]` is effectively not estimable because the linked filing-return panel only contributes through `2024`
     - `CAR[-1,+1]` is only marginal at best under alternative treatment definitions
   - current recommendation:
     - do not promote this into a full packet unless we need an explicit regulatory-market null in the internet appendix
     - the stronger move is to keep Tests 29, 30, and 32 together as the main Packet H contribution

3. presentation pass
   - if Tests 29, 30, and 32 all survive, decide whether they are best reported as:
     - separate tables
     - one compact multi-panel main-text section
     - or a mix of main text plus internet appendix

## 8. Recommended Immediate Sequence

Run in this order:

1. `test_19_sec_comment_letter_scrutiny`
2. `test_20_comment_letter_cleanup`
3. `test_21_analyst_discernment`
4. `test_22_analyst_monitoring_interaction`
5. `test_23_analyst_coverage_splits`
6. `test_24_scitech_appointment_response`

Checkpoint after these six:

- decide which signals are strong enough for main text
- only then continue to the rest of Packet E / F

## 9. Execution Rule

Do not let the packet list become a grab bag.

For each test:

- run
- evaluate
- decide whether to deepen
- then move on

The point of `v3.2` is not to maximize count.  
It is to maximize the number of paper-usable results that are both interesting and defensible.
