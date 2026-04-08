# Preliminary Model Benchmark Matrix

- Status: `pending_primary_benchmark`
- Primary benchmark available: `False`
- Selected model: `none`

| Model | Benchmark | Accuracy | Macro F1 | Binary Relevance Acc | A/S Conditional Acc | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| mpnet_prelim_v1 | irr_boundary_benchmark | 0.7667 | 0.7618 | 0.8833 | 0.8000 | false |
| mpnet_prelim_v1 | frozen_validation_split | 0.7207 | 0.6276 | 0.8649 | 0.6190 | false |
| mpnet_logreg_prelim_v1 | irr_boundary_benchmark | 0.8000 | 0.7972 | 0.8750 | 0.8714 | false |
| mpnet_logreg_prelim_v1 | frozen_validation_split | 0.7658 | 0.6689 | 0.8829 | 0.6905 | false |
| binary_relevance_then_as_boundary_v2 | irr_boundary_benchmark | 0.7833 | 0.7754 | 0.8833 | 0.8143 | false |
| binary_relevance_then_as_boundary_v2 | frozen_validation_split | 0.7748 | 0.6346 | 0.9009 | 0.6429 | false |
