# Fresh Authority Comparison V24

## Purpose

Choose the Queue V21 opener after Queue V20 completed cleanly.

## Candidates compared

1. `semantic_director.api_bootstrap`
2. `semantic_director.cli`

## Candidate A: `semantic_director.api_bootstrap`

Why it is attractive:
- it is the cleanest remaining non-adapter `director` runtime surface
- it has focused direct test pressure in the assistive/bootstrap gate
- it already sits downstream of canonical `semantic_director.api_assistive` and
  `semantic_director.cost`
- it opens a coherent runtime-entrypoint queue alongside `cli` and `__main__`

Risk shape:
- medium
- it still depends on root utility and transport helpers
- it touches truthful runtime failure reporting, so the gate needs to stay tight

## Candidate B: `semantic_director.cli`

Why it is attractive:
- it is the most visible remaining root-only `director` entrypoint
- it would immediately move many direct test callers onto the package path
- it reduces lingering root pressure across the control-plane entry surface

Risk shape:
- medium-high
- it is a broader blast-radius move than `api_bootstrap`
- it still carries command-string references and root utility dependencies
- it is a better follow-on once the focused task runtime is canonical

## Decision

Chosen Queue V21 opener:
- `semantic_director.api_bootstrap`

## Why this wins now

It is the safer opener with real leverage.

Queue V20 closed the snapshot-adapter lane. The next honest move is to start
the remaining runtime-entrypoint lane with the smallest bounded authority that
still has direct caller pressure. That is `semantic_director.api_bootstrap`,
not `semantic_director.cli`.

Once `api_bootstrap` is canonical, the follow-on CLI and `__main__` moves can
stay inside the same lane without pretending the broader entry surface is as
cheap as the task runtime.
