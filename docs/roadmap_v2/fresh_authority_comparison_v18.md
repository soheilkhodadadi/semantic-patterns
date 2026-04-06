# Fresh Authority Comparison V18

## Purpose

Choose the Queue V15 opener from the active `ai_washing` classification surfaces in the root-surface triage registry.

## Candidates compared

1. `ai_washing_member.classification.train_binary_relevance_then_as`
2. `ai_washing_member.classification.benchmark_preliminary_models`

## Candidate A: `ai_washing_member.classification.train_binary_relevance_then_as`

Why it is attractive:
- it opens the remaining wave-1 model-training lane from the triage registry
- it pairs naturally with `train_logreg_preliminary` before the benchmark authority moves
- it keeps Queue V15 inside one coherent preliminary model-selection workflow
- the existing `tests/test_preliminary_benchmarking.py` bundle already exercises the binary, logreg, and benchmark chain together

Risk shape:
- medium
- one active `ai_washing` workflow lane
- low dependency spread outside the benchmarking gate

## Candidate B: `ai_washing_member.classification.benchmark_preliminary_models`

Why it is attractive:
- it has strong direct caller pressure in the benchmarking workflow
- it sits near the model-selection output boundary and would be highly visible as a migration win

Risk shape:
- medium-high
- still depends on root-owned wave-1 training authorities unless those move first
- less clean as a three-batch Queue V15 workflow than opening the upstream training lane

## Decision

Chosen Queue V15 opener:
- `ai_washing_member.classification.train_binary_relevance_then_as`

## Why this wins now

It gives Queue V15 a cleaner workflow shape:

1. `train_binary_relevance_then_as`
2. `train_logreg_preliminary`
3. `benchmark_preliminary_models`

That keeps the queue inside one active preliminary model-selection lane while following the triage registry instead of jumping straight to a downstream benchmark surface.
