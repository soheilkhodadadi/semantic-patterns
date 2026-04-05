# Adapter Registry V1

## Purpose

This note defines the first canonical registry view for tracked project adapters.

The goal is simple:
- keep the three active project adapters visible in one place
- define the minimum contract fields each adapter must expose
- separate control-plane identity from longer project-specific framing notes

## Canonical contract fields

Each tracked adapter should have:
- `project`: canonical slug
- `mode`: current operating mode
- `purpose`: one-sentence role in the lab
- `framing_note`: project-facing adapter note
- tracked lanes:
  - docs
  - reports
  - processed data
  - doc output
  - figure output
- `local_private_root`: location for non-tracked sensitive materials
- `shared_dependencies`: currently approved shared-core dependencies

## Current registered adapters

### `ai_washing`
- mode: `flagship_publication`
- role: benchmark research adapter and active manuscript lane
- framing note: `docs/projects/ai_washing/adapter_framing_v1.md`

### `eri`
- mode: `incubation_reuse_test`
- role: first serious reuse adapter outside the AI-washing domain
- framing note: `docs/projects/eri/adapter_framing_v1.md`

### `allocationlab`
- mode: `architecture_first`
- role: architecture and synthetic-case adapter for a future decision-system lane
- framing note: `docs/projects/allocationlab/adapter_framing_v1.md`

## Current control-plane source

The canonical code-side contract lives in:
- `src/semantic_ai_washing/labcore/registry/adapters.py`

## Bottom line

The registry does not replace the framing notes.
It gives the lab one compact control-plane object that says what each adapter is, where it lives, and what shared-core pieces it is currently allowed to depend on.
