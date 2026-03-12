# Prompt Boundary Benchmark

Use this playbook when label quality is concentrated in a narrow boundary problem rather than a broad extraction failure.

## When to use
- Overall agreement is acceptable.
- A specific label boundary is weak on a reviewed slice.
- The slice text can be held fixed while prompt variants are tested.

## Procedure
1. Freeze the input slice and the reviewed benchmark labels.
2. Define a small prompt set focused on the observed mismatch patterns.
3. Run all variants on the same rows.
4. Score overall agreement and the target subgroup agreement.
5. Select the winner deterministically.
6. If no variant passes the gate, stop and escalate to a different playbook.

## Success condition
- The target subgroup improves without degrading overall agreement.

## Stop condition
- No variant passes the gate, or improvements only come from harming other labels.

## Follow-up
- If prompt-only calibration fails, use `extraction_micro_cleanup` on the noisiest rows.
