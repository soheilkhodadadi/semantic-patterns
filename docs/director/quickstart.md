# Director Quickstart

## Purpose
`semantic_ai_washing.director` builds executable, gate-aware runbooks and continuous-planning recommendations from canonical roadmap YAML, protocol summaries, and iteration history.

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

## Optimize Next Work
```bash
python -m semantic_ai_washing.director.cli optimize
python -m semantic_ai_washing.director.cli optimize --iteration 1 --phase label-ops-bootstrap
```

Optimization emits:
- `director/optimization/graph_<id>.json`
- `director/optimization/readiness_<id>.json`
- `director/optimization/recommendation_<id>.json`
- `director/optimization/recommendation_<id>.md`
- optional `director/optimization/proposed_roadmap_patch_<id>.yaml`

## Generate a Runbook
```bash
python -m semantic_ai_washing.director.cli plan --iteration 1 --phase label-ops-bootstrap
```

For phases modeled in `director/model/roadmap_model.yaml`, the runbook is compiled from task groups rather than flat phase command maps.

## Execute a Runbook
```bash
python -m semantic_ai_washing.director.cli run \
  --runbook director/plans/runbook_<id>.yaml \
  --mode autonomous
```

If execution blocks, a blocker event and ranked recovery options are written to `director/decisions/`.

## Decide or Defer
```bash
python -m semantic_ai_washing.director.cli decide \
  --execution-state director/runs/execution_state_<id>.json

python -m semantic_ai_washing.director.cli defer \
  --decision-file director/decisions/decision_<id>.json \
  --until-iteration 2 \
  --until-phase irr-and-adjudication \
  --criteria "Sentence integrity remediation must land before manual IRR work."
```

## Atlas Isolation
Atlas must not run in the repo `.venv`.

Use the configured isolated wrapper path recorded in `director/config/tooling_policy.yaml`. Director doctor validates that the wrapper exists and that `.venv` still matches the expected project interpreter metadata.

## Make Targets
```bash
make director-doctor
make director-plan ITER=1 PHASE=label-ops-bootstrap
make director-status
```

## Validation
```bash
make bootstrap
make doctor
make format
make lint
.venv/bin/pytest -q
python -m semantic_ai_washing.director.cli doctor --strict-secrets --json
```
