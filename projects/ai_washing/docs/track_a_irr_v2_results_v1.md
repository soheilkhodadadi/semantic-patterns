# Track A IRR V2 Results V1

## Purpose

Record the first revised-rubric IRR return after the selective-defer benchmark
lane and convert it into a clear promotion decision for the classifier stack.

This note answers four questions:
1. what is the current human-human IRR v2 result?
2. where is disagreement still concentrated?
3. is the selective-defer runtime technically ready?
4. should the project proceed to a new full panel build now?

## Inputs

- rater-1 master:
  - `data/labels/v1/irr_subset_boundary_revised_v2_master.csv`
- returned second-rater workbook:
  - `data/labels/v2/irr_subset_boundary_revised_v2_rater2_blinded_Filled.xlsx`
- provisional adjudication staging:
  - `data/labels/v2/adjudication_boundary_revised_v2.parquet`
- scoring outputs:
  - `reports/labels/irr_boundary_revised_v2_report.json`
  - `reports/labels/irr_boundary_revised_v2_confusion_matrix.csv`
  - `reports/labels/irr_boundary_revised_v2_transition_counts.csv`
  - `reports/labels/irr_boundary_revised_v2_status.json`
- disagreement sheet:
  - `data/labels/v2/irr_boundary_revised_v2_adjudication_sheet.xlsx`

## IRR v2 result

Headline result:
- status: `pending_adjudication`
- reviewed rows: `120`
- kappa: `0.6625`
- disagreements: `27`
- gate result: `deferred`

This does not clear the current minimum gate of `0.70`.

## Comparison to prior IRR

Previous official IRR:
- source: `reports/labels/irr_report.json`
- kappa: `0.6750`
- disagreements: `26`

Revised IRR v2:
- kappa: `0.6625`
- disagreements: `27`

Interpretation:
- the revised rubric did not improve headline human-human agreement
- the revised cycle is directionally cleaner in rationale quality, but that did
  not translate into a better top-line IRR

## Where disagreement remains

Transition counts:
- `A -> I`: `4`
- `S -> A`: `10`
- `S -> I`: `11`
- `I -> A`: `1`
- `I -> S`: `1`
- `A -> S`: `0`

By-class kappa:
- `Actionable`: `0.7305`
- `Speculative`: `0.5286`
- `Irrelevant`: `0.7052`

Critical read:
- `Actionable` is now the strongest class
- `Irrelevant` is acceptable but not strong enough to offset the weak center
- `Speculative` remains the bottleneck
- the main instability is no longer `Actionable` vs `Speculative` in both
  directions equally
- it is specifically the over-fragility of `Speculative`

That matches the earlier boundary audits: future-intent and in-progress build
sentences still produce inconsistent human decisions.

## Playbook trace

Consulted curated playbook:
- `director/playbooks/prompt_boundary_benchmark.md`

Observed outcome against the playbook stop condition:
- the benchmark slice was frozen
- prompt and rubric variants were tested on that fixed slice
- local model design then improved further with selective defer
- but the revised human-human IRR still failed to clear the gate

Conclusion:
- the playbook stop condition was reached
- prompt-only or rubric-only calibration is no longer enough evidence for
  promotion
- the blocker is now adjudication quality and disagreement resolution, not
  missing benchmark discipline

## Selective-defer runtime status

The runtime side is technically ready.

Selected manifests:
- main operating point:
  - `artifacts/models/prelim_selected_model_selective_defer_conf49_v1.json`
- higher-API robustness operating point:
  - `artifacts/models/prelim_selected_model_selective_defer_conf54_v1.json`

Runtime posture:
- base local model:
  - `binary_relevance_then_as_v1` for `Irrelevant` vs `Non-Irrelevant`
  - `mpnet_logreg_prelim_v1` for `Actionable` vs `Speculative`
- defer rule:
  - API A on `local_confidence < threshold`
- API A policy:
  - `director/config/api_assistive_policy_heldout_v3_mini_high_output.yaml`

Live smoke result:
- source: `reports/evaluation/selective_defer_runtime_smoke_v1.json`
- rows tested: `3`
- local rows: `2`
- deferred rows: `1`
- metadata columns were written through the classification path

That means the classifier can now run end-to-end under the hybrid posture.

## Promotion decision

Do not treat the classifier lane as final yet.

Reason:
1. the hybrid runtime is technically deployable
2. but human-human IRR v2 is still below gate
3. and the unresolved disagreement mass is still large enough to change the
   benchmark story after adjudication

Operationally:
- yes, the hybrid classifier can now be run on the full sentence universe
- no, it should not yet be treated as the final paper-grade classification
  backbone

## What can proceed now

Safe to proceed:
- keep the two selective-defer manifests as the current deployable candidates
- run bounded smoke or shadow classifications
- prepare downstream code paths and panel merge logic

Not yet safe to promote:
- a canonical full-corpus classification refresh that becomes the paper’s main
  panel input
- a “winner model” claim stronger than “best current automated candidate”

## Next step

Immediate next action:
1. adjudicate the `27` disagreement rows in:
   - `data/labels/v2/irr_boundary_revised_v2_adjudication_sheet.xlsx`
2. recompute IRR status on the adjudicated file
3. compare the selected `0.49` and `0.54` hybrid manifests against the
   adjudicated benchmark
4. only then decide whether to launch the full panel rebuild with the hybrid
   classifier as the new main input

Current recommendation:
- hold the final panel rebuild until adjudication finishes
- if parallel progress is needed, run the `0.49` classifier as a shadow panel
  only
