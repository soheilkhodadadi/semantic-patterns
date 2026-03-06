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
- Deferred blockers (if any):
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

### Phase: label-expansion (director recovery update)
- Date: 2026-03-03
- Branch: `iteration1/label-expansion-recovery`
- Goal: Resume Phase 1 execution with director runbooks on top of existing label-expansion outputs.
- Deliverables:
  - merged director package into phase recovery branch (`aac143c5a52bc75a01fc135fb67727ab030a7889`)
  - executed director runbook for `Iteration 1 / label-expansion`:
    - `director/plans/runbook_31bb0b5874d88bca.yaml`
    - state: `director/runs/execution_state_31bb0b5874d88bca.json`
    - decision record: `director/decisions/decision_964477c9c2f994a2.json`
  - fixed QA gate exit semantics so failed QA blocks autonomous execution:
    - `src/semantic_ai_washing/labeling/qa_labeled_dataset.py` now exits non-zero on `status=fail`
- Validation run:
  - `make director-plan ITER=1 PHASE=label-expansion`
  - `PATH="$(pwd)/.venv/bin:$PATH" .venv/bin/python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_31bb0b5874d88bca.yaml --mode autonomous`
  - `PATH="$(pwd)/.venv/bin:$PATH" .venv/bin/python -m semantic_ai_washing.director.cli decide --blocker-file /tmp/director_blocker_31bb0b5874d88bca.json --auto-select`
  - `make lint`
  - `.venv/bin/pytest -q` -> `33 passed`
- Gate status:
  - runbook now blocks correctly at QA step with:
    - `class_count_below_min:Actionable=43<60`
    - `class_count_below_min:Speculative=59<60`
    - `class_count_below_min:Irrelevant=51<60`
    - `target_size_mismatch:153!=400`
- Risks/issues encountered:
  - R2 class-balance and sample-size gate remains failed.
  - Runtime ambiguity discovered: prior QA CLI returned exit `0` on failed QA, causing false-positive runbook pass.
- Mitigation/resolution:
  - patched QA CLI to exit `1` when `status != pass`.
  - reran director execution to confirm blocker behavior and decision escalation path.
- Commits:
  - `aac143c5a52bc75a01fc135fb67727ab030a7889` (merge director foundation into recovery branch)
  - `c2027c485ea7253356b7af9f66e18d15ec3cd3e1` (fix QA non-zero exit on failure)
- CI status:
  - local lint/tests pass (`make lint`, `.venv/bin/pytest -q`)
  - remote CI pending for `iteration1/label-expansion-recovery`


## Director Foundation (In Progress)

### Phase: director-foundation (start)
- Date: 2026-03-02
- Branch: `director/foundation`
- Goal: Build reusable autonomous director package that turns roadmap/protocol/iteration history into executable runbooks with gate checks and blocker escalation.
- Deliverables (planned):
  - `semantic_ai_washing.director` package (`core`, `adapters`, `policies`, CLI)
  - repo config/snapshot workspace under `director/`
  - director docs + tests + CI integration + Makefile targets
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `make director-doctor`
  - `make director-plan`
  - `make director-status`
- Risks/issues encountered (initial):
  - `.venv` drift from Atlas CLI bootstrap caused missing `pip` in `.venv`.
- Mitigation/resolution:
  - Rebuilt `.venv` with `python3.9 -m venv --clear .venv` and completed bootstrap.
- Commits:
  - `3bdbf33ef0f4f287f57acc33d0b5f8f9af808f50` (director package foundation + docs/tests/CI integration)
  - `b76975af857b3584e87c57fd95a90d017e4206c7` (iteration log evidence finalization)
  - `4155a6ebdf90727fef26712c811e1ed02d4ef27f` (director test hardening for secret scan compatibility)
