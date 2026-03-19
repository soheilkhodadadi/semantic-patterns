from __future__ import annotations

from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import load_table


def test_load_table_retries_parquet_timeout_with_direct_parquetfile(
    monkeypatch, tmp_path: Path
) -> None:
    path = tmp_path / "sample.parquet"
    pd.DataFrame({"value": [1, 2, 3]}).to_parquet(path, index=False)

    original_read_parquet = pd.read_parquet

    def flaky_read_parquet(*args, **kwargs):
        if Path(args[0]) == path:
            raise TimeoutError("transient parquet timeout")
        return original_read_parquet(*args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", flaky_read_parquet)

    loaded = load_table(path)

    assert loaded.to_dict(orient="list") == {"value": [1, 2, 3]}
