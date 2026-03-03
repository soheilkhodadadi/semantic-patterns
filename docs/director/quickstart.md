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
  --protocol "<path-to-protocol.docx-or-md>" \
  --roadmap "<path-to-roadmap.docx-or-md>" \
  --iteration-log docs/iteration_log.md \
  --atlas-search "Framework for Code Transformation"
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