- CI status:
  - local validation pass (`make bootstrap`, `make doctor`, `make format`, `make lint`, `.venv/bin/pytest -q`)
  - director local validation pass (`make director-doctor`, `make director-plan`, `make director-status`)
  - remote CI pending

### Phase: director-foundation (execution update)
- Date: 2026-03-02
- Branch: `director/foundation`
- Goal: Implement autonomous planning/execution director in parallel with Iteration 1 science branches.
- Deliverables implemented:
  - Package:
    - `src/semantic_ai_washing/director/__init__.py`
    - `src/semantic_ai_washing/director/__main__.py`
    - `src/semantic_ai_washing/director/cli.py`
    - `src/semantic_ai_washing/director/schemas.py`
    - `src/semantic_ai_washing/director/core/*`
    - `src/semantic_ai_washing/director/adapters/*`
    - `src/semantic_ai_washing/director/policies/*`
  - Director workspace defaults:
    - `director/config/project_profile.yaml`
    - `director/config/autonomy_policy.yaml`
    - `director/config/cost_policy.yaml`
    - `director/snapshots/protocol_summary.json`
    - `director/snapshots/roadmap_summary.json`
    - `director/snapshots/iteration_state.json`
    - `director/README.md`
  - Docs:
    - `docs/director/quickstart.md`
    - `docs/director/policy.md`
  - Tests:
    - `tests/test_director_core.py`
    - `tests/test_director_cli.py`
  - Repo integration:
    - `Makefile` (`director-doctor`, `director-plan`, `director-status`)
    - `.github/workflows/ci.yml` director job
    - `setup.cfg` dependencies and `director` console entrypoint
- Validation run:
  - `make bootstrap` -> pass (after `.venv` rebuild)
  - `make doctor` -> pass
  - `make format` -> pass
  - `make lint` -> pass
  - `.venv/bin/pytest -q` -> `23 passed`
  - `make director-doctor` -> pass
  - `make director-plan ITER=1 PHASE=label-expansion` -> pass
  - `make director-status` -> pass
- Risks/issues encountered:
  - Initial editable install hung when pip build isolation overlapped with concurrent bootstrap runs.
  - Python 3.9 + Pydantic field evaluation required `Optional[...]` annotations in schemas.
- Mitigation/resolution:
  - Killed overlapping pip processes, re-ran install with stabilized environment.
  - Converted schema optional unions to `Optional[...]` for Python 3.9 compatibility.
- Commits:
  - `3bdbf33ef0f4f287f57acc33d0b5f8f9af808f50` (director package foundation + docs/tests/CI integration)
  - `b76975af857b3584e87c57fd95a90d017e4206c7` (iteration log evidence finalization)
  - `4155a6ebdf90727fef26712c811e1ed02d4ef27f` (director test hardening for secret scan compatibility)
- CI status:
  - local validation pass (`make bootstrap`, `make doctor`, `make format`, `make lint`, `.venv/bin/pytest -q`)
  - director local validation pass (`make director-doctor`, `make director-plan`, `make director-status`)
  - remote CI pending

### Phase: stabilization-main-director-i1 (start)
- Date: 2026-03-03
- Branch: `stabilize/main-director-i1`
- Goal: Merge director foundation and useful Iteration 1 code/docs into a stable main-ready branch while deferring unresolved science blockers correctly.
- Deliverables (planned):
  - merge `director/foundation` + selected `iteration1/label-expansion-recovery` code/docs
  - exclude generated phase artifacts from `main` (`data/labels/iteration1/*`, `reports/iteration1/phase1/*`)
  - harden director blocker handling, deferral, parsing, and runbook gating
  - add roadmap/protocol canonical in-repo sources for director ingestion
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `make director-doctor`
  - `make director-plan ITER=1 PHASE=label-expansion`
- Risks/issues encountered:
  - mixed processed data layout can cause duplicate file accounting across root/year folders.
- Mitigation/resolution:
  - add mixed-layout warnings and basename de-duplication in recursive scans.
