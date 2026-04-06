# Fresh Authority Comparison V29

## Purpose

Choose Queue V26 after Queue V25 completed cleanly.

## Candidates compared

1. `hygiene.remaining_bounded_followon`
2. `semantic_director.wrapper_normalization`

## Candidate A: `hygiene.remaining_bounded_followon`

Representative surfaces:
- late-stage script-deprecation wording follow-ons
- additional posture/index refresh around legacy consumer and flat-shim lanes

Why it is attractive:
- hygiene has helped the repo tell a truer story
- another bounded pass would still be safe

Risk shape:
- medium
- after Queues V23 and V24, the remaining hygiene leverage is weaker
- another queue here risks polishing posture language more than changing the
  actual package/member boundary story

## Candidate B: `semantic_director.wrapper_normalization`

Representative surfaces:
- `semantic_director.cli`
- `semantic_director.gates`
- root compatibility shims under `src/semantic_ai_washing/director/core/`

Why it is attractive:
- Queue V25 left exactly two intentional deferred imports inside
  `semantic_director`
- both are real director-facing contracts, not generic helpers:
  - OpenAI key/security contract
  - director-specific command-timeout wording
- normalizing them would complete the remaining honest `director` package
  boundary pressure without inventing a new runtime wave

Risk shape:
- low to medium
- only worth doing if we deliberately want those two wrapper contracts to
  become package-owned
- safe if scoped strictly to those wrappers and validated narrowly

## Decision

Chosen Queue V26 opener:
- `semantic_director.wrapper_normalization`

## Why this wins now

The hygiene lane is still valuable, but it is no longer the highest-leverage
late-stage move.

Queue V25 proved that only two real deferred `director` imports remained, and
both are package-shaped wrapper contracts rather than accidental lag. That makes
Queue V26 the right moment to normalize them on purpose:
- `semantic_director.security`
- `semantic_director.runtime`

This stays bounded, honest, and end-stage appropriate.
