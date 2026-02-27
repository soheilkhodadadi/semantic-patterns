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
