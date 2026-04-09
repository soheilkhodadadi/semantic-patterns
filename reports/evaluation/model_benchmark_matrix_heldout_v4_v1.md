# Preliminary Model Benchmark Matrix

- Status: `no_winner`
- Primary benchmark available: `True`
- Selected model: `none`

| Model | Benchmark | Accuracy | Macro F1 | Binary Relevance Acc | A/S Conditional Acc | Leakage |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| mpnet_prelim_v1 | held_out_v4 | 0.7333 | 0.7262 | 0.9000 | 0.7162 | true |
| mpnet_prelim_v1 | historical_held_out | 0.6215 | 0.5825 | 0.7401 | 0.7556 | false |
| mpnet_prelim_v1 | irr_boundary_benchmark | 0.7667 | 0.7618 | 0.8833 | 0.8000 | false |
| mpnet_prelim_v1 | frozen_validation_split | 0.7117 | 0.6158 | 0.8649 | 0.5952 | false |
| mpnet_logreg_prelim_v1 | held_out_v4 | 0.7833 | 0.7780 | 0.9083 | 0.7838 | true |
| mpnet_logreg_prelim_v1 | historical_held_out | 0.6667 | 0.6224 | 0.7684 | 0.7667 | false |
| mpnet_logreg_prelim_v1 | irr_boundary_benchmark | 0.8000 | 0.7972 | 0.8750 | 0.8714 | false |
| mpnet_logreg_prelim_v1 | frozen_validation_split | 0.7568 | 0.6570 | 0.8829 | 0.6667 | false |
| binary_relevance_then_as_v1 | held_out_v4 | 0.7583 | 0.7419 | 0.9083 | 0.7297 | true |
| binary_relevance_then_as_v1 | historical_held_out | 0.6836 | 0.6326 | 0.7853 | 0.7556 | false |
| binary_relevance_then_as_v1 | irr_boundary_benchmark | 0.7917 | 0.7841 | 0.8833 | 0.8286 | false |
| binary_relevance_then_as_v1 | frozen_validation_split | 0.7838 | 0.6609 | 0.8919 | 0.6667 | false |
| layered_binary_relevance_logreg_as_v1 | held_out_v4 | 0.7833 | 0.7709 | 0.9000 | 0.7838 | true |
| layered_binary_relevance_logreg_as_v1 | historical_held_out | 0.6893 | 0.6371 | 0.7853 | 0.7778 | false |
| layered_binary_relevance_logreg_as_v1 | irr_boundary_benchmark | 0.8083 | 0.8043 | 0.8750 | 0.8714 | false |
| layered_binary_relevance_logreg_as_v1 | frozen_validation_split | 0.7658 | 0.6540 | 0.8829 | 0.6667 | false |
