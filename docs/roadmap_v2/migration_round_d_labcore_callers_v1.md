# Migration Round D: First Labcore Direct-Caller Slice V1

## Purpose

This note records the first real caller migration outside the `director` package.
The goal is to prove that the new shared package seed is usable directly by an external caller family before broader package/member migrations begin.

## Migration slice

The first migrated caller family is the `labeling` assistive-prelabel batch family:
- `src/semantic_ai_washing/labeling/assistive_prelabel_batch.py`
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `src/semantic_ai_washing/labeling/score_prelabel_sheet.py`

These modules are a good first slice because they are:
- outside `director`
- already bounded as a coherent workflow family
- dependent only on low-level helper behavior, not on `director` orchestration semantics
- covered by existing regression tests

## What changed

The migrated modules now import shared low-level helpers directly from `labcore`:
- runtime helpers from `semantic_ai_washing.labcore.runtime`
- Responses transport helpers from `semantic_ai_washing.labcore.openai_responses`

This means the first direct external dependency on the extracted shared layer is now real, not hypothetical.

## What did not change

The migration intentionally does **not**:
- relocate the labeling modules into a new workspace member yet
- remove compatibility shims from `semantic_ai_washing.director.core.*`
- change any `director`-owned call paths
- broaden the slice beyond the assistive-prelabel family

This keeps the blast radius small while still proving the new model.

## Why this slice matters

This round is the first practical proof of the package-first design:
- `labcore` is no longer only a compatibility extraction target
- external callers can use it directly
- future shared packages can be promoted through real caller adoption rather than only through internal refactors

## Acceptance gate

This slice is accepted when:
- the three labeling modules import from `labcore` directly
- the existing labeling regression tests still pass
- no broader authority shift is implied for unrelated modules

## Follow-on implications

If this slice holds, the next bounded steps become clearer:
- additional external caller families can migrate to `labcore` directly
- `ai_washing` member-facing normalization can proceed with more confidence
- eventual `packages/labcore` seeding has one more real usage proof behind it

## Bottom line

Round D begins with direct caller adoption, not broad relocation.
That is the right first proof for the workspace/package model.