- Deferred blockers (if any):
  - Phase 1 size/class-balance blocker remains deferred to later iteration phases with explicit deferral metadata.
- Commits:
  - pending
- CI status:
  - pending

### Phase: stabilization-main-director-i1 (execution update)
- Date: 2026-03-03
- Branch: `stabilize/main-director-i1`
- Goal: Stabilize main-bound branch with director and Iteration 1 code/docs while preserving truthful blocker semantics.
- Deliverables implemented:
  - merged `director/foundation`
  - imported selected Iteration 1 code/docs only:
    - `src/semantic_ai_washing/labeling/*`
    - `tests/test_labeling_phase1.py`
    - `docs/labeling_protocol.md`
    - `docs/iteration_log.md` updates
  - intentionally excluded generated artifacts from main-bound branch:
    - `data/labels/iteration1/*`
    - `reports/iteration1/phase1/*`
  - director hardening:
    - `decide --execution-state` support
    - explicit `defer` command + deferred blocker records
    - validation-gate wiring to actual validation step outcomes
    - execution `cwd` normalization and command environment support
    - iteration-log parser cleanup (template/codeblock noise removed)
    - structured roadmap iteration extraction in snapshot ingestion
  - canonical in-repo director inputs added:
    - `docs/director/implementation_protocol_master.md`
    - `docs/director/roadmap_master.md`
    - `docs/director/data_architecture_target.md`
- Validation run:
  - `make bootstrap` -> pass
  - `make doctor` -> pass (with expected warning: conda base active while `.venv` is canonical)
  - `make format` -> pass
  - `make lint` -> pass
  - `.venv/bin/pytest -q` -> `37 passed`
  - `make director-doctor` -> pass
  - `make director-plan ITER=1 PHASE=label-expansion` -> pass (`runbook_4754d9fe102366cd.yaml`)
  - `make director-status` -> pass
  - `.venv/bin/python -m semantic_ai_washing.director.cli decide --execution-state director/runs/execution_state_31bb0b5874d88bca.json` -> pass (decision file generated)
  - `.venv/bin/python -m semantic_ai_washing.director.cli defer --decision-file director/decisions/decision_8bbeeba8186ff739.json --until-iteration 2 --until-phase full-classification --criteria "Resume after Phase 1 label expansion blockers are addressed"` -> pass
  - execution state `director/runs/execution_state_31bb0b5874d88bca.json` transitioned to `deferred_blocked` (not `passed`)
- Risks/issues encountered:
  - prior director snapshots referenced personal absolute docx paths.
  - long-running sampling step in `build_labeling_sample` can stall autonomous full run in local environments with large corpora.
- Mitigation/resolution:
  - switched committed snapshots to in-repo canonical source documents.
  - used explicit defer-with-expiry workflow to preserve truthful blocker semantics while allowing forward progress.
- Deferred blockers (if any):
  - unresolved Phase 1 dataset size/class-balance gate remains deferred; not marked pass.
  - active deferred record: `director/decisions/deferred_eedb6fbadba43363.json` (`until_iteration=2`, `until_phase=full-classification`).
- Commits:
  - `1a88f3fd2111f0f98c88db1eb27a1c43034f618d` (stabilization implementation: director hardening + Iteration 1 code/docs integration)
- CI status:
  - local validation pass (`make bootstrap`, `make doctor`, `make format`, `make lint`, `.venv/bin/pytest -q`, `make director-doctor`, `make director-plan`, `make director-status`)
  - remote CI pending

### Phase: stabilization-main-director-i1 (closeout)
- Date: 2026-03-03
- Branch: `main`
- Goal: Complete stabilization merge and publish a clean main baseline with truthful deferred blocker handling.
- Deliverables:
  - merged `stabilize/main-director-i1` into `main`
  - published director package, labeling package, roadmap/protocol/data-architecture docs, and Iteration 1 logging/rubric updates
  - kept generated Phase 1 science artifacts out of tracked `main`
