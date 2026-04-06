# Director Utility Boundary Posture Refresh V1

## Purpose

Record what Queue V25 changed in the late-stage `director` package boundary and
what remains intentionally deferred.

## What Queue V25 cleaned up

Queue V25 removed direct-equivalent package imports from root compatibility
surfaces where stable canonical replacements already existed:

- runtime helpers now prefer `semantic_labcore.runtime`
- responses transport now prefers `semantic_labcore.openai_responses`
- schema imports now prefer `semantic_director.schemas`

This tightened the package boundary without inventing any new authority.

## What still remains intentionally deferred

Two root compatibility imports still remain inside `semantic_director`:

1. `semantic_ai_washing.director.core.security`
   - still used by `semantic_director.cli`
   - kept because it preserves the director-facing environment validation and
     repo secret-scan contract already exercised by the live control-plane
     entrypoint

2. `semantic_ai_washing.director.core.utils.run_command`
   - still used by `semantic_director.gates`
   - kept because the wrapper preserves current director command-execution
     wording and behavior rather than being a pure runtime helper alias

## Current posture

This means the remaining `director` boundary pressure is now narrow and honest:

- no broad extraction wave remains
- no big runtime lane remains
- the remaining root imports are wrapper-shaped and should only move if we
  deliberately decide to normalize those behavior contracts

## Recommended next-step posture

- do not auto-open another tiny `director` cleanup queue just to reduce import
  count
- prefer either:
  - a very explicit wrapper-normalization queue if we decide those contracts
    should become package-owned
  - or a separate late-stage hygiene queue

Queue V25 therefore counts as a useful late-stage polish queue, not the start
of a new migration wave.
