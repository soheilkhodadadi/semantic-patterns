# Director Policy

## Core Rules
- `director/model/roadmap_model.yaml` is the canonical planning source.
- `docs/director/roadmap_master.md` is generated from canonical YAML and must stay hash-synchronized.
- Canonical planning inputs are repo snapshots under `director/snapshots/`.
- External documents and chats are ingested as structured summaries, not committed raw.
- Blockers are escalated with ranked options; no silent continuation past failed gates.
- The optimizer is proposal-only. It may emit cross-iteration resequencing patches, but it may not rewrite the canonical roadmap automatically.
- Manual tasks are first-class and must block truthfully when required outputs are absent.
- Historical and superseded phases remain in the roadmap for traceability and are excluded from next-work ranking and execution.
- Every iteration ends with an explicit `review-and-replan` phase.
- Iterations 2-5 start with `kickoff-and-preflight`.
- Next-iteration work is not authorized until the previous iteration review is approved.

## Scientific Policies
- `held_out_sentences.csv` is frozen evaluation-only.
- IRR is human-human only. Model-vs-label agreement is not IRR.
- Labeling and adjudication must not peek at downstream outcomes.
- Retraining requires a frozen split registry.
- Sentence-quality gates must pass before manual labeling and IRR work.
- Recovery or infrastructure phases do not silently satisfy canonical science gates.

## API Policy
- OpenAI API output is assistive-only until a later benchmark gate explicitly promotes a new mode.
- Assistive usage may support triage, rubric checks, bounded dry-runs, or optional prelabels.
- API outputs must not become canonical labels by default.
- Cost and usage telemetry are required when API support is enabled.
- A bounded live smoke test is allowed for `iteration1/rubric-and-api-bootstrap` and must issue exactly one real request.
- A failed live smoke test blocks the phase.
- A successful smoke test does not authorize batch assistive prelabeling or canonical label promotion.

## Tooling Policy
- Atlas must run in an isolated environment outside the repo `.venv`.
- Repo-root `uv run` is forbidden for Atlas tasks.
- `director/config/tooling_policy.yaml` defines the expected wrapper and repo `.venv` policy checks.

## Reproducibility
- Plans and runbooks are generated with schema-stable payloads.
- Every planning and execution event writes audit records under `director/runs/`.
- Gate outcomes and blocker decisions are persisted as JSON artifacts.
- Deferred blockers are tracked in `director/decisions/deferred_*.json`.
- Iteration reviews, approvals, kickoff checks, branch plans, and starter prompts are persisted under `director/reviews/`.

## Branch Lifecycle
- Standard integration branch:
  - `iteration{iteration_id}/integration`
- Standard work branch:
  - `iteration{iteration_id}/{slug}`
- Stable merge target:
  - `main`
- Default iteration-boundary practice:
  - approved review
  - optional roadmap patch apply
  - integration-branch closeout validation
  - merge to `main`
  - new-chat starter prompt for the next iteration

## Data Architecture Direction
- Source filings are referenced via `SEC_SOURCE_DIR`; machine-specific committed defaults are forbidden.
- Canonical sentence, label, classification, and panel layers move to Parquet-backed tables.
- CSV is retained for review/export and bounded manual workflows.
- Transitional txt/csv flows remain supported only during migration.
