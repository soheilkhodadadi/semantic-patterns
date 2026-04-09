# Selective-Defer Simulation

- Benchmark: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/validation/held_out_v4/held_out_sentences_v4_gpt5mini_high_output_scored.csv`
- Rows: `120`
- Local base: `layered_binary_relevance_logreg_as_v1`
- API A column: `assistive_label`
- API B available: `False`

| Policy | Accuracy | Macro F1 | Binary Relevance Acc | A/S Acc | Deferred Rows | Deferred Rate | Errors Captured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| api_a_conf_or_margin | 0.8500 | 0.8347 | 0.9167 | 0.8649 | 40 | 0.3333 | 12 |
| api_a_conf_or_margin_or_disagreement | 0.8500 | 0.8347 | 0.9167 | 0.8649 | 40 | 0.3333 | 12 |
| api_a_low_conf_060 | 0.8500 | 0.8347 | 0.9167 | 0.8649 | 40 | 0.3333 | 12 |
| api_a_low_as_margin_015 | 0.8083 | 0.7927 | 0.8833 | 0.8514 | 16 | 0.1333 | 6 |
| api_a_component_disagreement | 0.7917 | 0.7812 | 0.9167 | 0.7703 | 4 | 0.0333 | 1 |
| local_only | 0.7833 | 0.7709 | 0.9000 | 0.7838 | 0 | 0.0000 | 0 |
| oracle_error_only | 0.9167 | 0.9110 | 0.9500 | 0.9324 | 26 | 0.2167 | 16 |
