from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from semantic_ai_washing.analysis.delivery_table_payloads import load_panel


def test_load_panel_accepts_parquet_and_derives_sic2(tmp_path: Path) -> None:
    path = tmp_path / "panel.parquet"
    pd.DataFrame(
        {
            "cik": ["0001", "0001", "0002"],
            "year": [2020, 2021, 2020],
            "sic": [3571, 3571, 6021],
            "n_A": [2, 1, 0],
            "n_S": [1, 1, 0],
            "n_I": [0, 0, 0],
            "n_total": [3, 2, 0],
            "patents_ai": [1, 3, 0],
        }
    ).to_parquet(path, index=False)

    loaded = load_panel(path)

    assert loaded["sic2"].astype("Int64").tolist() == [35, 35, 60]
    assert loaded["log_patents_ai"].round(6).tolist() == np.log1p([1, 3, 0]).round(6).tolist()
    first_row = loaded.sort_values(["cik", "year"]).iloc[0]
    assert first_row["patents_ai_lead1"] == 3
    assert first_row["log_patents_ai_lead1"] > 0
