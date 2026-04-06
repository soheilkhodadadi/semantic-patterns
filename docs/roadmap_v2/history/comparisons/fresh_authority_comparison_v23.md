# Fresh Authority Comparison V23

## Purpose

Choose the Queue V20 opener after Queue V19 completed cleanly.

## Candidates compared

1. `semantic_director.iteration_log`
2. `semantic_director.api_bootstrap`

## Candidate A: `semantic_director.iteration_log`

Why it is attractive:
- it is the cleanest remaining `director` adapter authority with direct root test pressure
- it opens a coherent snapshot-adapter queue alongside `documents` and `atlas`
- it reduces the remaining root-only pressure around `SnapshotIngestor` instead of opening an unrelated runtime lane
- it has a compact parser boundary and a focused regression shape

Risk shape:
- low
- direct caller pressure is concentrated in the snapshot/core regression bundle
- no live API transport or cost-policy behavior needs to move in the opener

## Candidate B: `semantic_director.api_bootstrap`

Why it is attractive:
- it has strong direct test pressure and real runtime value
- it would continue the assistive/API smoke-test chain inside the `director` lane
- it is already downstream of canonical `api_assistive` and `cost`

Risk shape:
- medium
- it still depends on root `openai_responses`, utils, and schema paths
- it is a less coherent follow-on from Queue V19 than the remaining snapshot adapters

## Decision

Chosen Queue V20 opener:
- `semantic_director.iteration_log`

## Why this wins now

It is the cleaner opener.

Queue V19 closed the last active `ai_washing` benchmark edge and tightened the
`director` validation/governance lane. The next highest-value move is to reduce
remaining root-only pressure around snapshot ingestion by migrating the
remaining snapshot adapters as one coherent queue.

`semantic_director.api_bootstrap` remains a good future `director` candidate,
but it is better handled after the snapshot-adapter lane is canonical.
