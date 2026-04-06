# Fresh Authority Comparison V15

## Purpose

Choose the Queue V12 opener after Queue V11 completed cleanly.

## Candidates compared

1. `semantic_director.review`
2. `ai_washing_member.labeling.assistive_prelabel_batch`

## Candidate A: `semantic_director.review`

Why it is attractive:
- it is the next real `director` control-plane surface after `planner`
- direct caller pressure is concentrated in the CLI and focused director review/playbook tests
- it opens a clean downstream follow-on in `optimizer`
- the root compatibility shim can preserve monkeypatch-based test behavior by re-exporting the same `ReviewEngine` class object

Risk shape:
- medium
- one clean `director` lane
- shared director regression bundle already exists

## Candidate B: `ai_washing_member.labeling.assistive_prelabel_batch`

Why it is attractive:
- it opens an active assistive-labeling workflow that is still relevant to the project
- it would move a meaningful current-stage labeling surface into the member-owned lane
- it could later connect naturally to `benchmark_prompt_variants` and restartable assistive flows

Risk shape:
- medium-high
- monkeypatch-heavy tests still lean on root-module globals in the legacy path
- the authority move is honest, but the direct caller/test boundary is not yet as clean as the `director` review chain

## Decision

Chosen Queue V12 opener:
- `semantic_director.review`

## Why this wins now

It is the cleaner opener for Queue V12 because it lets us build a compact `director` chain:

1. `review`
2. `optimizer`
3. `api_assistive` only if its follow-on pre-scan still stays clean

That keeps the queue in a stable control-plane lane and avoids forcing the assistive-labeling workflow forward before its root monkeypatch boundary is ready.
