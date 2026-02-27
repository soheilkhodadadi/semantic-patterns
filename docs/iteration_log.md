# Iteration Log

This file is the persistent execution record across chats/iterations.
Use it as the first context source in every new chat.

## How To Use This Log (Continuous Updates)

Update this file at these points:
- At iteration start: add an iteration header with scope, branches, and acceptance gates.
- After each phase branch is completed: append a short phase entry (branch, deliverables, validations, risks).
- At iteration close: record merge commits, CI status, and carry-forward decisions.

Rules:
- Keep entries concise and factual.
- Record exact commit SHAs and artifact/report paths.
- Record only decisions that affect future work (defaults, thresholds, workflow changes).
- Prefer canonical commands (`python -m semantic_ai_washing...`) in examples.

## Phase Entry Template (Copy/Paste)

```md
### Phase: <name>
- Date:
- Branch:
- Goal:
- Deliverables:
- Validation run:
- Risks/issues encountered:
- Mitigation/resolution:
- Commits:
- CI status:
```

## Iteration 0 (Completed)

### Iteration Scope
- Observability & logging
- Error handling hardening
- Testing & QA baseline
- Documentation & maintainability
- Environment hardening and interpreter guardrails

### Branch and Merge Summary
- `iteration0/observability`
  - feature commit: `b3e86c7`
  - merged to `main`: `ef22fe0`
- `iteration0/error-handling`
  - feature commit: `a31ccdf`
  - merged to `main`: `2a6b2cc`
- `iteration0/testing-qa`
  - feature commit: `5e50e88`
  - merged to `main`: `ad85253`
- `iteration0/documentation`
  - feature commit: `8a2d556`
  - hardening commit: `0fb3342`
  - merged to `main`: `3f1cf33`

### Delivered Outcomes

#### 1) Observability
- Added structured logging in extraction with configurable `--log-level`.
- Replaced extraction `print()` usage with `logging` lifecycle and summary messages.

#### 2) Error Handling
- Hardened extraction/classification boundaries with staged exception handling.
- Startup-critical checks fail fast; per-file failures are logged and skipped.
- Improved merge resilience with safe fallback behavior and contextual logging.

#### 3) Testing & QA
- Added root pytest baseline and test discovery isolation (`tests/` only).
- Added extraction merge regression tests.
- Added CI workflow (`.github/workflows/ci.yml`) running Ruff + pytest on push/PR.

#### 4) Documentation & Maintainability
- Rewrote README to concise canonical quickstart.
- Added `CONTRIBUTING.md` with branch/PR/merge workflow.
- Aligned factual guidance in `AGENTS.md`.
- Improved docstrings in extraction/filter/classification core modules.
- Fixed aggregation drift: supports both current `*_classified.csv` and legacy `*_classified.txt`.
- Added aggregation compatibility tests.

#### 5) Environment Hardening
- Added `make bootstrap` for idempotent `.venv` setup and editable install.
- Added `make doctor` to verify interpreter/pip/import/tooling health and warn on conda base drift.
- Added `.vscode/settings.json` defaulting to `.venv` interpreter + pytest settings.
- Added optional install of `numexpr` and `bottleneck` in bootstrap to suppress recurring pandas warnings.

### Validation Evidence Used in Iteration 0
- `make bootstrap`
- `make doctor`
- `make format`
- `make lint`
- `.venv/bin/pytest -q`
- `.venv/bin/python -c "import semantic_ai_washing; print('ok')"`

### CI Evidence
- Iteration 0 documentation/hardening run: https://github.com/soheilkhodadadi/semantic-patterns/actions/runs/22414665241
- Status: `completed/success`

### Carry-Forward Decisions (For Iterations 1+)
- Standard local environment: repo `.venv` (not conda base).
- Run `make doctor` before lint/tests in local development.
- Keep canonical invocation style: `python -m semantic_ai_washing.<domain>.<module>`.
- Keep phase branches + integration/merge gates with artifact discipline.

### Known Follow-Ups
- Continue phase-based iteration execution with explicit risk gates (IRR, leakage control, artifact versioning) in Iteration 1.

## Iteration 1 (In Progress)

### Iteration Scope
- Expand label quality controls and retrain/evaluate centroid classifier with reproducibility gates.
- Execute phase-by-phase branch workflow through `iteration1/integration`.
- Enforce diagnostics-first gating (Phase 0) before IRR/retraining work.

### Branch Strategy
- Integration branch: `iteration1/integration`
- Phase branch (current): `iteration1/diagnostics-nlp`

### Iteration 1 Global Gates
- IRR gate: Cohen's kappa >= 0.6 before retraining.
- Held-out gate: accuracy >= 0.80 on canonical evaluation.
- Leakage gate: held-out split excluded from centroid computation and threshold tuning.
- Reproducibility gate: artifact metadata includes commit hash, parameters, and input fingerprints.

### Iteration 1 Risk Register (R1-R7)
- R1 label ambiguity between Actionable vs Speculative.
- R2 class imbalance / centroid collapse.
- R3 train/validation/test leakage.
- R4 embedding or scoring non-determinism.
- R5 silent file skips / partial output batches.
- R6 label mapping or centroid metadata mismatch.
- R7 scope creep from hardening before science gates.

