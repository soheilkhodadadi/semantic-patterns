"""Benchmark default vs fast sentence segmentation on a bounded filing sample."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.data.extract_sentence_table import extract_sentence_table


def _load_sample_manifest(
    *,
    index_csv: str | Path,
    year: int,
    form: str,
    sample_filings: int,
) -> pd.DataFrame:
    frame = pd.read_csv(index_csv, dtype={"cik": str, "form": str, "path": str})
    filtered = frame[
        (frame["year"].astype(int) == int(year))
        & (frame["form"].fillna("").astype(str).str.upper() == str(form).upper())
    ].copy()
    filtered = (
        filtered.sort_values(["quarter", "cik", "filename"]).head(int(sample_filings)).copy()
    )
    if filtered.empty:
        raise ValueError(f"No filings found for year={year} form={form}")
    filtered["manifest_id"] = f"segmentation_benchmark_{year}_{str(form).lower()}"
    filtered["source_window_id"] = filtered.get("source_window_id", "historical_2000_2020")
    return filtered[
        ["cik", "year", "quarter", "form", "filename", "path", "manifest_id", "source_window_id"]
    ]


def _quality_summary(output_path: str | Path) -> dict[str, Any]:
    frame = pd.read_parquet(output_path)
    token_series = (
        frame["token_count"].astype(int) if not frame.empty else pd.Series([], dtype=int)
    )
    return {
        "rows_retained": int(len(frame)),
        "fragment_like_rows": int((frame["fragment_score"].astype(float) > 0).sum())
        if not frame.empty
        else 0,
        "token_summary": {
            "min": int(token_series.min()) if not token_series.empty else 0,
            "median": float(token_series.median()) if not token_series.empty else 0.0,
            "mean": float(round(token_series.mean(), 4)) if not token_series.empty else 0.0,
            "max": int(token_series.max()) if not token_series.empty else 0,
        },
    }


def benchmark_modes(args: argparse.Namespace) -> dict[str, Any]:
    manifest = _load_sample_manifest(
        index_csv=args.index_csv,
        year=int(args.year),
        form=args.form,
        sample_filings=int(args.sample_filings),
    )

    results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="segmentation_benchmark_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        manifest_path = tmp_root / "manifest.csv"
        manifest.to_csv(manifest_path, index=False)

        for mode in ("default", "fast"):
            output_path = tmp_root / f"sentences_{mode}.parquet"
            sample_output = tmp_root / f"sample_{mode}.csv"
            report_path = tmp_root / f"report_{mode}.json"

            started = time.perf_counter()
            report = extract_sentence_table(
                manifest_path=str(manifest_path),
                output_path=str(output_path),
                sample_output_path=str(sample_output),
                report_path=str(report_path),
                source_root=args.source_root,
                keywords_path=args.keywords_path,
                min_tokens=int(args.min_tokens),
                max_tokens=int(args.max_tokens),
                max_fragment_score=float(args.max_fragment_score),
                segmentation_mode=mode,
                sample_size=int(args.sample_size),
            )
            elapsed = time.perf_counter() - started
            results[mode] = {
                "runtime_seconds": round(elapsed, 4),
                "report": report,
                "quality_summary": _quality_summary(output_path),
            }

    summary = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "index_csv": str(Path(args.index_csv).resolve()),
            "source_root": str(args.source_root),
            "year": int(args.year),
            "form": str(args.form),
            "sample_filings": int(args.sample_filings),
            "min_tokens": int(args.min_tokens),
            "max_tokens": int(args.max_tokens),
            "max_fragment_score": float(args.max_fragment_score),
        },
        "results": results,
    }

    output_report = Path(args.output_report)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-csv", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--form", default="10-K")
    parser.add_argument("--sample-filings", type=int, default=50)
    parser.add_argument("--keywords-path", default="data/metadata/ai_keywords.txt")
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument("--max-fragment-score", type=float, default=0.0)
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument(
        "--output-report",
        default="reports/data/segmentation_mode_benchmark_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = benchmark_modes(args)
    default_rt = summary["results"]["default"]["runtime_seconds"]
    fast_rt = summary["results"]["fast"]["runtime_seconds"]
    print(
        "[segmentation-benchmark] "
        f"default={default_rt}s fast={fast_rt}s report={args.output_report}"
    )


if __name__ == "__main__":
    main()
