# Preliminary Model Benchmark Matrix

- Status: `no_winner`
- Primary benchmark available: `True`
- Selected model: `none`

| Model | Benchmark | Accuracy | Macro F1 | Binary Relevance Acc | A/S Conditional Acc | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| mpnet_prelim_v1 | held_out_v3 | 0.6215 | 0.5825 | 0.7401 | 0.7556 | false |
| mpnet_prelim_v1 | irr_boundary_benchmark | 0.7667 | 0.7618 | 0.8833 | 0.8000 | false |
| mpnet_prelim_v1 | frozen_validation_split | 0.7207 | 0.6276 | 0.8649 | 0.6190 | false |
| mpnet_logreg_prelim_v1 | held_out_v3 | 0.6667 | 0.6224 | 0.7684 | 0.7667 | false |
| mpnet_logreg_prelim_v1 | irr_boundary_benchmark | 0.8000 | 0.7972 | 0.8750 | 0.8714 | false |
| mpnet_logreg_prelim_v1 | frozen_validation_split | 0.7658 | 0.6689 | 0.8829 | 0.6905 | false |
| binary_relevance_then_as_v1 | held_out_v3 | 0.6836 | 0.6326 | 0.7853 | 0.7556 | false |
| binary_relevance_then_as_v1 | irr_boundary_benchmark | 0.7917 | 0.7841 | 0.8833 | 0.8286 | false |
| binary_relevance_then_as_v1 | frozen_validation_split | 0.7838 | 0.6521 | 0.8919 | 0.6905 | false |
| layered_binary_relevance_logreg_as_v1 | held_out_v3 | 0.6893 | 0.6371 | 0.7853 | 0.7778 | false |
| layered_binary_relevance_logreg_as_v1 | irr_boundary_benchmark | 0.8083 | 0.8043 | 0.8750 | 0.8714 | false |
| layered_binary_relevance_logreg_as_v1 | frozen_validation_split | 0.7658 | 0.6476 | 0.8829 | 0.6905 | false |
