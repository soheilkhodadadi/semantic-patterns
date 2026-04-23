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

## 7. Packet H: Optional / Deferred

## Test 29. `test_29_sec_ai_washing_enforcement_did`

Cheap policy-salience extension around the March 18, 2024 SEC AI-washing actions.

## Test 30. `test_30_capital_raising_timing`

Only reopen if we still want a financing-opportunism angle after Packet F.

## Test 31. `test_31_greenwashing_claims_vs_actions_bridge`

Future bridge to a greenwashing project. Not a current-paper blocker.

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
