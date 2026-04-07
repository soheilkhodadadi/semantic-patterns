"""Restartable quarter-batch sentence extraction for a bounded annual refresh year."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.data.extract_sentence_table import (
    DEFAULT_MAX_TOKENS,
    extract_sentence_table,
)

DEFAULT_MANIFEST_DIR = "data/manifests/filings/annual_10k_2025_refresh_v1"
DEFAULT_SOURCE_ROOT = "/Users/soheilkhodadadi/DataWork/10-X_C_2025_staged_v1"
DEFAULT_YEAR = 2025
DEFAULT_OUTPUT_ROOT = "data/processed/sentences_refresh_2025_v1"
DEFAULT_REPORT = "reports/data/annual_10k_2025_refresh_extraction_v1.json"
DEFAULT_PROGRESS = "reports/data/annual_10k_2025_refresh_extraction_progress_v1.json"
DEFAULT_KEYWORDS = "data/metadata/ai_keywords.txt"


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _batch_output_dir(output_root: str | Path, year: int, quarter: int) -> Path:
    return Path(output_root) / f"year={int(year)}" / "_batches" / f"quarter={int(quarter)}"


def _combined_output_path(output_root: str | Path, year: int) -> Path:
    return Path(output_root) / f"year={int(year)}" / "ai_sentences.parquet"


def _batch_report_path(output_root: str | Path, year: int, quarter: int) -> Path:
    return _batch_output_dir(output_root, year, quarter) / "report.json"


def _load_batch_manifest_paths(manifest_dir: str | Path, year: int) -> list[tuple[int, Path]]:
    root = Path(manifest_dir)
    paths = []
    for path in sorted(root.glob(f"manifest_y{int(year)}_q*.csv")):
        quarter = int(path.stem.split("_q")[-1])
        paths.append((quarter, path))
    if not paths:
        raise FileNotFoundError(f"No refresh manifests found under {root} for year={year}")
    return paths


def _combine_batch_outputs(
    output_root: str | Path, year: int, batch_quarters: list[int]
) -> dict[str, Any]:
    frames: list[pd.DataFrame] = []
    total_rows = 0
    for quarter in batch_quarters:
        batch_path = _batch_output_dir(output_root, year, quarter) / "ai_sentences.parquet"
        if not batch_path.exists():
            raise FileNotFoundError(f"Missing batch output for quarter={quarter}: {batch_path}")
        frame = pd.read_parquet(batch_path)
        total_rows += int(len(frame))
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    combined.sort_values(["source_file", "sentence_index", "sentence_id"], inplace=True)
    combined.reset_index(drop=True, inplace=True)
    output_path = _combined_output_path(output_root, year)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output_path, index=False)
    return {
        "output_path": str(output_path),
        "row_count": int(len(combined)),
        "input_row_count": int(total_rows),
    }


def run_extraction(args: argparse.Namespace) -> dict[str, Any]:
    manifest_paths = _load_batch_manifest_paths(args.manifest_dir, args.year)
    completed_quarters: list[int] = []
    batch_state: dict[str, Any] = {}

    _write_json(
        args.progress_report,
        {
            "status": "starting",
            "generated_at_utc": _now_utc(),
            "summary": {
                "status": "starting",
                "year": int(args.year),
                "quarters_requested": [quarter for quarter, _ in manifest_paths],
                "quarters_completed": completed_quarters,
                "current_quarter": None,
                "output_root": str(args.output_root),
            },
            "quarters": batch_state,
        },
    )

    for quarter, manifest_path in manifest_paths:
        batch_dir = _batch_output_dir(args.output_root, args.year, quarter)
        batch_output_path = batch_dir / "ai_sentences.parquet"
        batch_sample_path = batch_dir / "ai_sentences_sample.csv"
        batch_report_path = _batch_report_path(args.output_root, args.year, quarter)
        batch_dir.mkdir(parents=True, exist_ok=True)

        if batch_output_path.exists() and batch_report_path.exists():
            report = json.loads(batch_report_path.read_text(encoding="utf-8"))
            batch_state[str(quarter)] = {
                "status": "reused",
                "manifest_path": str(manifest_path),
                "output_path": str(batch_output_path),
                "row_count": int(
                    report.get("extraction_counts", {}).get("clean_sentence_rows", 0)
                ),
            }
            completed_quarters.append(quarter)
            continue

        _write_json(
            args.progress_report,
            {
                "status": "running",
                "generated_at_utc": _now_utc(),
                "summary": {
                    "status": "running",
                    "year": int(args.year),
                    "quarters_requested": [value for value, _ in manifest_paths],
                    "quarters_completed": completed_quarters,
                    "current_quarter": int(quarter),
                    "output_root": str(args.output_root),
                },
                "quarters": batch_state,
            },
        )

        report = extract_sentence_table(
            manifest_path=str(manifest_path),
            output_path=str(batch_output_path),
            sample_output_path=str(batch_sample_path),
            report_path=str(batch_report_path),
            source_root=args.source_root,
            keywords_path=args.keywords_path,
            min_tokens=int(args.min_tokens),
            max_tokens=int(args.max_tokens),
            segmentation_mode=str(args.segmentation_mode),
            sample_size=int(args.sample_size),
        )
        batch_state[str(quarter)] = {
            "status": "completed",
            "manifest_path": str(manifest_path),
            "output_path": str(batch_output_path),
            "row_count": int(report.get("extraction_counts", {}).get("clean_sentence_rows", 0)),
        }
        completed_quarters.append(quarter)

    combined = _combine_batch_outputs(args.output_root, args.year, [q for q, _ in manifest_paths])
    final_report = {
        "status": "passed",
        "generated_at_utc": _now_utc(),
        "summary": {
            "status": "passed",
            "year": int(args.year),
            "quarters_requested": [quarter for quarter, _ in manifest_paths],
            "quarters_completed": completed_quarters,
            "combined_output_path": combined["output_path"],
            "combined_row_count": combined["row_count"],
        },
        "quarters": batch_state,
        "combined": combined,
    }
    _write_json(args.output_report, final_report)
    _write_json(
        args.progress_report,
        {
            "status": "completed",
            "generated_at_utc": _now_utc(),
            "summary": final_report["summary"],
            "quarters": batch_state,
        },
    )
    return final_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", default=DEFAULT_MANIFEST_DIR)
    parser.add_argument("--source-root", default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--progress-report", default=DEFAULT_PROGRESS)
    parser.add_argument("--keywords-path", default=DEFAULT_KEYWORDS)
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--segmentation-mode", choices=["default", "fast"], default="default")
    parser.add_argument("--sample-size", type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_extraction(args)
    print(
        "[refresh-extract] extracted "
        f"year={report['summary']['year']} rows={report['summary']['combined_row_count']}"
    )
    print(f"[refresh-extract] combined_output -> {report['summary']['combined_output_path']}")


if __name__ == "__main__":
    main()