- Validation run:
  - source branch validation evidence preserved in prior entry (bootstrap/doctor/format/lint/pytest/director checks)
  - post-merge branch status: clean (`git status`)
- Risks/issues encountered:
  - unresolved Phase 1 science gate remains deferred and must not be interpreted as pass.
- Mitigation/resolution:
  - deferred blocker records + `deferred_blocked` execution semantics preserved in director state/decision flow.
- Deferred blockers (if any):
  - `31bb0b5874d88bca-step-004-runtime` deferred to `iteration=2`, `phase=full-classification` under explicit criteria.
- Commits:
  - `063860eb48251d2a3d4afe0e7ec6f6742ad075dc` (merge `stabilize/main-director-i1` into `main`)
  - source commits included: `1a88f3fd2111f0f98c88db1eb27a1c43034f618d`, `e80fbd3b6ad2d9de109770ac0a56d5f62f8e64c4`
- CI status:
  - published to `origin/main`
  - remote CI pending

### Phase: label-expansion-recovery (start)
- Date: 2026-03-03
- Branch: `main`
- Goal: Generate and execute a bounded non-stalling recovery runbook for Iteration 1 Phase 1 while preserving canonical strict-gate semantics.
- Deliverables (planned):
  - add bounded sampler controls (`--years`, `--max-ai-files`)
  - add recovery phase profile in director config (`iteration1/label-expansion-recovery`)
  - add planner timeout overrides (`snapshot=300`, `validation=1800`, `phase=1200`)
  - execute fresh recovery runbook and capture explicit block/decision/deferral evidence
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `make director-plan ITER=1 PHASE=label-expansion-recovery`
  - `.venv/bin/python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_<id>.yaml --mode autonomous`
  - `make director-status`
- Risks/issues encountered:
  - recovery sample may remain below target-size even with bounded file scope.
- Mitigation/resolution:
  - preserve strict failure semantics (`blocked`/`deferred_blocked`) and defer explicitly if unresolved.
- Deferred blockers (if any):
  - pending run outcome
- Commits:
  - `3524a0fda9326c355729f4f0684f83f6fe6697ce` (bounded recovery profile + timeout controls + tests/docs/log updates)
- CI status:
  - published to `origin/main`
  - remote CI pending

### Phase: label-expansion-recovery (execution update)
- Date: 2026-03-03
- Branch: `main`
- Goal: Execute bounded recovery runbook and verify non-stalling behavior with explicit blocker/defer path.
- Deliverables implemented:
  - sampler enhancements:
    - `src/semantic_ai_washing/labeling/build_labeling_sample.py`
    - new args: `--years`, `--max-ai-files`
    - summary fields: `years_filter`, `max_ai_files`, `ai_files_considered`, `ai_files_processed`, `ai_files_skipped_by_year_filter`
  - director timeout/profile enhancements:
    - `director/config/project_profile.yaml`:
      - `step_timeout_overrides: {snapshot_seconds: 300, validation_seconds: 1800, phase_seconds: 1200}`
      - new recovery phase command map + artifact map for `iteration1/label-expansion-recovery`
    - `src/semantic_ai_washing/director/core/planner.py` uses timeout overrides for snapshot/validation/phase step groups
  - docs updates:
    - `docs/director/quickstart.md` (recovery plan/run/decide/defer flow)
    - `docs/director/policy.md` (non-canonical recovery phase rule)
  - test coverage additions:
    - `tests/test_labeling_phase1.py` (year filter + file cap behaviors)
    - `tests/test_director_core.py` (timeout override wiring, recovery-vs-canonical phase command selection, timeout-block behavior)
