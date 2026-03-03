# Director Policy

## Core Rules
- Canonical planning inputs are repo snapshots under `director/snapshots/`.
- External documents/chats are ingested as structured summaries, not committed raw.
- Blockers are escalated with ranked options; no silent continuation past failed gates.
- LLM refinement is budget-limited and optional (`llm_enabled` in `director/config/cost_policy.yaml`).
- Science blockers can be deferred only with expiry metadata (`until_iteration`, `until_phase`, `criteria`).
- Deferral state is `deferred_blocked`; failed gates are never treated as passed.
- Recovery phases (for example `label-expansion-recovery`) are non-canonical substitutes and must not be interpreted as satisfying the canonical science gate unless explicitly promoted in the iteration log.

## Security
- API keys must be provided only via environment variables.
- Tracked-file secret scanning is part of `director doctor` and CI.
- Rotate any exposed keys before enabling LLM refinement.

## Reproducibility
- Plans and runbooks are generated with schema-stable payloads.
- Every planning and execution event writes audit records under `director/runs/`.
- Gate outcomes and blocker decisions are persisted as JSON artifacts.
- Deferred blockers are tracked in `director/decisions/deferred_*.json`.

## Autonomy Boundaries
- `require_explicit_recovery_selection=true` is default.
- Executor halts on gate/policy/security blockers and writes decision scaffolds.
- Resume is allowed only from checkpointed execution state.

## Data Architecture Direction
- Source filings should be referenced via `SEC_SOURCE_DIR` (no machine-specific committed defaults).
- Transitional `*_ai_sentences.txt` and `*_classified.csv` outputs remain supported while moving toward canonical structured sentence/classification tables.
- Legacy `src/scripts` shims are compatibility-only and targeted for removal by Iteration 3.
