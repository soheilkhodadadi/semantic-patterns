# Migration Round I: AI-Washing Group 1 Code Seed V1

## Scope

This round starts Group 1 of the `labeling/common.py` migration by moving the
canonical implementation into the `ai_washing` member shell while preserving
legacy root compatibility.

Included in this slice:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`
- `projects/ai_washing/src/ai_washing_member/labeling/__init__.py`
- `projects/ai_washing/src/ai_washing_member/__init__.py`
- root compatibility shim at `src/semantic_ai_washing/labeling/common.py`
- member-local compatibility tests

## Member-local import path

Chosen transitional import path for the first member-owned code seed:
- `ai_washing_member.labeling.common`

Why this path:
- it avoids duplicating the canonical `semantic_ai_washing` package identity too early
- it gives the member shell a real code owner now
- it is explicit that this is a transition package, not the final export form

## Why this is only the start of Group 1

This round moves the authoritative implementation, but it does not yet require
all Group 1 callers to import the member-local path directly.

Legacy callers remain stable through the root compatibility shim:
- `semantic_ai_washing.labeling.common`

That keeps the move low-risk while proving that real project-owned code can now
live under `projects/ai_washing/src/`.

## Validation gate

Accept this slice only when:
- member-local tests pass
- focused Group 1 regression tests still pass
- `make doctor` succeeds with the updated workspace path profile
- root compatibility imports still work

## Outcome

This round is the first real project-member code move for `ai_washing`.
It narrows the authority map without prematurely declaring the whole member
buildable.