### Phase: diagnostics-baseline (start)
- Date: 2026-02-27
- Branch: `iteration1/diagnostics-nlp`
- Goal: Produce reproducible baseline diagnostics report + artifacts for Phase 0 gate.
- Deliverables (planned):
  - `src/semantic_ai_washing/diagnostics/phase0_baseline.py`
  - evaluator structured outputs (metrics/confusion/details)
  - `docs/pipeline_map.md`
  - Phase 0 diagnostics tests
  - artifacts under `reports/iteration1/phase0/`
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `.venv/bin/python -m semantic_ai_washing.diagnostics.phase0_baseline --years 2024 --limit 20 --force --two-stage --rule-boosts --tau 0.07 --eps-irr 0.03 --min-tokens 6 --output-dir reports/iteration1/phase0`
- Risks/issues encountered: none yet
- Mitigation/resolution:
  - R6 correction logged: canonical centroid artifact in repo is `data/validation/centroids_mpnet.json` (not `centroids.mpnet.json`).
- Commits:
  - phase branch commit: `f5c67abdec4a832b7cd06653804c7ebecee2e77d`
  - merge to integration: `6e527369103b622fa3b661e8abb7ef7574adebce`
  - integration log finalization: `db40a3c9fc7e078294b134121853e3359473443e`
- CI status:
  - local validation: pass (`ruff` + `pytest`)
  - remote CI: not run yet for `iteration1/integration` in this session

### Phase: diagnostics-baseline (completed)
- Date: 2026-02-27
- Branch: `iteration1/diagnostics-nlp`
- Goal: Produce reproducible baseline diagnostics report + artifacts for Phase 0 gate.
- Deliverables:
  - Added diagnostics runner: `src/semantic_ai_washing/diagnostics/phase0_baseline.py`
  - Added diagnostics package init: `src/semantic_ai_washing/diagnostics/__init__.py`
  - Added evaluator structured outputs + reusable metrics/confusion helpers:
    - `src/semantic_ai_washing/tests/evaluate_classifier_on_held_out.py`
  - Added canonical pipeline map doc: `docs/pipeline_map.md`
  - Added diagnostics invariants tests: `tests/test_phase0_diagnostics.py`
  - Generated artifacts:
    - `reports/iteration1/phase0/baseline_eval_details.csv`
    - `reports/iteration1/phase0/baseline_eval_metrics.json`
    - `reports/iteration1/phase0/baseline_eval_confusion_matrix.csv`
    - `reports/iteration1/phase0/baseline_batch_distribution.csv`
    - `reports/iteration1/phase0/baseline_failure_taxonomy.csv`
    - `reports/iteration1/phase0/run_metadata.json`
    - `reports/iteration1/phase0/baseline_report.md`
    - `reports/iteration1/phase0/pipeline_map_snapshot.md`
- Validation run:
  - `make bootstrap` -> blocked by local machine prerequisite (`xcodebuild` license not accepted).
  - `make doctor` -> blocked by same Xcode license prerequisite.
  - `make format` -> blocked by same Xcode license prerequisite.
  - Equivalent `.venv` validations executed successfully:
    - `.venv/bin/ruff check --fix`
    - `.venv/bin/ruff format`
    - `.venv/bin/ruff format --check`
    - `.venv/bin/ruff check`
    - `.venv/bin/pytest -q` -> `12 passed`
  - Phase command executed:
    - `.venv/bin/python -m semantic_ai_washing.diagnostics.phase0_baseline --years 2024 --limit 20 --force --two-stage --rule-boosts --tau 0.07 --eps-irr 0.03 --min-tokens 6 --output-dir reports/iteration1/phase0`
  - Gate evidence:
    - coverage mismatch: `0` (`expected=20`, `existing=20`)
    - centroid fingerprint captured (sha256 in `run_metadata.json`)
    - metrics + confusion matrix generated
    - report generated with gate checklist
- Risks/issues encountered:
  - Environment blocker: system Xcode license not accepted prevented all `make` targets.
  - Runtime blocker: live MPNet evaluation/reclassification calls timed out in this environment.
  - R5 risk observed (potential silent partials) during timeout scenarios.
- Mitigation/resolution:
  - Added deterministic coverage guard (`expected` vs `existing` + mismatch count).
  - Added bounded subprocess timeouts and explicit fallback metadata for evaluation/reclassification modes.
  - Logged fallback modes in `run_metadata.json` and `baseline_report.md`.
- Commits:
  - phase branch commit: `f5c67abdec4a832b7cd06653804c7ebecee2e77d`
  - merge to integration: `6e527369103b622fa3b661e8abb7ef7574adebce`
  - integration log finalization: `db40a3c9fc7e078294b134121853e3359473443e`
- CI status:
  - local validation: pass (`.venv/bin/ruff ...`, `.venv/bin/pytest -q`)
  - remote CI: not run yet for `iteration1/integration` in this session
