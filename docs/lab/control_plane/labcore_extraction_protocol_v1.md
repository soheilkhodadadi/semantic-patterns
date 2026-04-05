# Labcore Extraction Protocol V1

## Purpose

This protocol defines the first controlled path for moving shared `labcore` implementation from:
- `src/semantic_ai_washing/labcore/`

to the seeded package shell under:
- `packages/labcore/src/semantic_labcore/`

The goal is to make extraction safe, reversible, and compatible with the active AI-washing lane.

## Extraction principle

The extraction unit is a coherent module or subpackage, not a single helper function.

Good extraction units include:
- `runtime.py`
- `audit.py`
- `security.py`
- `openai_responses.py`
- `registry/`

Do not extract one tiny symbol at a time.
The replaceable unit should stay package-shaped.

## Preconditions

Before extracting a module into `packages/labcore`:
- the package shell exists
- package smoke tests pass
- at least one real caller family already uses `semantic_ai_washing.labcore` directly
- compatibility shims are still allowed in the legacy path
- targeted validation scope is known in advance

## Recommended extraction order

1. `runtime.py`
2. `audit.py`
3. `security.py`
4. `openai_responses.py`
5. `registry/`

Reason:
- this order follows current reuse maturity
- it keeps low-level dependencies below higher-level registry logic

## Controlled extraction steps

### Step 1. Copy, do not move
Copy the selected module from:
- `src/semantic_ai_washing/labcore/...`

to:
- `packages/labcore/src/semantic_labcore/...`

Do not delete the legacy module in the same round.

### Step 2. Preserve authority with a shim
After the copy is in place, convert the legacy module into a compatibility shim that re-exports from `semantic_labcore`.

Direction after extraction should be:
- canonical implementation: `semantic_labcore.*`
- compatibility layer: `semantic_ai_washing.labcore.*`

This preserves the active AI-washing import lane while allowing the shared package to become real.

### Step 3. Keep dependency direction clean
The extracted package must not import back into:
- `semantic_ai_washing`
- project-specific analytics
- manuscript generation code

If back-imports are needed, the extraction is premature.

### Step 4. Validate in three layers
Run, at minimum:
- local package smoke tests for `packages/labcore`
- targeted caller tests for the migrated family
- compatibility import checks through `semantic_ai_washing.labcore`

### Step 5. Record the round
Every extraction round must leave behind:
- one migration note
- one validation summary
- one explicit statement of what remains authoritative

## Acceptance gate

An extraction round is accepted when:
- canonical implementation exists in `semantic_labcore`
- the legacy path still imports cleanly
- targeted callers still pass
- package build still passes
- no project-specific semantics leaked into the shared package

## Fail conditions

Stop and roll back the round if:
- the extracted module needs project-specific imports
- the compatibility shim becomes circular
- callers need wide import rewrites beyond the bounded scope
- package build or targeted caller tests fail

## Near-term first candidate

The best first real extraction candidate is:
- `runtime.py`

Why:
- it is already heavily reused
- its scope is genuinely generic
- multiple caller families already depend on it safely

## Bottom line

`labcore` extraction should happen by module-sized copy-plus-shim rounds.
That keeps the active project stable while the shared package becomes canonical over time.
