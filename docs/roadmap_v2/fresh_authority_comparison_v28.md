# Fresh Authority Comparison V28

## Purpose

Choose Queue V25 after Queue V24 completed cleanly.

## Candidates compared

1. `hygiene.remaining_script_consumer_followon`
2. `semantic_director.utility_boundary_cleanup`

## Candidate A: `hygiene.remaining_script_consumer_followon`

Representative surfaces:
- `src/data/clean_compustat.py`
- `src/data/clean_crsp.py`
- `src/data/clean_sec.py`
- `src/data/download_compustat.py`
- `src/data/download_crsp.py`
- `src/data/download_sec.py`

Why it is attractive:
- the historical data utility lane is now clearly marked as deprecated at both
  the source-module and flat-consumer levels
- another hygiene pass could continue nibbling at the same late-stage surface

Risk shape:
- medium
- after Queue V24, the remaining leverage here is weaker
- another queue in the same lane now risks over-optimizing wording instead of
  materially clarifying the repo

## Candidate B: `semantic_director.utility_boundary_cleanup`

Representative surfaces:
- `semantic_director.decision`
- `semantic_director.documents`
- `semantic_director.iteration_log`
- `semantic_director.sensors`
- `semantic_director.validation_assets`
- `semantic_director.script_inventory`
- `semantic_director.api_bootstrap`
- `semantic_director.cli`

Why it is attractive:
- these package-owned modules still import a small number of root compatibility
  helpers even where canonical equivalents already exist
- the remaining work is direct-equivalent import cleanup, not boundary
  invention
- it is a small but real late-stage package polish queue

Risk shape:
- low to medium
- the cleanup must avoid utility shims that still intentionally preserve
  `director`-specific behavior
- direct-equivalent imports only keeps the blast radius small

## Decision

Chosen Queue V25 opener:
- `semantic_director.utility_boundary_cleanup`

## Why this wins now

Queue V24 did the honest remaining script-consumer cleanup.

That means the next higher-leverage move is to tighten the package boundary in
`semantic_director` where direct equivalents already exist:
- `semantic_labcore.runtime`
- `semantic_labcore.openai_responses`
- `semantic_director.schemas`

This is small enough to stay safe and useful enough to be worth a queue.
