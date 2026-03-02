# Director Policy

## Core Rules
- Canonical planning inputs are repo snapshots under `director/snapshots/`.
- External documents/chats are ingested as structured summaries, not committed raw.
- Blockers are escalated with ranked options; no silent continuation past failed gates.
- LLM refinement is budget-limited and optional (`llm_enabled` in `director/config/cost_policy.yaml`).

## Security
- API keys must be provided only via environment variables.
- Tracked-file secret scanning is part of `director doctor` and CI.
- Rotate any exposed keys before enabling LLM refinement.

## Reproducibility
- Plans and runbooks are generated with schema-stable payloads.
- Every planning and execution event writes audit records under `director/runs/`.
- Gate outcomes and blocker decisions are persisted as JSON artifacts.

## Autonomy Boundaries
- `require_explicit_recovery_selection=true` is default.
- Executor halts on gate/policy/security blockers and writes decision scaffolds.
- Resume is allowed only from checkpointed execution state.
