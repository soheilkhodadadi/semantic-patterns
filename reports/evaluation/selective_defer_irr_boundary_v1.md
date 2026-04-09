# Selective-Defer Simulation

- Benchmark: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/validation/irr_boundary_benchmark_v1_review_sheet_scored.csv`
- Rows: `120`
- Local base: `layered_binary_relevance_logreg_as_v1`
- API A column: `assistive_label`
- API B available: `False`

| Policy | Accuracy | Macro F1 | Binary Relevance Acc | A/S Acc | Deferred Rows | Deferred Rate | Errors Captured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| api_a_low_as_margin_015 | 0.8250 | 0.8216 | 0.8750 | 0.9000 | 10 | 0.0833 | 3 |
| api_a_component_disagreement | 0.8250 | 0.8213 | 0.8917 | 0.8857 | 3 | 0.0250 | 2 |
| api_a_conf_or_margin | 0.8250 | 0.8196 | 0.8833 | 0.8857 | 32 | 0.2667 | 7 |
| api_a_conf_or_margin_or_disagreement | 0.8250 | 0.8196 | 0.8833 | 0.8857 | 32 | 0.2667 | 7 |
| api_a_low_conf_060 | 0.8250 | 0.8196 | 0.8833 | 0.8857 | 32 | 0.2667 | 7 |
| local_only | 0.8083 | 0.8043 | 0.8750 | 0.8714 | 0 | 0.0000 | 0 |
| oracle_error_only | 0.9083 | 0.9071 | 0.9333 | 0.9571 | 23 | 0.1917 | 12 |
