# Director Quickstart

## Purpose
`semantic_ai_washing.director` builds executable, gate-aware runbooks from roadmap + protocol + iteration history snapshots.

## Initialize
```bash
python -m semantic_ai_washing.director.cli init
```

## Ingest Canonical Context
```bash
python -m semantic_ai_washing.director.cli ingest \
  --protocol docs/director/implementation_protocol_master.md \
  --roadmap docs/director/roadmap_master.md \
  --iteration-log docs/iteration_log.md
```

## Generate Plan + Runbook
```bash
python -m semantic_ai_washing.director.cli plan --iteration 1 --phase label-expansion
```

Generated outputs are placed under `director/plans/` and `director/decisions/`.

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

## Make Targets
```bash
make director-doctor
make director-plan ITER=1 PHASE=label-expansion
make director-status
```

## Cost and Status
```bash
python -m semantic_ai_washing.director.cli cost-report
python -m semantic_ai_washing.director.cli status
```