- Validation run:
  - `make bootstrap` -> pass
  - `make doctor` -> pass (with expected conda base warning)
  - `make format` -> pass
  - `make lint` -> pass
  - `.venv/bin/pytest -q` -> `41 passed`
  - `make director-plan ITER=1 PHASE=label-expansion-recovery` -> pass
    - runbook: `director/plans/runbook_115d7b0ec26e20bc.yaml`
  - runbook execution:
    - `.venv/bin/python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_115d7b0ec26e20bc.yaml --mode autonomous`
    - step results: validation steps passed; `step-007` completed in bounded runtime; `step-009` blocked with QA fail
    - state: `director/runs/execution_state_115d7b0ec26e20bc.json`
    - blocker: `115d7b0ec26e20bc-step-009-runtime` (target size mismatch)
    - decision scaffold: `director/decisions/decision_cde09cd3d28fb567.json`
  - blocker handling:
    - `.venv/bin/python -m semantic_ai_washing.director.cli decide --execution-state director/runs/execution_state_115d7b0ec26e20bc.json` -> pass (decision file: `director/decisions/decision_e3fdeaf10fbd4fcd.json`)
    - `.venv/bin/python -m semantic_ai_washing.director.cli defer --decision-file director/decisions/decision_cde09cd3d28fb567.json --until-iteration 2 --until-phase full-classification --criteria "Increase sampled supply and align recovery target-size policy before retry"` -> pass
    - deferred record: `director/decisions/deferred_51a4c7ed8c613dc7.json`
    - final execution state transitioned to `deferred_blocked`
- Risks/issues encountered:
  - recovery QA failed on `target_size_mismatch:121!=220` (class floor not the blocker in this run).
- Mitigation/resolution:
  - preserved explicit block semantics and recorded defer-with-expiry metadata for continuation.
- Deferred blockers (if any):
  - active: `115d7b0ec26e20bc-step-009-runtime` deferred to `iteration=2`, `phase=full-classification`.
  - canonical strict `iteration1/label-expansion` (`target-size=400`, `class>=60`) remains deferred and not passed.
- Commits:
  - `3524a0fda9326c355729f4f0684f83f6fe6697ce` (bounded recovery profile + timeout controls + tests/docs/log updates)
- CI status:
  - local validation pass
  - published to `origin/main`
  - remote CI pending

### Phase: irr-validation (start)
- Date: 2026-03-03
- Branch: `iteration1/irr-validation`
- Goal: Implement Phase 2 IRR gate workflow (subset prep, second-rater template, κ computation, adjudication scaffolding) with director-gated infrastructure-mode execution.
- Deliverables (planned):
  - `src/semantic_ai_washing/labeling/prepare_irr_subset.py`
  - `src/semantic_ai_washing/labeling/compute_irr_metrics.py`
  - `src/semantic_ai_washing/labeling/adjudicate_irr_labels.py`
  - director profile wiring for `iteration1/irr-validation`
  - docs + tests + runbook evidence
- Validation run (planned):
  - `make bootstrap`
  - `make doctor`
  - `make format`
  - `make lint`
  - `.venv/bin/pytest -q`
  - `make director-plan ITER=1 PHASE=irr-validation`
  - `.venv/bin/python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_<id>.yaml --mode autonomous`
  - `make director-status`
- Risks/issues encountered:
  - Manual second-rater file may be unavailable during this run; strict κ gate may remain deferred.
- Mitigation/resolution:
  - Use infrastructure-mode IRR execution that emits explicit `irr_status.json` deferral state.
- Deferred blockers (if any):
  - pending
- Commits:
  - pending
- CI status:
  - pending

### Phase: irr-validation (execution update)
- Date: 2026-03-03
- Branch: `iteration1/irr-validation`
- Outcome:
  - director runbook execution passed in infrastructure mode.
  - strict IRR science gate (`kappa >= 0.6`) remains deferred pending manual second-rater completion.
