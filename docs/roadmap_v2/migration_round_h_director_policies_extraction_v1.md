# Migration Round H: Director Policies Extraction V1

## Scope

This round promotes the next clean `director` package slice into
`packages/director/src/semantic_director/policies/`.

Included in this slice:
- `semantic_director.policies.risk_register`
- `semantic_director.policies.__init__`
- package-local policy smoke test

Compatibility preserved in:
- `src/semantic_ai_washing/director/policies/risk_register.py`
- `src/semantic_ai_washing/director/policies/__init__.py`

## Why this slice now

This is the cleanest second `director` slice because it:
- is self-contained data policy content
- has a single meaningful runtime consumer in planner logic
- does not require moving planner internals yet
- keeps package growth incremental and easy to validate

## Validation gate

Accept this slice only when:
- package-local policy smoke tests pass
- root planner-oriented `director` tests still pass
- package build smoke still succeeds

## Outcome

This round grows `packages/director` without forcing a larger core extraction.
