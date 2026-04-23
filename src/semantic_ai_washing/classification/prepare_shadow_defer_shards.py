"""Prepare non-overlapping shard CSVs from a deferred shadow review sheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _to_bool_series(series: pd.Series) -> pd.Series:
    return (
        series.fillna(True)
        .map(lambda value: str(value).strip().lower() not in {"false", "0", "no", "n", ""})
        .astype(bool)
    )


def _pending_mask(frame: pd.DataFrame) -> pd.Series:
    canonical_mask = frame["label"].fillna("").astype(str).str.strip().ne("")
    assistive_mask = frame["assistive_label"].fillna("").astype(str).str.strip().ne("")
    sentence_blank_mask = frame["sentence"].fillna("").astype(str).str.strip().eq("")
    if "prelabel_eligible" in frame.columns:
        eligible_mask = _to_bool_series(frame["prelabel_eligible"])
    else:
        eligible_mask = pd.Series(True, index=frame.index, dtype=bool)
    return ~canonical_mask & ~assistive_mask & eligible_mask & ~sentence_blank_mask


def run_prepare(args: argparse.Namespace) -> dict[str, object]:
    input_path = Path(args.input_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(input_path, low_memory=False).copy()
    frame["sentence_id"] = frame["sentence_id"].astype(str)

    pending = frame.loc[_pending_mask(frame)].copy()
    pending = pending.sort_values(
        ["source_year", "source_file", "sentence_index", "sentence_id"]
    ).reset_index(drop=True)

    shard_count = int(args.shard_count)
    pending["shadow_shard_id"] = (pending.index % shard_count) + 1

    shard_rows: list[dict[str, object]] = []
    shard_paths: list[str] = []
    for shard_id in range(1, shard_count + 1):
        shard = pending.loc[pending["shadow_shard_id"] == shard_id].copy()
        shard_path = output_dir / f"{args.prefix}_shard{shard_id:02d}.csv"
        shard.to_csv(shard_path, index=False)
        shard_paths.append(str(shard_path))
        shard_rows.append(
            {
                "shard_id": shard_id,
                "rows": int(len(shard)),
                "output_csv": str(shard_path),
            }
        )

    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "input_csv": str(input_path),
            "shard_count": shard_count,
        },
        "outputs": {
            "output_dir": str(output_dir),
            "prefix": args.prefix,
            "shard_paths": shard_paths,
        },
        "summary": {
            "rows_total": int(len(frame)),
            "rows_pending": int(len(pending)),
            "rows_completed_assistive": int(
                frame["assistive_label"].fillna("").astype(str).str.strip().ne("").sum()
            ),
            "rows_completed_canonical": int(
                frame["label"].fillna("").astype(str).str.strip().ne("").sum()
            ),
        },
        "shards": shard_rows,
    }
    report_path = Path(args.output_report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--prefix", default="selective_defer_conf49_shadow_full_corpus_v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_prepare(args)
    print(
        "[shadow-defer-shards] prepared "
        f"pending_rows={report['summary']['rows_pending']} "
        f"shards={len(report['shards'])}"
    )
    print(f"[shadow-defer-shards] report -> {args.output_report}")


if __name__ == "__main__":
    main()
