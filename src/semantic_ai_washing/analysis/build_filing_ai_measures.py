"""Build filing-level AI narrative measures from classified filing outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SPINE = "data/interim/market/filing_event_spine_v1.csv"
DEFAULT_OUTPUT = "data/interim/market/filing_ai_measures_v1.csv"
DEFAULT_REPORT = "reports/analysis/filing_ai_measures_v1.json"
CHATGPT_RELEASE_DATE = "20221130"

OUTPUT_COLUMNS = [
    "filing_id",
    "source_filename",
    "source_path",
    "filing_date",
    "filing_year",
    "form_type",
    "cik",
    "gvkey",
    "sentence_count",
    "n_actionable",
    "n_speculative",
    "n_irrelevant",
    "n_other",
    "n_ai_total",
    "share_actionable",
    "share_speculative",
    "share_irrelevant",
    "any_actionable",
    "any_speculative",
    "any_irrelevant",
    "post_chatgpt",
]

LABEL_MAP = {
    "actionable": "n_actionable",
    "speculative": "n_speculative",
    "irrelevant": "n_irrelevant",
}


def load_event_spine(path: str | Path) -> list[dict[str, str]]:
    resolved = Path(path)
    with resolved.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return []
        return [dict(row) for row in reader]


def is_post_chatgpt(filing_date: str) -> bool:
    return (filing_date or "") >= CHATGPT_RELEASE_DATE


def _blank_measure_row(spine_row: dict[str, str]) -> dict[str, str]:
    return {
        "filing_id": spine_row.get("filing_id", ""),
        "source_filename": spine_row.get("source_filename", ""),
        "source_path": spine_row.get("source_path", ""),
        "filing_date": spine_row.get("filing_date", ""),
        "filing_year": spine_row.get("filing_year", ""),
        "form_type": spine_row.get("form_type", ""),
        "cik": spine_row.get("cik", ""),
        "gvkey": spine_row.get("gvkey", ""),
        "sentence_count": "0",
        "n_actionable": "0",
        "n_speculative": "0",
        "n_irrelevant": "0",
        "n_other": "0",
        "n_ai_total": "0",
        "share_actionable": "0.0",
        "share_speculative": "0.0",
        "share_irrelevant": "0.0",
        "any_actionable": "0",
        "any_speculative": "0",
        "any_irrelevant": "0",
        "post_chatgpt": "1" if is_post_chatgpt(spine_row.get("filing_date", "")) else "0",
    }


def measure_filing(spine_row: dict[str, str]) -> dict[str, str]:
    row = _blank_measure_row(spine_row)
    source_path = Path(spine_row.get("source_path", ""))
    if not source_path.exists():
        raise FileNotFoundError(f"Missing classified filing output: {source_path}")

    counts = {column: 0 for column in ["n_actionable", "n_speculative", "n_irrelevant", "n_other"]}
    sentence_count = 0

    with source_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for classified_row in reader:
            sentence_count += 1
            label = str(classified_row.get("label_pred", "") or "").strip().lower()
            target_column = LABEL_MAP.get(label, "n_other")
            counts[target_column] += 1

    n_ai_total = counts["n_actionable"] + counts["n_speculative"] + counts["n_irrelevant"]
    denominator = n_ai_total if n_ai_total else 0

    row.update(
        {
            "sentence_count": str(sentence_count),
            "n_actionable": str(counts["n_actionable"]),
            "n_speculative": str(counts["n_speculative"]),
            "n_irrelevant": str(counts["n_irrelevant"]),
            "n_other": str(counts["n_other"]),
            "n_ai_total": str(n_ai_total),
            "share_actionable": f"{(counts['n_actionable'] / denominator) if denominator else 0.0:.6f}",
            "share_speculative": f"{(counts['n_speculative'] / denominator) if denominator else 0.0:.6f}",
            "share_irrelevant": f"{(counts['n_irrelevant'] / denominator) if denominator else 0.0:.6f}",
            "any_actionable": "1" if counts["n_actionable"] else "0",
            "any_speculative": "1" if counts["n_speculative"] else "0",
            "any_irrelevant": "1" if counts["n_irrelevant"] else "0",
        }
    )
    return row


def build_filing_ai_measures(spine_path: str = DEFAULT_SPINE) -> tuple[list[dict[str, str]], dict[str, Any]]:
    spine_rows = load_event_spine(spine_path)
    measure_rows = [measure_filing(spine_row) for spine_row in spine_rows]

    totals = {
        "sentence_count": sum(int(row["sentence_count"]) for row in measure_rows),
        "n_actionable": sum(int(row["n_actionable"]) for row in measure_rows),
        "n_speculative": sum(int(row["n_speculative"]) for row in measure_rows),
        "n_irrelevant": sum(int(row["n_irrelevant"]) for row in measure_rows),
        "n_other": sum(int(row["n_other"]) for row in measure_rows),
        "n_ai_total": sum(int(row["n_ai_total"]) for row in measure_rows),
    }

    filings_with_any_actionable = sum(int(row["any_actionable"]) for row in measure_rows)
    filings_with_any_speculative = sum(int(row["any_speculative"]) for row in measure_rows)
    filings_with_any_irrelevant = sum(int(row["any_irrelevant"]) for row in measure_rows)

    report = {
        "spine_path": str(Path(spine_path).resolve()),
        "row_count": len(measure_rows),
        "totals": totals,
        "filings_with_any_actionable": filings_with_any_actionable,
        "filings_with_any_speculative": filings_with_any_speculative,
        "filings_with_any_irrelevant": filings_with_any_irrelevant,
        "post_chatgpt_filing_count": sum(int(row["post_chatgpt"]) for row in measure_rows),
        "date_min": min((row["filing_date"] for row in measure_rows), default=""),
        "date_max": max((row["filing_date"] for row in measure_rows), default=""),
    }
    return measure_rows, report


def write_rows(rows: list[dict[str, str]], output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_report(report: dict[str, Any], report_path: str | Path) -> None:
    resolved = Path(report_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spine", default=DEFAULT_SPINE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, report = build_filing_ai_measures(spine_path=args.spine)
    write_rows(rows, args.output)
    write_report(report, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
