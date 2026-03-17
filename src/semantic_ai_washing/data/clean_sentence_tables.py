"""Post-extraction cleanup for canonical AI sentence parquet tables."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_INPUT_ROOT = "data/processed/sentences"
DEFAULT_OUTPUT_ROOT = "data/processed/sentences_clean"
DEFAULT_REPORT = "reports/data/sentence_cleanup_v1.json"
DEFAULT_YEARS = (2016, 2021, 2022, 2023, 2024)
DEFAULT_MIN_TOKENS = 6
DEFAULT_MAX_TOKENS = 120
DEFAULT_MAX_FRAGMENT_SCORE = 0.0

TABLE_LIKE_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in (
        r"\bexhibit\s+a\b",
        r"\bconsolidated schedule of investments\b",
        r"\basserting party\b",
        r"\bmortgage trust\b",
        r"\bservicing platform applicable certification period\b",
        r"\bsecuritization transaction\b",
        r"\bstart date end date\b",
        r"\bform 10-d\b",
    )
]


def _resolve_year_path(root: str | Path, year: int) -> Path:
    return Path(root) / f"year={int(year)}" / "ai_sentences.parquet"


def _is_table_like_sentence(text: str) -> bool:
    sentence = str(text or "")
    return any(pattern.search(sentence) for pattern in TABLE_LIKE_PATTERNS)


def _cleanup_frame(
    frame: pd.DataFrame,
    *,
    min_tokens: int,
    max_tokens: int,
    max_fragment_score: float,
) -> tuple[pd.DataFrame, dict[str, int]]:
    working = frame.copy()
    if "token_count" not in working.columns:
        working["token_count"] = (
            working["sentence"].fillna("").astype(str).str.split().map(len).astype(int)
        )
    if "fragment_score" not in working.columns:
        working["fragment_score"] = 0.0

    working["_table_like"] = working["sentence"].fillna("").astype(str).map(_is_table_like_sentence)

    too_short_mask = working["token_count"].astype(int) < int(min_tokens)
    too_long_mask = working["token_count"].astype(int) > int(max_tokens)
    fragment_mask = working["fragment_score"].astype(float) > float(max_fragment_score)
    table_like_mask = working["_table_like"].astype(bool)
    keep_mask = ~(too_short_mask | too_long_mask | fragment_mask | table_like_mask)

    cleaned = working.loc[keep_mask].copy()
    cleaned.drop(columns=["_table_like"], inplace=True)

    return cleaned, {
        "rows_input": int(len(working)),
        "rows_retained": int(keep_mask.sum()),
        "rows_dropped": int((~keep_mask).sum()),
        "dropped_too_short": int(too_short_mask.sum()),
        "dropped_too_long": int(too_long_mask.sum()),
        "dropped_fragment_like": int(fragment_mask.sum()),
        "dropped_table_like": int(table_like_mask.sum()),
    }


def clean_sentence_tables(args: argparse.Namespace) -> dict[str, Any]:
    years = [int(year) for year in args.years]
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    per_year: dict[str, Any] = {}
    summary_rows_input = 0
    summary_rows_retained = 0

    for year in years:
        input_path = _resolve_year_path(args.input_root, year)
        if not input_path.exists():
            per_year[str(year)] = {
                "status": "missing_input",
                "input_path": str(input_path),
            }
            continue

        frame = pd.read_parquet(input_path)
        cleaned, stats = _cleanup_frame(
            frame,
            min_tokens=int(args.min_tokens),
            max_tokens=int(args.max_tokens),
            max_fragment_score=float(args.max_fragment_score),
        )
        output_path = _resolve_year_path(output_root, year)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")

        per_year[str(year)] = {
            "status": "cleaned",
            "input_path": str(input_path),
            "output_path": str(output_path),
            **stats,
        }
        summary_rows_input += int(stats["rows_input"])
        summary_rows_retained += int(stats["rows_retained"])

    report = {
        "status": "passed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "years_requested": years,
            "rows_input": int(summary_rows_input),
            "rows_retained": int(summary_rows_retained),
            "rows_dropped": int(summary_rows_input - summary_rows_retained),
            "min_tokens": int(args.min_tokens),
            "max_tokens": int(args.max_tokens),
            "max_fragment_score": float(args.max_fragment_score),
            "output_root": str(output_root),
        },
        "years": per_year,
    }

    report_path = Path(args.output_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--output-report", default=DEFAULT_REPORT)
    parser.add_argument("--years", nargs="+", default=[str(year) for year in DEFAULT_YEARS])
    parser.add_argument("--min-tokens", type=int, default=DEFAULT_MIN_TOKENS)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--max-fragment-score", type=float, default=DEFAULT_MAX_FRAGMENT_SCORE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = clean_sentence_tables(args)
    print(
        "[sentence-cleanup] "
        f"rows_retained={report['summary']['rows_retained']} "
        f"rows_dropped={report['summary']['rows_dropped']}"
    )
    print(f"[sentence-cleanup] report -> {args.output_report}")


if __name__ == "__main__":
    main()