- Validation run:
  - `make bootstrap` -> pass
  - `make doctor` -> pass (with expected conda base warning)
  - `make format` -> pass
  - `make lint` -> pass
  - `.venv/bin/pytest -q` -> `46 passed`
  - `make director-plan ITER=1 PHASE=irr-validation` -> pass
    - runbook: `director/plans/runbook_e332495a856a965e.yaml`
    - plan: `director/plans/plan_e332495a856a965e.md`
    - decision scaffold: `director/decisions/decision_e332495a856a965e.json`
  - runbook execution:
    - `.venv/bin/python -m semantic_ai_washing.director.cli run --runbook director/plans/runbook_e332495a856a965e.yaml --mode autonomous` -> pass
    - execution state: `director/runs/execution_state_e332495a856a965e.json`
    - execution result: `director/runs/execution_result_e332495a856a965e.json`
    - status: `passed` (`steps_passed=10`, `step_count=10`)
  - `make director-status` -> pass
- Artifacts generated:
  - `data/labels/iteration1/irr/irr_subset_master.csv`
  - `data/labels/iteration1/irr/irr_subset_rater2_blinded.csv`
  - `data/labels/iteration1/irr/irr_adjudication_sheet.csv`
  - `reports/iteration1/phase2_irr/irr_subset_sampling_report.json`
  - `reports/iteration1/phase2_irr/irr_kappa_report.json`
  - `reports/iteration1/phase2_irr/irr_status.json` (`status=pending_rater2`, `gate_result=deferred`)
  - `reports/iteration1/phase2_irr/adjudication_status.json` (`status=pending_rater2`)
- Risks/issues encountered:
  - second-rater file `data/labels/iteration1/irr/irr_subset_rater2_completed.csv` is not yet available.
- Mitigation/resolution:
  - infrastructure mode emitted explicit deferred IRR status artifacts and did not falsely mark strict κ pass.
  - strict recheck command is documented in `docs/director/quickstart.md` and must be run after rater2 completion.
- Deferred blockers (if any):
  - no director runtime blocker in this run.
  - scientific gate remains deferred: clear when strict IRR run reports `kappa >= 0.6`.
- Commits:
  - `50ef8f3a801f27828f80da9f1544f79037d8bf0e` (Phase 2 IRR tooling + director profile/tests/docs + phase2 report evidence)
- CI status:
  - local validation pass (`make bootstrap`, `make doctor`, `make format`, `make lint`, `.venv/bin/pytest -q`)
  - branch pushed: `origin/iteration1/irr-validation`

## Director Extension (In Progress)

### Phase: algorithmic-roadmap-control-loop (execution update)
- Date: 2026-03-05
- Branch: `iteration1/irr-validation`
- Goal: Convert director planning from prose-driven phase maps to a canonical YAML task model with deterministic readiness analysis, optimization, and proposal-only resequencing.
- Deliverables implemented:
  - canonical planning sources:
    - `director/model/roadmap_model.yaml`
    - `director/model/remediation_library.yaml`
  - generated roadmap/doc outputs:
    - `docs/director/roadmap_master.md` (generated from canonical YAML)
    - `docs/director/roadmap_model_spec.md`
    - `docs/director/continuous_planning.md`
  - new director core modules:
    - `src/semantic_ai_washing/director/core/roadmap_model.py`
    - `src/semantic_ai_washing/director/core/task_graph.py`
    - `src/semantic_ai_washing/director/core/sensors.py`
    - `src/semantic_ai_washing/director/core/readiness.py`
    - `src/semantic_ai_washing/director/core/optimizer.py`
    - `src/semantic_ai_washing/director/core/render.py`
  - schema and planner/executor extensions:
    - `RoadmapModel`, `IterationSpec`, `PhaseSpec`, `TaskSpec`, `ArtifactSpec`, `ConditionSpec`
    - task-graph planning for modeled phases
    - `manual` blocker type + `waiting_manual` step state
    - explicit planner failure for unmigrated phases that have neither modeled tasks nor fallback commands
  - CLI/extensions:
    - `python -m semantic_ai_washing.director.cli render-roadmap`
    - `python -m semantic_ai_washing.director.cli optimize`
    - `ingest --roadmap-model ...`
  - Iteration 1 modeled at task level in canonical YAML:
    - `diagnostics-nlp`
    - `label-expansion`
    - `irr-validation`
    - `centroid-retraining`
    - `classifier-calibration`
    - `batch-classification-2021-2024`
  - fallback compatibility retained for unmigrated recovery phase:
    - `director/config/project_profile.yaml` preserves `iteration1/label-expansion-recovery` command/artifact maps
