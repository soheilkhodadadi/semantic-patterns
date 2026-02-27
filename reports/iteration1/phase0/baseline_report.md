# Iteration 1 Phase 0 Baseline Report

- Generated: 2026-02-27T18:01:28.249395+00:00
- Git commit: `445d154cd2fb2ec48ca6d6e378448efa4b38f86a`
- Centroids: `data/validation/centroids_mpnet.json`
- Centroid sha256: `449e819f7174895a92711840ce25f2298a35e2a6b621561e9712a584b3f8ff77`
- Evaluation mode: `fallback_existing_eval_details`

## Held-out Metrics
- Accuracy: `0.5417`
- Macro F1: `0.5235`
- Total samples: `216`

## Batch Sanity Summary
- Input files selected: `20`
- Processed: `0`
- Skipped: `20`
- Errors: `0`
- Reclassification note: `reclassification fallback used (TimeoutExpired)`
- Coverage mismatch count: `0`
- Pathology-flagged files: `6`

## Phase Gate Checklist
- [PASS] Metrics available
- [PASS] Centroid fingerprint available
- [PASS] Git commit hash recorded
- [PASS] Coverage mismatch is zero
- [PASS] Failure taxonomy generated
- [PASS] Distribution diagnostics generated
- [PASS] Confusion labels align with A/S/I

## Failure Taxonomy (A->S, A->I, S->A, S->I, I->A, I->S)

- `A->S`: `0`
- `A->I`: `10`
- `S->A`: `4`
- `S->I`: `2`
- `I->A`: `18`
- `I->S`: `65`
