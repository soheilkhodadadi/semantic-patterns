# Selective-Defer Simulation

- Benchmark: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/validation/held_out_v4/held_out_sentences_v4_hybrid_api_upgrade_v2_scored.csv`
- Rows: `120`
- Local base: `layered_binary_relevance_logreg_as_v1`
- API A column: `assistive_label`
- API B available: `False`

| Policy | Accuracy | Macro F1 | Binary Relevance Acc | A/S Acc | Deferred Rows | Deferred Rate | Errors Captured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| api_a_conf_or_margin | 0.8500 | 0.8364 | 0.9167 | 0.8649 | 40 | 0.3333 | 13 |
| api_a_conf_or_margin_or_disagreement | 0.8500 | 0.8364 | 0.9167 | 0.8649 | 40 | 0.3333 | 13 |
| api_a_low_conf_060 | 0.8500 | 0.8364 | 0.9167 | 0.8649 | 40 | 0.3333 | 13 |
| api_a_component_disagreement | 0.8000 | 0.7910 | 0.9167 | 0.7838 | 4 | 0.0333 | 2 |
| api_a_low_as_margin_015 | 0.7917 | 0.7799 | 0.8667 | 0.8378 | 16 | 0.1333 | 4 |
| local_only | 0.7833 | 0.7709 | 0.9000 | 0.7838 | 0 | 0.0000 | 0 |
| oracle_error_only | 0.9250 | 0.9186 | 0.9583 | 0.9459 | 26 | 0.2167 | 17 |