- Validation run:
  - `.venv/bin/python -m semantic_ai_washing.director.cli render-roadmap` -> pass
    - output: `docs/director/roadmap_master.md`
  - `.venv/bin/python -m semantic_ai_washing.director.cli ingest --protocol docs/director/implementation_protocol_master.md --roadmap-model director/model/roadmap_model.yaml --iteration-log docs/iteration_log.md` -> pass
    - snapshots refreshed:
      - `director/snapshots/protocol_summary.json`
      - `director/snapshots/roadmap_summary.json`
      - `director/snapshots/iteration_state.json`
  - `.venv/bin/python -m semantic_ai_washing.director.cli optimize --iteration 1 --phase irr-validation` -> pass
    - optimization report id: `d3700831-313a6972`
    - outputs:
      - `director/optimization/graph_d3700831-313a6972.json`
      - `director/optimization/readiness_d3700831-313a6972.json`
      - `director/optimization/recommendation_d3700831-313a6972.json`
      - `director/optimization/recommendation_d3700831-313a6972.md`
      - `director/optimization/proposed_roadmap_patch_d3700831-313a6972.yaml`
  - `.venv/bin/python -m semantic_ai_washing.director.cli plan --iteration 1 --phase irr-validation` -> pass
    - runbook: `director/plans/runbook_bfa7a63ec1affa51.yaml`
  - `.venv/bin/python -m semantic_ai_washing.director.cli plan --iteration 1 --phase label-expansion-recovery` -> pass
    - runbook: `director/plans/runbook_db6d75490b63bd50.yaml`
  - `make doctor` -> pass (with expected conda base warning)
  - `make format` -> pass
  - `make lint` -> pass
  - `.venv/bin/pytest -q` -> `53 passed`
- Risks/issues encountered:
  - initial YAML migration regression removed fallback phase commands for unmigrated phases, allowing validation-only runbooks to be generated for `label-expansion-recovery`.
  - optimizer surfaced a real upstream blocker for IRR source quality rather than manual-rating readiness.
- Mitigation/resolution:
  - restored fallback command/artifact maps for `iteration1/label-expansion-recovery`.
  - changed planner behavior to fail loudly when a phase has neither modeled tasks nor fallback commands.
  - added regression coverage for both the loud-fail behavior and fallback recovery planning.
  - optimizer now truthfully reroutes away from IRR when quality preconditions fail.
- Deferred blockers (if any):
  - `iteration1.shared.audit_sentence_integrity` is `blocked_quality` for `iteration1/irr-validation`.
  - current evidence from `director/optimization/readiness_d3700831-313a6972.json`:
    - `sentence_fragment_rate_lte` actual = `1.0`
    - `rows = 121`
    - `fragment_rows = 121`
  - recommended remediation tasks:
    - `common.remediate_fragmented_sentences`
    - `common.resample_from_clean_sentence_pool`
  - strict IRR progression should not resume until sentence-quality remediation is addressed or formally deferred with updated policy.
- Commits:
  - pending local commit (implementation validated in working tree; commit SHA to be recorded after commit)
- CI status:
  - local validation pass (`render-roadmap`, `ingest --roadmap-model`, `optimize`, `plan`, `make doctor`, `make format`, `make lint`, `.venv/bin/pytest -q`)
  - remote CI pending commit/push
