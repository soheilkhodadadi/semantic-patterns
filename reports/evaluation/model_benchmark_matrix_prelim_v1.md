# Preliminary Model Benchmark Matrix

- Status: `selected`
- Primary benchmark available: `True`
- Selected model: `binary_relevance_then_as_v1`

| Model | Benchmark | Accuracy | Macro F1 | Binary Relevance Acc | A/S Conditional Acc | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| mpnet_prelim_v1 | held_out_v2 | 0.6384 | 0.6120 | 0.7627 | 0.7556 | false |
| mpnet_prelim_v1 | historical_held_out | 0.4299 | 0.4478 | 0.6402 | 0.7345 | false |
| mpnet_prelim_v1 | irr_boundary_benchmark | 0.7667 | 0.7618 | 0.8833 | 0.8000 | false |
| mpnet_prelim_v1 | frozen_validation_split | 0.7117 | 0.6158 | 0.8649 | 0.5952 | false |
| mpnet_logreg_prelim_v1 | held_out_v2 | 0.6893 | 0.6616 | 0.8023 | 0.7667 | false |
| mpnet_logreg_prelim_v1 | historical_held_out | 0.4626 | 0.4662 | 0.6028 | 0.8192 | false |
| mpnet_logreg_prelim_v1 | irr_boundary_benchmark | 0.8000 | 0.7972 | 0.8750 | 0.8714 | false |
| mpnet_logreg_prelim_v1 | frozen_validation_split | 0.7568 | 0.6570 | 0.8829 | 0.6667 | false |
| binary_relevance_then_as_v1 | held_out_v2 | 0.7062 | 0.6729 | 0.8192 | 0.7556 | false |
| binary_relevance_then_as_v1 | historical_held_out | 0.4065 | 0.4158 | 0.5794 | 0.7740 | false |
| binary_relevance_then_as_v1 | irr_boundary_benchmark | 0.7917 | 0.7841 | 0.8833 | 0.8286 | false |
| binary_relevance_then_as_v1 | frozen_validation_split | 0.7838 | 0.6609 | 0.8919 | 0.6667 | false |
