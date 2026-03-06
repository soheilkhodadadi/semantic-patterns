# Director Quickstart

## Purpose
`semantic_ai_washing.director` builds executable, gate-aware runbooks from canonical roadmap YAML + protocol + iteration history snapshots.

## Initialize
```bash
python -m semantic_ai_washing.director.cli init
```

## Ingest Canonical Context
```bash
python -m semantic_ai_washing.director.cli ingest \
  --protocol docs/director/implementation_protocol_master.md \
  --roadmap-model director/model/roadmap_model.yaml \
  --iteration-log docs/iteration_log.md
```

## Render Canonical Roadmap Markdown
```bash
python -m semantic_ai_washing.director.cli render-roadmap
```

## Generate Plan + Runbook
```bash
python -m semantic_ai_washing.director.cli plan --iteration 1 --phase label-expansion
```

Generated outputs are placed under `director/plans/` and `director/decisions/`.

For phases modeled in `director/model/roadmap_model.yaml`, the runbook is compiled from task groups rather than flat phase command maps.

## Execute Runbook
```bash
python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_<id>.yaml --mode autonomous
```

If execution blocks, a blocker event and ranked recovery options are written to `director/decisions/`.

## Work With Blockers
```bash
# Decide from execution state directly
python -m semantic_ai_washing.director.cli decide \
  --execution-state director/runs/execution_state_<id>.json --auto-select

# Defer a blocker to a later phase with explicit criteria
python -m semantic_ai_washing.director.cli defer \
  --decision-file director/decisions/decision_<id>.json \
  --until-iteration 2 \
  --until-phase full-sample-classification \
  --criteria "Increase labeled pool and satisfy class-floor gate"
```

## Recovery Runbook Flow (Bounded)
```bash
# Generate a bounded recovery runbook (non-canonical Phase 1 recovery profile)
python -m semantic_ai_washing.director.cli plan \
  --iteration 1 \
  --phase label-expansion-recovery

# Execute and inspect status
python -m semantic_ai_washing.director.cli run \
  --runbook director/plans/runbook_<id>.yaml \
  --mode autonomous
python -m semantic_ai_washing.director.cli status

# If blocked, decide/defer explicitly
python -m semantic_ai_washing.director.cli decide \
  --execution-state director/runs/execution_state_<id>.json
python -m semantic_ai_washing.director.cli defer \
  --decision-file director/decisions/decision_<id>.json \
  --until-iteration 2 \
  --until-phase full-classification \
  --criteria "Carry deferred science gate until recovery criteria are met"
```

## IRR Runbook Flow (Phase 2)
```bash
# Generate and execute IRR validation phase runbook
python -m semantic_ai_washing.director.cli plan \
  --iteration 1 \
  --phase irr-validation
python -m semantic_ai_washing.director.cli run \
  --runbook director/plans/runbook_<id>.yaml \
  --mode autonomous
python -m semantic_ai_washing.director.cli status

# Optional strict κ recheck (non-runbook) once rater2 labels are complete
python -m semantic_ai_washing.labeling.compute_irr_metrics \
  --master data/labels/iteration1/irr/irr_subset_master.csv \
  --rater2 data/labels/iteration1/irr/irr_subset_rater2_completed.csv \
  --output-report reports/iteration1/phase2_irr/irr_kappa_report_strict.json \
  --output-confusion reports/iteration1/phase2_irr/irr_confusion_matrix_strict.csv \
  --output-transitions reports/iteration1/phase2_irr/irr_transition_counts_strict.csv \
  --output-status reports/iteration1/phase2_irr/irr_status_strict.json \
  --min-kappa 0.60 \
  --gate-mode strict
```

## Make Targets
```bash
make director-doctor
make director-plan ITER=1 PHASE=label-expansion
make director-status
```

## Continuous Optimization
```bash
python -m semantic_ai_washing.director.cli optimize
python -m semantic_ai_washing.director.cli optimize --iteration 1 --phase irr-validation
```

## Cost and Status
```bash
python -m semantic_ai_washing.director.cli cost-report
python -m semantic_ai_washing.director.cli status
```
