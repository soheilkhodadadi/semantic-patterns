"""Post-extraction cleanup for canonical AI sentence parquet tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.core.sentence_filter import (
    clean_extracted_sentence,
    get_sentence_integrity_flags,
    is_artifact_only_ai_false_positive,
    normalize_sentence_text,
)


DEFAULT_INPUT_ROOT = "data/processed/sentences"
DEFAULT_OUTPUT_ROOT = "data/processed/sentences_clean"
DEFAULT_REPORT = "reports/data/sentence_cleanup_v1.json"
DEFAULT_YEARS = (2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024)
DEFAULT_MIN_TOKENS = 6
DEFAULT_MAX_TOKENS = 120
DEFAULT_MAX_FRAGMENT_SCORE = 0.0
INTEGRITY_FLAG_COUNT = 4

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
        r"\bpoint of beginning\b",
        r"\bdegrees?\s+\d+\s+minutes?\b",
    )
]
LEADING_NUMERIC_PREFIX_RE = re.compile(
    r"^\s*\d{1,3}\s+(?=(?:we|our|the|this|these|in|from|based|privacy|competitors|retaining)\b)",
    re.I,
)
SPACED_LETTERS_RE = re.compile(r"(?:\b[A-Za-z]\b(?:\s+|$)){8,}")
NOISY_TOKEN_RE = re.compile(r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d.,:/\\'\-]{5,}")
MIXED_GLYPH_RE = re.compile(r"[A-Za-z][^A-Za-z\s]{2,}[A-Za-z]|[A-Za-z]{1,3}[\\/][A-Za-z]{1,3}")


def _sha1_short(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _resolve_year_path(root: str | Path, year: int) -> Path:
    return Path(root) / f"year={int(year)}" / "ai_sentences.parquet"


def _is_table_like_sentence(text: str) -> bool:
    sentence = str(text or "")
    return any(pattern.search(sentence) for pattern in TABLE_LIKE_PATTERNS)


def _strip_leading_numeric_prefix(text: str) -> str:
    return LEADING_NUMERIC_PREFIX_RE.sub("", str(text or "")).strip()


def _looks_like_ocr_noise(text: str) -> bool:
    sentence = str(text or "").strip()
    if not sentence:
        return True
    if SPACED_LETTERS_RE.search(sentence):
        return True

    chars = [ch for ch in sentence if not ch.isspace()]
    if not chars:
        return True
    letters = sum(ch.isalpha() for ch in chars)
    non_letters = len(chars) - letters
    if non_letters / max(len(chars), 1) >= 0.58:
        return True

    tokens = [token.strip("()[]{}\"'.,;:") for token in sentence.split() if token.strip()]
    if not tokens:
        return True
    noisy_token_count = sum(
        1 for token in tokens if NOISY_TOKEN_RE.search(token) or MIXED_GLYPH_RE.search(token)
    )
    return len(tokens) >= 8 and (noisy_token_count / len(tokens)) >= 0.35


def _clean_sentence_text(text: str) -> str:
    cleaned = clean_extracted_sentence(text)
    cleaned = _strip_leading_numeric_prefix(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _cleanup_frame(
    frame: pd.DataFrame,
    *,
    min_tokens: int,
    max_tokens: int,
    max_fragment_score: float,
) -> tuple[pd.DataFrame, dict[str, int]]:
    working = frame.copy()
    working["sentence"] = working["sentence"].fillna("").astype(str).map(_clean_sentence_text)
    working["sentence_norm"] = working["sentence"].map(normalize_sentence_text)
    if "sentence_text_id" in working.columns:
        working["sentence_text_id"] = working["sentence_norm"].map(_sha1_short)
    flags = working["sentence"].map(lambda text: get_sentence_integrity_flags(text, min_tokens=min_tokens))
    working["integrity_flags"] = flags.map(lambda values: json.dumps(values, separators=(",", ":"), ensure_ascii=True))
    working["fragment_score"] = flags.map(
        lambda values: round(len(values) / INTEGRITY_FLAG_COUNT, 6)
    )
    working["token_count"] = (
        working["sentence"].fillna("").astype(str).str.split().map(len).astype(int)
    )

    working["_empty_after_clean"] = working["sentence"].astype(str).str.strip() == ""
    working["_table_like"] = working["sentence"].map(_is_table_like_sentence)
    working["_artifact_ai_false_positive"] = working["sentence"].map(
        is_artifact_only_ai_false_positive
    )
    working["_ocr_like"] = working["sentence"].map(_looks_like_ocr_noise)

    too_short_mask = working["_empty_after_clean"] | (
        working["token_count"].astype(int) < int(min_tokens)
    )
    too_long_mask = working["token_count"].astype(int) > int(max_tokens)
    fragment_mask = working["fragment_score"].astype(float) > float(max_fragment_score)
    table_like_mask = working["_table_like"].astype(bool)
    artifact_ai_mask = working["_artifact_ai_false_positive"].astype(bool)
    ocr_like_mask = working["_ocr_like"].astype(bool)
    keep_mask = ~(
        too_short_mask
        | too_long_mask
        | fragment_mask
        | table_like_mask
        | artifact_ai_mask
        | ocr_like_mask
    )

    cleaned = working.loc[keep_mask].copy()
    cleaned.drop(
        columns=[
            "_empty_after_clean",
            "_table_like",
            "_artifact_ai_false_positive",
            "_ocr_like",
        ],
        inplace=True,
    )

    return cleaned, {
        "rows_input": int(len(working)),
        "rows_retained": int(keep_mask.sum()),
        "rows_dropped": int((~keep_mask).sum()),
        "dropped_too_short": int(too_short_mask.sum()),
        "dropped_too_long": int(too_long_mask.sum()),
        "dropped_fragment_like": int(fragment_mask.sum()),
        "dropped_table_like": int(table_like_mask.sum()),
        "dropped_artifact_ai_false_positive": int(artifact_ai_mask.sum()),
        "dropped_ocr_like": int(ocr_like_mask.sum()),
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
