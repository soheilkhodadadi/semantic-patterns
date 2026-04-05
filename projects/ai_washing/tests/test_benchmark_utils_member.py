from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.classification.benchmark_utils import (
    compute_metrics,
    load_benchmark_frame,
)
from semantic_ai_washing.classification.benchmark_utils import (
    compute_metrics as root_compute_metrics,
)
from semantic_ai_washing.classification.benchmark_utils import (
    load_benchmark_frame as root_load_benchmark_frame,
)


def test_member_load_benchmark_frame_matches_root_shim(tmp_path: Path) -> None:
    path = tmp_path / "benchmark.csv"
    pd.DataFrame(
        [
            {"sentence": "Actionable alpha", "label": "Actionable"},
            {"sentence": "Speculative beta", "label": "Speculative"},
            {"sentence": "Irrelevant gamma", "label": "Irrelevant"},
            {"sentence": "Bad row", "label": "Unknown"},
        ]
    ).to_csv(path, index=False)

    member_frame = load_benchmark_frame(path)
    root_frame = root_load_benchmark_frame(path)

    assert member_frame.to_dict(orient="records") == root_frame.to_dict(orient="records")
    assert member_frame["label"].tolist() == ["Actionable", "Speculative", "Irrelevant"]


def test_member_compute_metrics_matches_root_shim() -> None:
    y_true = ["Actionable", "Speculative", "Irrelevant", "Actionable"]
    y_pred = ["Actionable", "Speculative", "Irrelevant", "Speculative"]

    member_metrics = compute_metrics(y_true, y_pred)
    root_metrics = root_compute_metrics(y_true, y_pred)

    assert member_metrics == root_metrics
    assert member_metrics["accuracy"] == 0.75
    assert set(member_metrics["per_class"]) == {"Actionable", "Speculative", "Irrelevant"}
