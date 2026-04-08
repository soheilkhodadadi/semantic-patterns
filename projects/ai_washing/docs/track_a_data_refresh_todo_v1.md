
# AI-Washing Track A Data Refresh To-Do V1

## Purpose

This note turns the current Track A source reviews into the practical next-step
sequence for execution.

## Decisions already made

### Filing/disclosure lane
- proceed immediately with `2025` sentence cleanup
- then classify the cleaned `2025` annual 10-K sentence table

### Patent lane
- keep both patent-timing lanes active:
  - true pregrant application filing timing for the conceptually cleaner lane
  - corrected hybrid grant timing for the less-censored full-span backbone
- expand the patent window to `2014-2025`
- rebuild the panel from a refreshed disclosure-side speaker universe rather
  than merging new patent outputs into the old panel backbone
- prefer PatentsView **pregrant tables** over raw USPTO XML for the serious
  application-timing rebuild

### Market-reaction lane
- keep this as a separate lane from the annual disclosure/patent rebuild
- use SEC filing dates as the event anchor
- use daily CRSP/CCM data for the first event window
- use annual fundamentals from CCM for controls

## Immediate execution sequence

Completed:
1. `2025` sentence cleanup
2. `2025` classification
3. `2025` classification spot check
4. refreshed `2016-2025` narrative measures
5. refreshed speaker-firm universe
6. refreshed WRDS identity/crosswalk + annual controls
7. refreshed hybrid grant-timed patent rebuild
8. refreshed annual ever-speaker panel backbone on the hybrid grant lane
9. true pregrant application-timed patent lane
10. combined refreshed panel with both grant and application timing
11. patent-matching robustness note and shareable report package
12. first A/S classifier audit pack and probe slice
13. bounded `2024` fuzzy sensitivity run and rejection of fuzzy matching as a
    live patent robustness lane
14. merge restructure/publication-refresh work back into `main`
15. open fresh branch `codex/ai-washing-publication-upgrade`

Next:
16. benchmark the revised A/S rubric on the fixed `16`-row probe slice
17. build a small rubric-probe review pack for fast sub-agent and later human
    benchmark review
18. expand to a larger reviewed boundary pack and test whether stricter rubric
    variants meaningfully diverge
19. move to targeted training-set cleanup / expansion and local retraining under
    the revised default rubric
20. if local-model gains stall after rubric cleanup and retraining, open an
    API-based robustness lane rather than forcing the same architecture past its
    credible ceiling
21. if the local model remains strong on easy cases but weak on a narrow hard
    tail, test a selective-defer hybrid classifier that escalates only edge
    cases to API arbitration, with:
    - API `A` as the cheaper first deferred call
    - API `B` as the stronger disagreement arbiter
    - no human tie-break in the live path
22. after the annual backbone is stable, open the filing-date event-study lane
    using daily return data

Classifier-upgrade planning anchors:
- `projects/ai_washing/docs/track_a_2025_classification_spot_check_v1.md`
- `projects/ai_washing/docs/track_a_classifier_upgrade_diagnostic_plan_v1.md`
- `projects/ai_washing/docs/track_a_classifier_upgrade_execution_roadmap_v1.md`
- `projects/ai_washing/docs/track_a_phase1_rubric_benchmark_v1.md`

## Data dependencies to prepare

### PatentViews
- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_assignee_disambiguated.tsv`
- `pg_published_application`
- `pg_published_application_abstract`
- `pg_assignee_disambiguated`
- `pg_granted_pgpubs_crosswalk`
- optional `pg_applicant_not_disambiguated`

### WRDS / CCM
- `ccmsecd` for daily event-window returns
- `ccmfunda` for annual controls

## What we are intentionally not doing yet

- not folding event-study data requirements into the annual panel rebuild
- not treating monthly returns as the main event-study input
- not using the old exploratory patent scripts for the refreshed patent lane
- not treating the old panel as the implicit source of truth for refreshed firm
  identity
- not treating the current classifier as the automatically final model for the
  rerun; model-upgrade review still has to happen before final empirical output
- not replacing the exact normalized patent match with fuzzy matching in the
  baseline method because the bounded `2024` sensitivity test showed the current
  fuzzy supplement is too noisy

## Bottom line

The fastest safe path now is:
- use the refreshed hybrid grant lane to keep the panel rebuild moving
- build a true pregrant application lane rather than forcing application timing
  through a grant-centered source
- make an explicit publication-lag decision before treating the latest
  application years as final-paper-grade
- open the market-reaction lane after the refreshed annual backbone is rebuilt

Operational lesson captured here:
- `reports/final/ai_washing_long_run_job_resilience_lessons_v1.md`
