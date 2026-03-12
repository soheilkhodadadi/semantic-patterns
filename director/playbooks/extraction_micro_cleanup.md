# Extraction Micro Cleanup

Use this playbook when a small number of noisy rows are preventing reliable review or IRR, but a full extraction redesign would be too expensive.

## When to use
- Noise is concentrated in a small set of rows.
- The noise type is concrete and repeated.
- Raw source files are available for targeted re-extraction.

## Procedure
1. Isolate 5 to 10 noisy rows.
2. Trace each row to its original source file and local context.
3. Add one cleanup rule at a time.
4. Rebuild only the targeted slice.
5. Compare before and after on the same rows.
6. Accept the rule only if it removes the targeted noise without collateral damage.

## Success condition
- The targeted contamination is removed and the rebuilt rows are cleaner for raters.

## Stop condition
- Cleanup improves one error type but creates new corruption or sentence loss.

## Follow-up
- If cleanup succeeds, rerun the affected slice and then return to prompt or rubric calibration if needed.
