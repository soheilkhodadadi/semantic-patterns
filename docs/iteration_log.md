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

### Phase: label-expansion (start)
- Date: 2026-02-27
- Branch: `iteration1/label-expansion`
- Goal: Expand labeled dataset to 400 rows with leakage-safe dedupe, QA gates, stable IDs, and labeling rubric.
- Deliverables (planned):
  - `src/semantic_ai_washing/labeling/__init__.py`
  - `src/semantic_ai_washing/labeling/ff12_mapping.py`
  - `src/semantic_ai_washing/labeling/build_labeling_sample.py`
  - `src/semantic_ai_washing/labeling/dedupe_labeled_sentences.py`
  - `src/semantic_ai_washing/labeling/qa_labeled_dataset.py`
  - `docs/labeling_protocol.md`
  - phase artifacts under `data/labels/iteration1/` and `reports/iteration1/phase1/`
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `.venv/bin/python -m semantic_ai_washing.labeling.build_labeling_sample ...`
  - `.venv/bin/python -m semantic_ai_washing.labeling.dedupe_labeled_sentences ...`
  - `.venv/bin/python -m semantic_ai_washing.labeling.qa_labeled_dataset ...`
- Risks/issues encountered (so far):
  - R3 leakage risk confirmed by overlap diagnostics between labeled base and held-out.
- Mitigation/resolution:
  - Freeze `data/validation/held_out_sentences.csv` and enforce hard overlap exclusion in sampling and QA.
- Commits:
  - `c00769bca2115b6f9b4f52d4f2a80c80cc2de338` (phase implementation + artifacts)
- CI status:
  - local fallback validation pass (`python3.9` + `PYTHONPATH=src`): Ruff + pytest
  - canonical `.venv`/`make` path blocked by host prerequisites

### Phase: label-expansion (execution update)
- Date: 2026-02-27
- Branch: `iteration1/label-expansion`
- Goal: Deliver leakage-safe label expansion tooling, rubric, and QA gates for a 400-row target dataset.
- Deliverables implemented:
  - New package + CLIs:
    - `src/semantic_ai_washing/labeling/__init__.py`
    - `src/semantic_ai_washing/labeling/common.py`
    - `src/semantic_ai_washing/labeling/ff12_mapping.py`
    - `src/semantic_ai_washing/labeling/build_labeling_sample.py`
    - `src/semantic_ai_washing/labeling/dedupe_labeled_sentences.py`
    - `src/semantic_ai_washing/labeling/qa_labeled_dataset.py`
  - New rubric doc:
    - `docs/labeling_protocol.md`
  - New tests:
    - `tests/test_labeling_phase1.py`
  - Phase artifacts generated:
    - `data/labels/iteration1/base_labeled_nonleaky.csv`
    - `data/labels/iteration1/labeling_sheet_for_manual.csv`
    - `data/labels/iteration1/labeling_sheet_completed.csv`
    - `data/labels/iteration1/expanded_labeled_sentences_preqa.csv`
    - `data/labels/iteration1/uncertain_rows.csv`
    - `data/labels/iteration1/label_conflicts.csv`
    - `data/labels/iteration1/dataset_metadata.json`
    - `reports/iteration1/phase1/sampling_summary.json`
    - `reports/iteration1/phase1/dedupe_report.json`
    - `reports/iteration1/phase1/qa_report.json`
    - `reports/iteration1/phase1/leakage_overlap_report.csv`
- Validation run:
  - Required make targets attempted and blocked by local machine prerequisite:
    - `make bootstrap` -> blocked (`xcodebuild` license not accepted)
    - `make doctor` -> blocked (`xcodebuild` license not accepted)
    - `make format` -> blocked (`xcodebuild` license not accepted)
    - `make lint` -> blocked (`xcodebuild` license not accepted)
  - `.venv/bin/pytest -q` attempted and hung due local `.venv` runtime issue (Rosetta/code-signature attachment failure while importing numeric stack).
  - Fallback validation executed with `python3.9` + `PYTHONPATH=src`:
    - `python3.9 -m ruff check --fix ...`
    - `python3.9 -m ruff format ...`
    - `python3.9 -m ruff format --check ...`
    - `python3.9 -m ruff check ...`
    - `PYTHONPATH=src python3.9 -m pytest -q` -> `22 passed`
  - Phase commands executed:
    - `PYTHONPATH=src python3.9 -m semantic_ai_washing.labeling.build_labeling_sample ... --target-total 400 ...`
    - `PYTHONPATH=src python3.9 -m semantic_ai_washing.labeling.dedupe_labeled_sentences ...`
    - `PYTHONPATH=src python3.9 -m semantic_ai_washing.labeling.qa_labeled_dataset ...`
- Gate status:
  - `qa_report.json` status: `fail`
  - Violations:
    - `class_count_below_min:Actionable=43<60`
    - `class_count_below_min:Speculative=59<60`
    - `class_count_below_min:Irrelevant=51<60`
    - `target_size_mismatch:153!=400`
  - Leakage checks:
    - base labeled overlap removed: `99`
    - final leakage overlap count: `0`
- Repo-state correction logged:
  - With current repository corpus and frozen held-out policy, `target_total=400` is infeasible in this phase run:
    - candidate pool after leakage + dedupe filters: `130`
    - base non-leaky labeled rows: `24`
    - merged pre-QA rows: `153`
  - This supersedes any prior assumption that 400 rows were immediately attainable from current in-repo candidates.
- Risks/issues encountered:
  - R2 class imbalance remained after leakage-safe sampling.
  - R3 leakage prevented via hard exclusion, reducing available sample volume.
  - R7 scope control maintained (no retraining/calibration introduced).
  - Environment blockers impacted canonical `make`/`.venv` validation path.
- Mitigation/resolution:
  - Added hard-fail QA gates + explicit reports for size/balance/leakage.
  - Persisted metadata/fingerprints for reproducibility.
  - Captured infeasibility evidence in artifacts for next planning decision.
- Commits:
  - `c00769bca2115b6f9b4f52d4f2a80c80cc2de338` (phase implementation + artifacts)
- CI status:
  - local fallback validation pass (`python3.9` + `PYTHONPATH=src`): Ruff + pytest
  - canonical `.venv`/`make` path blocked by host prerequisites
