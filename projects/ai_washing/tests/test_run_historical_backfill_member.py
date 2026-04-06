from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pandas as pd

from ai_washing_member.data.run_historical_backfill import run_backfill


def test_member_run_backfill_indexes_only_annual_forms(tmp_path):
    root = tmp_path / "sec"
    (root / "2016" / "QTR1").mkdir(parents=True)
    (root / "2017" / "QTR2").mkdir(parents=True)
    annual = root / "2016" / "QTR1" / "20160115_10-K_edgar_data_1000_example.txt"
    quarterly = root / "2016" / "QTR1" / "20160315_10-Q_edgar_data_2000_example.txt"
    annual_2 = root / "2017" / "QTR2" / "20170415_10-K-A_edgar_data_3000_example.txt"
    annual.write_text("annual", encoding="utf-8")
    quarterly.write_text("quarterly", encoding="utf-8")
    annual_2.write_text("annual amended", encoding="utf-8")

    args = Namespace(
        source_root=str(root),
        source_root_hint="",
        years=["2016", "2017"],
        forms=["10-K", "10-K-A"],
        output_csv=str(tmp_path / "index.csv"),
        output_source_windows=str(tmp_path / "source_windows.json"),
        output_summary=str(tmp_path / "summary.json"),
        progress_report=str(tmp_path / "progress.json"),
        cache_dir=str(tmp_path / "cache"),
        materialize_years=[],
        output_root=str(tmp_path / "sentences"),
        keywords_path="data/metadata/ai_keywords.txt",
        min_tokens=6,
        max_tokens=120,
        segmentation_mode="default",
        sample_size=10,
        materialization_report_template=str(tmp_path / "materialization_{year}.json"),
        force_recompute=False,
    )

    report = run_backfill(args)

    assert report["status"] == "completed"
    frame = pd.read_csv(args.output_csv, dtype={"cik": str})
    assert sorted(frame["form"].unique().tolist()) == ["10-K", "10-K-A"]
    assert len(frame) == 2
    progress = json.loads(Path(args.progress_report).read_text(encoding="utf-8"))
    assert progress["status"] == "completed"
