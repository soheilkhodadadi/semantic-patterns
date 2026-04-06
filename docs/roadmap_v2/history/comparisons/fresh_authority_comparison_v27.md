# Fresh Authority Comparison V27

## Purpose

Choose Queue V24 after Queue V23 completed cleanly.

## Candidates compared

1. `semantic_director.utility_boundary_cleanup`
2. `hygiene.legacy_script_consumer_cleanup`

## Candidate A: `semantic_director.utility_boundary_cleanup`

Representative surfaces:
- `semantic_director.decision`
- `semantic_director.documents`
- `semantic_director.gates`
- `semantic_director.sensors`
- `semantic_director.api_bootstrap`
- `semantic_director.cli`

Why it is attractive:
- these package-owned modules still import a few root compatibility helpers such
  as `semantic_ai_washing.director.core.utils`, `security`, and
  `openai_responses`
- another tiny follow-on could make the package boundary look even cleaner

Risk shape:
- medium
- the pressure is real but shallow
- much of it is intentionally labcore-backed or compatibility-shaped
- forcing this next would risk a low-leverage cleanup queue driven more by
  aesthetics than by operational clarity

## Candidate B: `hygiene.legacy_script_consumer_cleanup`

Representative surfaces:
- `src/data/clean_compustat.py`
- `src/data/clean_crsp.py`
- `src/data/clean_sec.py`
- `src/data/download_compustat.py`
- `src/data/download_crsp.py`
- `src/data/download_sec.py`

Why it is attractive:
- Queue V23 already downgraded the underlying `semantic_ai_washing.data.*`
  utilities in the generated registry layer
- the remaining ambiguity now lives in the flat consumer shim lane
- this is the cleanest next step before any later script-deprecation or
  quarantine discussion

Risk shape:
- low
- generator-backed and docs-backed
- no code deletion
- keeps hygiene separate from authority migration

## Decision

Chosen Queue V24 opener:
- `hygiene.legacy_script_consumer_cleanup`

## Why this wins now

It is the more honest next move.

After Queue V23, the remaining ambiguity is not primarily inside the package
boundary. It is in the flat legacy script-consumer layer that still points at
the now-downgraded historical utilities.

That makes one more bounded hygiene queue higher leverage than a marginal
`director` utility polish queue.
