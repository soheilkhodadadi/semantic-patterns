# Script Consumer Posture Refresh V1

## Purpose

Record the practical outcome of Queue V24 after the flat legacy
`src/data/*` shim consumers were reclassified in the generated inventory and
registry layer.

## What changed

These six flat shim scripts are no longer best read as generic compatibility
surfaces:
- `src/data/clean_compustat.py`
- `src/data/clean_crsp.py`
- `src/data/clean_sec.py`
- `src/data/download_compustat.py`
- `src/data/download_crsp.py`
- `src/data/download_sec.py`

They now read as:
- legacy flat shims
- consumers of already-downgraded historical data utilities
- later cleanup candidates, not front-door workflow scripts

## Why this matters

Queue V23 clarified the posture of the underlying
`semantic_ai_washing.data.*` utilities.

Queue V24 clarifies the next layer out:
- the flat shim scripts should not be mistaken for current workflow entrypoints
- they remain useful only as compatibility consumers for older callers
- any future cleanup should deprecate or remove them deliberately, not by
  silent neglect

## What did not happen

- no flat shim was deleted
- no consumer was redirected to a new authority
- no code quarantine lane was created

## Recommended next posture

- do not promote the flat `src/data/*` shims into new workflow docs
- treat them as late-stage consumer cleanup candidates
- only consider removal after a later bounded queue confirms that their
  remaining external or historical caller expectations are satisfied

## Bottom line

Queue V24 did not shrink the repo, but it made the compatibility consumer lane
much more honest.

That is a good late-stage cleanup result.
