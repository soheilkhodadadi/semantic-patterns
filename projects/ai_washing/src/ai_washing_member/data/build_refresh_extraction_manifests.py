"""Build quarter-bounded extraction manifests for a bounded annual refresh window."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_INDEX = "data/metadata/available_filings_index_2025_refresh_v1.csv"
DEFAULT_SOURCE_WINDOW_ID = "annual_10k_2025_refresh_v1"
DEFAULT_YEAR = 2025
DEFAULT_FORMS = ("10-K",)
DEFAULT_OUTPUT_DIR = "data/manifests/filings/annual_10k_2025_refresh_v1"
DEFAULT_REPORT = "reports/data/annual_10k_2025_refresh_manifest_summary_v1.json"

MANIFEST_COLUMNS = [
    "manifest_id",
    "cik",
    "year",
    "quarter",
    "form",
    "filename",
    "path",
    "source_window_id",
]


def build_manifests(args: argparse.Namespace) -> dict[str, Any]:
    frame = pd.read_csv(
        args.index_csv,
        dtype={"cik": str, "filename": str, "path": str, "form": str, "source_window_id": str},
    )
    required = {"cik", "year", "quarter", "form", "filename", "path", "source_window_id"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Refresh index is missing required columns: {missing}")

    filtered = frame.loc[
        (frame["source_window_id"].astype(str) == str(args.source_window_id))
        & (frame["year"].astype(int) == int(args.year))
        & (frame["form"].astype(str).str.upper().isin({str(v).upper() for v in args.forms}))
    ].copy()
    if filtered.empty:
        raise ValueError(
            "No rows matched the requested refresh extraction scope. "
            f"window={args.source_window_id} year={args.year} forms={list(args.forms)}"
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    quarter_outputs: dict[str, Any] = {}
    for quarter in sorted(filtered["quarter"].astype(int).unique().tolist()):
        quarter_frame = filtered.loc[filtered["quarter"].astype(int) == int(quarter)].copy()
        manifest_id = f"{args.source_window_id}_y{int(args.year)}_q{int(quarter)}"
        quarter_frame["manifest_id"] = manifest_id
        quarter_frame = quarter_frame[
            [
                "manifest_id",
                "cik",
                "year",
                "quarter",
                "form",
                "filename",
                "path",
                "source_window_id",
            ]
        ].sort_values(["form", "cik", "filename"])

        output_path = output_dir / f"manifest_y{int(args.year)}_q{int(quarter)}.csv"
        quarter_frame.to_csv(output_path, index=False)
        quarter_outputs[str(int(quarter))] = {
            "manifest_id": manifest_id,
            "path": str(output_path),
            "row_count": int(len(quarter_frame)),
            "forms": sorted(quarter_frame["form"].astype(str).str.upper().unique().tolist()),
        }

    report = {
        "status": "built",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": "built",
            "source_window_id": str(args.source_window_id),
            "year": int(args.year),
            "forms": [str(value).upper() for value in args.forms],
            "manifest_count": len(quarter_outputs),
            "total_rows": int(len(filtered)),
            "quarters": sorted(int(key) for key in quarter_outputs),
        },
        "manifests": quarter_outputs,
    }

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-csv", default=DEFAULT_INDEX)
    parser.add_argument("--source-window-id", default=DEFAULT_SOURCE_WINDOW_ID)
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--forms", nargs="+", default=list(DEFAULT_FORMS))
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-path", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_manifests(args)
    print(
        "[refresh-manifests] built "
        f"manifests={report['summary']['manifest_count']} rows={report['summary']['total_rows']}"
    )
    print(f"[refresh-manifests] output_dir -> {args.output_dir}")


if __name__ == "__main__":
    main()
