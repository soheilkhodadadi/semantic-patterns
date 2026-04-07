
# AI-Washing Track A Data Refresh To-Do V1

## Purpose

This note turns the current Track A source reviews into the practical next-step
sequence for execution.

## Decisions already made

### Filing/disclosure lane
- proceed immediately with `2025` sentence cleanup
- then classify the cleaned `2025` annual 10-K sentence table

### Patent lane
- use application filing timing as the preferred main path
- keep grant-date timing as a later robustness lane if useful
- expand the patent window to `2014-2025`

### Market-reaction lane
- keep this as a separate lane from the annual disclosure/patent rebuild
- use SEC filing dates as the event anchor
- use daily CRSP/CCM data for the first event window
- use annual fundamentals from CCM for controls

## Immediate execution sequence

1. Finish `2025` sentence cleanup.
2. Classify the cleaned `2025` sentence table into the annual clean model lane.
3. Run a spot-check pass on the cleaned/classified `2025` outputs to confirm
   sentence quality, segmentation quality, and absence of obvious junk rows.
4. Patch patent extractor filename resolution for the new `g_*` PatentViews
   files.
5. Extend the filtered patent workflow to join `g_application.tsv` and carry
   `filing_date`.
6. Rebuild the patent series on a `2014-2025` window.
7. Open the classifier-upgrade planning lane before any final regression or
   event-study reruns.
8. Rebuild the annual ever-speaker panel only after the widened patent window
   is ready and the classifier-upgrade decision is explicit.
9. After the annual backbone is stable, open the filing-date event-study lane
   using daily return data.

Classifier-upgrade planning anchors:
- `projects/ai_washing/docs/track_a_2025_classification_spot_check_v1.md`
- `projects/ai_washing/docs/track_a_classifier_upgrade_diagnostic_plan_v1.md`

## Data dependencies to prepare

### PatentViews
- `g_application.tsv`
- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_assignee_disambiguated.tsv`

### WRDS / CCM
- `ccmsecd` for daily event-window returns
- `ccmfunda` for annual controls

## What we are intentionally not doing yet

- not folding event-study data requirements into the annual panel rebuild
- not treating monthly returns as the main event-study input
- not using the old exploratory patent scripts for the refreshed patent lane
- not treating the current classifier as the automatically final model for the
  rerun; model-upgrade review still has to happen before final empirical output

## Bottom line

The fastest safe path now is:
- keep the sentence/classification lane moving immediately
- prepare the patent lane correctly for application filing timing
- open the market-reaction lane after the refreshed annual backbone is rebuilt
