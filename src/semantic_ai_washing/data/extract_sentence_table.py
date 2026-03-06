"""Extract a canonical sentence table from a bounded filing manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.core.sentence_filter import (
    filter_ai_sentences,
    get_sentence_integrity_flags,
    load_keywords,
    merge_page_fragments,
    merge_sentence_fragments,
    normalize_sentence_text,
    segment_sentences,
)
from semantic_ai_washing.data.index_sec_filings import SEC_SOURCE_HINT_FILE, resolve_sec_source

DEFAULT_MANIFEST = "data/manifests/filings/pilot_2024_10k_v1.csv"
DEFAULT_OUTPUT = "data/processed/sentences/year=2024/ai_sentences.parquet"
DEFAULT_SAMPLE_OUTPUT = "data/processed/sentences/year=2024/ai_sentences_sample.csv"
DEFAULT_REPORT = "reports/data/pilot_2024_sentence_quality.json"
DEFAULT_KEYWORDS = "data/metadata/ai_keywords.txt"
EXTRACTOR_VERSION = "sentence_table_v1"
INTEGRITY_FLAG_COUNT = 4

OUTPUT_COLUMNS = [
    "sentence_id",
    "sentence_text_id",
    "sentence",
    "sentence_norm",
    "source_file",
    "source_year",
    "source_quarter",
    "source_form",
    "source_cik",
    "sentence_index",
    "extractor_version",
    "keyword_version",
    "manifest_id",
    "source_window_id",
    "integrity_flags",
    "fragment_score",
    "token_count",
]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: str | Path) -> str:
    return _sha256_bytes(Path(path).read_bytes())


def _sha1_short(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _resolve_source_root(source_root: str) -> Path:
    return resolve_sec_source(source_root=source_root, hint_file=SEC_SOURCE_HINT_FILE)


def _token_count(text: str) -> int:
    return len([token for token in str(text).split() if token.strip()])


def _serialize_flags(flags: list[str]) -> str:
    return json.dumps(flags, separators=(",", ":"), ensure_ascii=True)


def _token_count_summary(tokens: list[int]) -> dict[str, Any]:
    if not tokens:
        return {"count": 0, "min": 0, "p50": 0.0, "mean": 0.0, "max": 0}
    series = pd.Series(tokens, dtype="float64")
    return {
        "count": int(series.shape[0]),
        "min": int(series.min()),
        "p50": float(series.median()),
        "mean": float(round(series.mean(), 6)),
        "max": int(series.max()),
    }


def _build_row(
    sentence: str,
    sentence_index: int,
    manifest_row: pd.Series,
    keyword_version: str,
    min_tokens: int,
) -> tuple[dict[str, Any], list[str]]:
    sentence_norm = normalize_sentence_text(sentence)
    flags = get_sentence_integrity_flags(sentence, min_tokens=min_tokens)
    row = {
        "sentence_id": _sha1_short(f"{manifest_row['path']}|{sentence_index}|{sentence_norm}"),
        "sentence_text_id": _sha1_short(sentence_norm),
        "sentence": sentence,
        "sentence_norm": sentence_norm,
        "source_file": str(manifest_row["path"]),
        "source_year": int(manifest_row["year"]),
        "source_quarter": int(manifest_row["quarter"]),
        "source_form": str(manifest_row["form"]),
        "source_cik": str(manifest_row["cik"]),
        "sentence_index": int(sentence_index),
        "extractor_version": EXTRACTOR_VERSION,
        "keyword_version": keyword_version,
        "manifest_id": str(manifest_row["manifest_id"]),
        "source_window_id": str(manifest_row["source_window_id"]),
        "integrity_flags": _serialize_flags(flags),
        "fragment_score": round(len(flags) / INTEGRITY_FLAG_COUNT, 6),
        "token_count": _token_count(sentence),
    }
    return row, flags


def extract_sentence_table(
    manifest_path: str = DEFAULT_MANIFEST,
    output_path: str = DEFAULT_OUTPUT,
    sample_output_path: str = DEFAULT_SAMPLE_OUTPUT,
    report_path: str = DEFAULT_REPORT,
    source_root: str = "",
    keywords_path: str = DEFAULT_KEYWORDS,
    min_tokens: int = 6,
    sample_size: int = 200,
) -> dict[str, Any]:
    manifest = pd.read_csv(
        manifest_path, dtype={"cik": str, "filename": str, "path": str, "form": str}
    )
    if manifest.empty:
        raise ValueError(f"Manifest is empty: {manifest_path}")

    root = _resolve_source_root(source_root)
    if not root.exists():
        raise FileNotFoundError(f"SEC source root not found: {root}")

    keyword_file = Path(keywords_path)
    if not keyword_file.exists():
        raise FileNotFoundError(f"Keyword file not found: {keyword_file}")

    keywords = load_keywords(str(keyword_file))
    if not keywords:
        raise ValueError(f"Keyword file is empty: {keyword_file}")
    keyword_version = _sha256_file(keyword_file)

    rows: list[dict[str, Any]] = []
    failed_files: list[dict[str, str]] = []
    integrity_counts: Counter[str] = Counter()
    total_segmented_sentences = 0
    total_ai_sentences = 0

    for manifest_row in manifest.itertuples(index=False):
        relative_path = Path(str(manifest_row.path))
        filing_path = root / relative_path
        try:
            text = filing_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
            failed_files.append(
                {
                    "path": relative_path.as_posix(),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue

        segmented = segment_sentences(text)
        total_segmented_sentences += len(segmented)
        page_merged = merge_page_fragments(segmented, raw_text=text)
        merged = merge_sentence_fragments(page_merged)
        ai_sentences = filter_ai_sentences(merged, keywords)
        total_ai_sentences += len(ai_sentences)

        manifest_series = pd.Series(manifest_row._asdict())
        for idx, sentence in enumerate(ai_sentences, start=1):
            row, flags = _build_row(
                sentence=sentence,
                sentence_index=idx,
                manifest_row=manifest_series,
                keyword_version=keyword_version,
                min_tokens=min_tokens,
            )
            rows.append(row)
            integrity_counts.update(flags)

    sentence_table = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    if not sentence_table.empty:
        sentence_table.sort_values(
            by=["source_file", "sentence_index", "sentence_id"],
            inplace=True,
        )
        sentence_table.reset_index(drop=True, inplace=True)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sentence_table.to_parquet(output, index=False, engine="pyarrow", compression="snappy")

    sample_output = Path(sample_output_path)
    sample_output.parent.mkdir(parents=True, exist_ok=True)
    sample_rows = sentence_table.head(sample_size)
    sample_rows.to_csv(sample_output, index=False)

    manifest_id = (
        str(manifest["manifest_id"].iloc[0])
        if "manifest_id" in manifest.columns and not manifest.empty
        else ""
    )
    fragment_like_count = (
        int((sentence_table["fragment_score"] > 0).sum()) if not sentence_table.empty else 0
    )
    known_ff12 = 0
    unknown_ff12 = 0
    if "industry_metadata_source" in manifest.columns:
        known_ff12 = int((manifest["industry_metadata_source"] != "unknown").sum())
        unknown_ff12 = int((manifest["industry_metadata_source"] == "unknown").sum())

    report = {
        "manifest_metadata": {
            "manifest_id": manifest_id,
            "target_size": int(len(manifest)),
            "filings_attempted": int(len(manifest)),
            "filings_succeeded": int(len(manifest) - len(failed_files)),
            "filings_failed": int(len(failed_files)),
        },
        "extraction_counts": {
            "total_segmented_sentences": int(total_segmented_sentences),
            "total_ai_sentences_retained": int(total_ai_sentences),
            "average_ai_sentences_per_filing": float(
                round(total_ai_sentences / max(len(manifest) - len(failed_files), 1), 6)
            ),
        },
        "quality_metrics": {
            "fragment_rate": float(round(fragment_like_count / max(len(sentence_table), 1), 6))
            if len(sentence_table) > 0
            else 0.0,
            "integrity_flag_counts": dict(sorted(integrity_counts.items())),
            "token_count_summary": _token_count_summary(
                sentence_table["token_count"].astype(int).tolist()
                if not sentence_table.empty
                else []
            ),
        },
        "coverage_metrics": {
            "quarter_counts": {
                str(int(quarter)): int(count)
                for quarter, count in manifest["quarter"]
                .astype(int)
                .value_counts()
                .sort_index()
                .items()
            },
            "ff12_known_filing_count": known_ff12,
            "ff12_unknown_filing_count": unknown_ff12,
        },
        "failure_summary": {
            "read_errors_count": int(len(failed_files)),
            "failed_files": failed_files,
        },
        "output_fingerprints": {
            "parquet_sha256": _sha256_file(output),
            "sample_csv_sha256": _sha256_file(sample_output),
        },
    }

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--sample-output", default=DEFAULT_SAMPLE_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--source-root", default="")
    parser.add_argument("--keywords", default=DEFAULT_KEYWORDS)
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--sample-size", type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = extract_sentence_table(
        manifest_path=args.manifest,
        output_path=args.output,
        sample_output_path=args.sample_output,
        report_path=args.report,
        source_root=args.source_root,
        keywords_path=args.keywords,
        min_tokens=args.min_tokens,
        sample_size=args.sample_size,
    )
    print(f"[i] Wrote sentence table: {args.output}")
    print(f"[i] Wrote sentence sample: {args.sample_output}")
    print(f"[i] Wrote sentence quality report: {args.report}")
    print(
        "[i] AI sentences retained: "
        f"{report['extraction_counts']['total_ai_sentences_retained']:,}"
    )


if __name__ == "__main__":
    main()
