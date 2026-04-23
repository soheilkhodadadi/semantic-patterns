"""Build the first regression-ready filing estimation sample."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EVENT_PANEL = "data/processed/panel/filing_event_panel_v1.parquet"
DEFAULT_CONTROLS = "data/interim/market/filing_lagged_controls_v1.csv"
DEFAULT_OUTPUT = "data/processed/panel/filing_event_estimation_sample_v1.parquet"
DEFAULT_REPORT = "reports/analysis/filing_event_estimation_sample_v1.json"

CORE_COLUMNS = [
    "car_m1_p1",
    "share_actionable",
    "share_speculative",
    "share_irrelevant",
    "post_chatgpt",
    "ln_assets",
    "leverage",
    "cash",
    "roa",
]
EXTENDED_COLUMNS = CORE_COLUMNS + ["rd_intensity", "capx_at", "sales_growth"]
BHAR_6M_COLUMNS = CORE_COLUMNS + ["bhar_6m"]


def _normalize_string_key(series: pd.Series, *, zero_fill: int | None = None) -> pd.Series:
    normalized = series.fillna("").astype(str).str.strip()
    if zero_fill is not None:
        normalized = normalized.str.replace(r"\.0$", "", regex=True)
        normalized = normalized.str.zfill(zero_fill)
    return normalized


def _flag_complete(df: pd.DataFrame, required_columns: list[str]) -> pd.Series:
    return (~df[required_columns].isna().any(axis=1)).astype(int)


def build_filing_estimation_sample(
    event_panel_path: str = DEFAULT_EVENT_PANEL,
    *,
    controls_path: str = DEFAULT_CONTROLS,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    panel = pd.read_parquet(event_panel_path)
    controls = pd.read_csv(controls_path, low_memory=False)

    for frame in (panel, controls):
        if "filing_id" in frame.columns:
            frame["filing_id"] = _normalize_string_key(frame["filing_id"])
        if "gvkey" in frame.columns:
            frame["gvkey"] = _normalize_string_key(frame["gvkey"])
        if "filing_date" in frame.columns:
            frame["filing_date"] = _normalize_string_key(frame["filing_date"])

    sample = panel.merge(controls, on=["filing_id"], how="left", suffixes=("", "_ctrl"))
    sample["sample_car_core"] = _flag_complete(sample, CORE_COLUMNS)
    sample["sample_car_extended"] = _flag_complete(sample, EXTENDED_COLUMNS)
    sample["sample_bhar_6m_core"] = _flag_complete(sample, BHAR_6M_COLUMNS)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_panel_path": str(Path(event_panel_path).resolve()),
        "controls_path": str(Path(controls_path).resolve()),
        "row_count": int(len(sample)),
        "sample_counts": {
            "sample_car_core": int(sample["sample_car_core"].sum()),
            "sample_car_extended": int(sample["sample_car_extended"].sum()),
            "sample_bhar_6m_core": int(sample["sample_bhar_6m_core"].sum()),
        },
        "nonmissing_counts": {
            column: int(sample[column].notna().sum())
            for column in ["car_m1_p1", "car_m2_p2", "bhar_6m", "ln_assets", "leverage", "cash", "roa", "rd_intensity", "capx_at", "sales_growth"]
        },
    }
    return sample, report


def write_sample(sample: pd.DataFrame, output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(resolved, index=False)


def write_report(report: dict[str, Any], report_path: str | Path) -> None:
    resolved = Path(report_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-panel", default=DEFAULT_EVENT_PANEL)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample, report = build_filing_estimation_sample(
        event_panel_path=args.event_panel,
        controls_path=args.controls,
    )
    write_sample(sample, args.output)
    write_report(report, args.report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
