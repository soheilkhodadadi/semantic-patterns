"""Merge assistive labels from shard CSVs back into a master deferred review sheet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ASSISTIVE_COLUMNS = [
    "assistive_label",
    "assistive_confidence",
    "assistive_rationale",
    "assistive_model",
    "assistive_generated_at",
    "assistive_prompt_hash",
]


def _load_shard_rows(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False).copy()
    frame["sentence_id"] = frame["sentence_id"].astype(str)
    frame["assistive_label"] = frame["assistive_label"].fillna("").astype(str).str.strip()
    frame = frame.loc[frame["assistive_label"].ne("")].copy()
    keep = ["sentence_id", *[column for column in ASSISTIVE_COLUMNS if column in frame.columns]]
    return frame[keep].drop_duplicates("sentence_id", keep="last")


def run_merge(args: argparse.Namespace) -> dict[str, object]:
    master_path = Path(args.master_csv).resolve()
    output_path = Path(args.output_csv).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    master = pd.read_csv(master_path, low_memory=False).copy()
    master["sentence_id"] = master["sentence_id"].astype(str)

    shard_frames: list[pd.DataFrame] = []
    shard_rows: list[dict[str, object]] = []
    for shard_csv in args.shard_csv:
        shard_path = Path(shard_csv).resolve()
        shard = _load_shard_rows(shard_path)
        shard_frames.append(shard)
        shard_rows.append({"path": str(shard_path), "rows": int(len(shard))})

    merged_rows = 0
    if shard_frames:
        combined = pd.concat(shard_frames, ignore_index=True)
        duplicate_ids = combined["sentence_id"][combined["sentence_id"].duplicated()].unique().tolist()
        if duplicate_ids:
            raise ValueError(f"Duplicate sentence_id across shard outputs: {duplicate_ids[:5]}")
        combined = combined.set_index("sentence_id")
        matched = master["sentence_id"].isin(combined.index)
        merged_rows = int(matched.sum())
        for column in ASSISTIVE_COLUMNS:
            if column not in combined.columns:
                continue
            master.loc[matched, column] = combined.reindex(master.loc[matched, "sentence_id"])[column].tolist()

    master.to_csv(output_path, index=False)
    assistive_completed = int(
        master["assistive_label"].fillna("").astype(str).str.strip().ne("").sum()
    )
    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "master_csv": str(master_path),
            "shard_csv": [str(Path(value).resolve()) for value in args.shard_csv],
        },
        "outputs": {"output_csv": str(output_path)},
        "summary": {
            "rows_total": int(len(master)),
            "rows_merged_from_shards": merged_rows,
            "assistive_completed_rows": assistive_completed,
            "pending_rows": int(len(master) - assistive_completed),
        },
        "shards": shard_rows,
    }
    report_path = Path(args.output_report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master-csv", required=True)
    parser.add_argument("--shard-csv", nargs="+", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_merge(args)
    print(
        "[shadow-defer-shards] merged "
        f"assistive_completed={report['summary']['assistive_completed_rows']} "
        f"pending_rows={report['summary']['pending_rows']}"
    )
    print(f"[shadow-defer-shards] report -> {args.output_report}")


if __name__ == "__main__":
    main()
