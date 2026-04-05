from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.common import (
    ALLOWED_LABELS,
    compute_sample_id,
    compute_sentence_id,
    load_table,
    normalize_sentence,
)
from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS as ROOT_ALLOWED_LABELS,
    compute_sample_id as root_compute_sample_id,
    compute_sentence_id as root_compute_sentence_id,
    normalize_sentence as root_normalize_sentence,
)


def test_member_common_exports_match_root_compatibility_surface() -> None:
    assert ALLOWED_LABELS == ROOT_ALLOWED_LABELS
    assert normalize_sentence(" AI systems, ARE deployed. ") == root_normalize_sentence(
        " AI systems, ARE deployed. "
    )

    sentence_norm = normalize_sentence("We deploy AI models into production")
    assert compute_sample_id("path/file.txt", 7, sentence_norm) == root_compute_sample_id(
        "path/file.txt", 7, sentence_norm
    )
    assert compute_sentence_id(sentence_norm) == root_compute_sentence_id(sentence_norm)


def test_member_common_load_table_retries_parquet_timeout(tmp_path: Path, monkeypatch) -> None:
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
