# Selective-Defer Simulation

- Benchmark: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/data/validation/held_out_v3/held_out_sentences_v3_review_sheet_labelled.csv`
- Rows: `177`
- Local base: `layered_binary_relevance_logreg_as_v1`
- API A column: `assistive_label`
- API B available: `False`

| Policy | Accuracy | Macro F1 | Binary Relevance Acc | A/S Acc | Deferred Rows | Deferred Rate | Errors Captured |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| api_a_conf_or_margin | 0.9266 | 0.9167 | 0.9435 | 0.9444 | 77 | 0.4350 | 42 |
| api_a_conf_or_margin_or_disagreement | 0.9266 | 0.9167 | 0.9435 | 0.9444 | 77 | 0.4350 | 42 |
| api_a_low_conf_060 | 0.9266 | 0.9167 | 0.9435 | 0.9444 | 77 | 0.4350 | 42 |
| api_a_low_as_margin_015 | 0.7627 | 0.7217 | 0.8192 | 0.8556 | 21 | 0.1186 | 13 |
| local_only | 0.6893 | 0.6371 | 0.7853 | 0.7778 | 0 | 0.0000 | 0 |
| api_a_component_disagreement | 0.6893 | 0.6371 | 0.7853 | 0.7778 | 3 | 0.0169 | 0 |
| oracle_error_only | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 55 | 0.3107 | 55 |
