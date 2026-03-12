# Tranche 1 Prompt Benchmark v2.4

## Summary

- Generated at: `2026-03-11T02:18:57.234836+00:00`
- Input slice: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/labels/v1/labeling_batch_v1_reextracted_v2_2_slice40.csv`
- Benchmark labels: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv`
- Acceptance gate: overall `>= 35/40`, `Actionable/Speculative >= 10/12`
- Winner: `v2_4a`
- Winner gate passed: `True`

## Variant Scores

### `v2_4a` — factual_claim_rule
- Overall agreement: `35/40`
- `Actionable/Speculative` agreement: `11/12`
- `Actionable -> Speculative` misses: `0`
- `Actionable -> Irrelevant` misses: `0`
- Eligible: `True`
- Gate passed: `True`

### `v2_4b` — clause_priority_rule
- Overall agreement: `27/40`
- `Actionable/Speculative` agreement: `7/12`
- `Actionable -> Speculative` misses: `0`
- `Actionable -> Irrelevant` misses: `0`
- Eligible: `False`
- Gate passed: `False`

### `v2_4c` — decision_tree_rule
- Overall agreement: `36/40`
- `Actionable/Speculative` agreement: `10/12`
- `Actionable -> Speculative` misses: `0`
- `Actionable -> Irrelevant` misses: `1`
- Eligible: `True`
- Gate passed: `True`

### `v2_4d` — golden_example_rule
- Overall agreement: `33/40`
- `Actionable/Speculative` agreement: `11/12`
- `Actionable -> Speculative` misses: `0`
- `Actionable -> Irrelevant` misses: `0`
- Eligible: `False`
- Gate passed: `False`

## Decision

- Proceed to full tranche regeneration under `v2_4a`.

