"""Merge assistive deferred labels back into local shadow classification outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ASSISTIVE_MERGE_COLUMNS = [
    "assistive_label",
    "assistive_confidence",
    "assistive_rationale",
    "assistive_model",
    "assistive_generated_at",
    "assistive_prompt_hash",
]


def _load_assistive_rows(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path).copy()
    required = {"sentence_id", "assistive_label"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Deferred review sheet missing required columns: {missing}")
    frame["sentence_id"] = frame["sentence_id"].astype(str)
    frame["assistive_label"] = frame["assistive_label"].fillna("").astype(str).str.strip()
    frame = frame.loc[frame["assistive_label"].ne("")].copy()
    keep = ["sentence_id", *[col for col in ASSISTIVE_MERGE_COLUMNS if col in frame.columns]]
    return frame[keep].drop_duplicates("sentence_id", keep="last")


def run_merge(args: argparse.Namespace) -> dict[str, object]:
    years = [int(value) for value in args.years]
    deferred = _load_assistive_rows(args.deferred_csv)
    deferred_lookup = deferred.set_index("sentence_id")
    year_rows: dict[str, dict[str, object]] = {}
    total_rows = 0
    total_api_rows = 0

    for year in years:
        input_path = (
            Path(args.input_root)
            / f"year={year}"
            / f"model={args.input_model_id}"
            / "classified_sentences.parquet"
        )
        if not input_path.exists():
            raise FileNotFoundError(f"Missing local classification for year={year}: {input_path}")
        frame = pd.read_parquet(input_path).copy()
        frame["sentence_id"] = frame["sentence_id"].astype(str)
        matched = frame["sentence_id"].isin(deferred_lookup.index)
        api_rows = int(matched.sum())
        if api_rows:
            assistive = deferred_lookup.reindex(frame.loc[matched, "sentence_id"].tolist())
            frame.loc[matched, "predicted_label"] = assistive["assistive_label"].tolist()
            frame.loc[matched, "prediction_source"] = "api_a"
            frame.loc[matched, "deferred_to_api"] = True
            frame.loc[matched, "api_a_label"] = assistive["assistive_label"].tolist()
            for column in ASSISTIVE_MERGE_COLUMNS:
                if column == "assistive_label" or column not in assistive.columns:
                    continue
                target_column = {
                    "assistive_confidence": "api_a_confidence",
                    "assistive_rationale": "api_a_rationale",
                    "assistive_model": "api_a_model",
                }.get(column, column)
                frame.loc[matched, target_column] = assistive[column].tolist()

        output_path = (
            Path(args.output_root)
            / f"year={year}"
            / f"model={args.output_model_id}"
            / "classified_sentences.parquet"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(output_path, index=False)
        rows = int(len(frame))
        year_rows[str(year)] = {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "rows": rows,
            "api_rows": api_rows,
            "api_rate": (api_rows / rows) if rows else 0.0,
        }
        total_rows += rows
        total_api_rows += api_rows

    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "inputs": {
            "input_root": str(Path(args.input_root).resolve()),
            "input_model_id": str(args.input_model_id),
            "deferred_csv": str(Path(args.deferred_csv).resolve()),
            "years": years,
        },
        "outputs": {
            "output_root": str(Path(args.output_root).resolve()),
            "output_model_id": str(args.output_model_id),
        },
        "summary": {
            "rows_total": total_rows,
            "api_rows_total": total_api_rows,
            "api_rate_total": (total_api_rows / total_rows) if total_rows else 0.0,
        },
        "years": year_rows,
    }
    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--input-model-id", required=True)
    parser.add_argument("--years", nargs="+", required=True)
    parser.add_argument("--deferred-csv", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--output-model-id", required=True)
    parser.add_argument("--output-report", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_merge(args)
    print(
        "[shadow-defer-merge] merged "
        f"api_rows={report['summary']['api_rows_total']} "
        f"rate={report['summary']['api_rate_total']:.4f}"
    )
    print(f"[shadow-defer-merge] report -> {args.output_report}")


if __name__ == "__main__":
    main()
