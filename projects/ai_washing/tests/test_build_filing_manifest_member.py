from __future__ import annotations

from pathlib import Path

import pandas as pd

from ai_washing_member.data.build_filing_manifest import build_manifest, compute_manifest_row_id


def _build_index_frame(per_quarter: int = 2) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cik_seed = 2000
    for quarter in (1, 2, 3, 4):
        for offset in range(per_quarter):
            cik = str(cik_seed + quarter * 10 + offset)
            rows.append(
                {
                    "cik": cik,
                    "year": 2024,
                    "quarter": quarter,
                    "form": "10-K",
                    "filename": f"20240{quarter}01_10-K_edgar_data_{cik}_000{offset}.txt",
                    "path": f"2024/QTR{quarter}/20240{quarter}01_10-K_edgar_data_{cik}_000{offset}.txt",
                    "source_root": "env:SEC_SOURCE_DIR",
                    "index_timestamp": "2026-03-06T00:00:00+00:00",
                    "source_window_id": "active_2021_2024",
                }
            )
    return pd.DataFrame(rows)


def test_member_build_manifest_runs_with_repo_style_contract(tmp_path: Path) -> None:
    index_path = tmp_path / "index.csv"
    controls_path = tmp_path / "controls.csv"
    crosswalk_path = tmp_path / "crosswalk.csv"

    _build_index_frame(per_quarter=2).to_csv(index_path, index=False)
    pd.DataFrame(
        [
            {"cik": "2010", "year": 2024, "sic": 3571},
            {"cik": "2020", "year": 2024, "sic": 2834},
            {"cik": "2030", "year": 2024, "sic": 4800},
            {"cik": "2040", "year": 2024, "sic": 6021},
        ]
    ).to_csv(controls_path, index=False)
    pd.DataFrame(columns=["cik", "gvkey", "sic"]).to_csv(crosswalk_path, index=False)

    manifest, summary = build_manifest(
        index_path=str(index_path),
        year=2024,
        form="10-K",
        target_size=8,
        quarter_quota=2,
        controls_path=str(controls_path),
        crosswalk_path=str(crosswalk_path),
        manifest_id="member_pilot",
        seed=13,
    )

    assert len(manifest) == 8
    assert summary["quota_satisfied"] is True
    assert set(manifest["selection_reason"]).issubset({"quarter_ff12_round_robin", "quarter_fill"})
    assert (
        compute_manifest_row_id("member_pilot", str(manifest.iloc[0]["path"]))
        == manifest.iloc[0]["manifest_row_id"]
    )
