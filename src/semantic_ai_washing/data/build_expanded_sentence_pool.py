"""Build the expanded 2024 filing manifest and clean AI sentence pool for Iteration 2."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
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
from semantic_ai_washing.data.build_filing_manifest import (
    OUTPUT_COLUMNS as MANIFEST_COLUMNS,
    DEFAULT_CONTROLS,
    DEFAULT_CROSSWALK,
    compute_manifest_row_id,
    normalize_cik,
    _prepare_candidates,
)
from semantic_ai_washing.data.extract_sentence_table import (
    DEFAULT_KEYWORDS,
    EXTRACTOR_VERSION,
    OUTPUT_COLUMNS as SENTENCE_COLUMNS,
)
from semantic_ai_washing.data.index_sec_filings import SEC_SOURCE_HINT_FILE, resolve_sec_source

DEFAULT_INDEX = "data/metadata/available_filings_index.csv"
DEFAULT_MANIFEST = "data/manifests/filings/expansion_2024_500_firms_v1.csv"
DEFAULT_SENTENCE_OUTPUT = "data/processed/sentences/year=2024/expanded_ai_sentences.parquet"
DEFAULT_REPORT = "reports/labels/sentence_pool_expansion_2024_summary.json"
DEFAULT_MANIFEST_ID = "expansion_2024_500_firms_v1"
DEFAULT_YEAR = 2024
DEFAULT_FORM = "10-K"
DEFAULT_TARGET_FIRMS = 500
DEFAULT_MIN_CLEAN_SENTENCES = 1000
DEFAULT_MIN_TOKENS = 6
DEFAULT_MAX_TOKENS = 120
DEFAULT_SAMPLE_SEED = 20260307
_INTEGRITY_FLAG_COUNT = 4


def _sha1_short(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _token_count(text: str) -> int:
    return len([token for token in str(text).split() if token.strip()])


def _serialize_flags(flags: list[str]) -> str:
    return json.dumps(flags, separators=(",", ":"), ensure_ascii=True)


def _has_keyword_hit(filing_text: str, keywords: list[str]) -> bool:
    lowered = filing_text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _ordered_unique_firm_rows(candidates: pd.DataFrame) -> list[pd.Series]:
    quarter_frames: dict[int, deque[pd.Series]] = {}
    for quarter in sorted(candidates["quarter"].astype(int).unique().tolist()):
        frame = candidates[candidates["quarter"].astype(int) == int(quarter)].copy()
        frame = frame.drop_duplicates(subset=["cik"], keep="first")
        quarter_frames[int(quarter)] = deque(
            row for _, row in frame.sort_values(["ff12_sort", "cik", "filename"]).iterrows()
        )

    ordered: list[pd.Series] = []
    while any(queue for queue in quarter_frames.values()):
        progressed = False
        for quarter in sorted(quarter_frames):
            queue = quarter_frames[quarter]
            if not queue:
                continue
            ordered.append(queue.popleft())
            progressed = True
        if not progressed:
            break
    return ordered


def _build_clean_sentence_rows(
    manifest_row: pd.Series,
    filing_text: str,
    keywords: list[str],
    keyword_version: str,
    *,
    min_tokens: int,
    max_tokens: int,
) -> tuple[list[dict[str, Any]], int]:
    segmented = segment_sentences(filing_text)
    page_merged = merge_page_fragments(segmented, raw_text=filing_text)
    merged = merge_sentence_fragments(page_merged)
    ai_sentences = filter_ai_sentences(merged, keywords)

    clean_rows: list[dict[str, Any]] = []
    for sentence_index, sentence in enumerate(ai_sentences, start=1):
        sentence_norm = normalize_sentence_text(sentence)
        flags = get_sentence_integrity_flags(sentence, min_tokens=min_tokens)
        token_count = _token_count(sentence)
        fragment_score = round(len(flags) / _INTEGRITY_FLAG_COUNT, 6)
        if fragment_score > 0.0:
            continue
        if token_count < min_tokens or token_count > max_tokens:
            continue
        clean_rows.append(
            {
                "sentence_id": _sha1_short(
                    f"{manifest_row['path']}|{sentence_index}|{sentence_norm}"
                ),
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
                "fragment_score": fragment_score,
                "token_count": token_count,
            }
        )
    return clean_rows, len(segmented)


def build_expanded_sentence_pool(
    *,
    index_path: str = DEFAULT_INDEX,
    output_manifest_path: str = DEFAULT_MANIFEST,
    output_sentences_path: str = DEFAULT_SENTENCE_OUTPUT,
    report_path: str = DEFAULT_REPORT,
    controls_path: str = DEFAULT_CONTROLS,
    crosswalk_path: str = DEFAULT_CROSSWALK,
    keywords_path: str = DEFAULT_KEYWORDS,
    source_root: str = "",
    year: int = DEFAULT_YEAR,
    form: str = DEFAULT_FORM,
    target_firms: int = DEFAULT_TARGET_FIRMS,
    min_clean_sentences: int = DEFAULT_MIN_CLEAN_SENTENCES,
    min_tokens: int = DEFAULT_MIN_TOKENS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    manifest_id: str = DEFAULT_MANIFEST_ID,
    seed: int = DEFAULT_SAMPLE_SEED,
) -> dict[str, Any]:
    candidates = _prepare_candidates(
        index_path=index_path,
        year=year,
        form=form,
        controls_path=controls_path,
        crosswalk_path=crosswalk_path,
    )
    ordered_rows = _ordered_unique_firm_rows(candidates)
    if len(ordered_rows) < int(target_firms):
        raise ValueError(
            f"Only {len(ordered_rows)} unique-firm filings are available; target_firms={target_firms}."
        )

    source_root_path = resolve_sec_source(source_root=source_root, hint_file=SEC_SOURCE_HINT_FILE)
    keywords_file = Path(keywords_path)
    keywords = load_keywords(str(keywords_file))
    if not keywords:
        raise ValueError(f"Keyword file is empty: {keywords_file}")
    keyword_version = _sha256_file(keywords_file)

    selected_rows: list[dict[str, Any]] = []
    selected_ciks: set[str] = set()
    sentence_rows: list[dict[str, Any]] = []
    segmented_total = 0
    failed_files: list[dict[str, str]] = []

    for index, row in enumerate(ordered_rows, start=1):
        if index == 1 or index % 250 == 0:
            print(
                "[sentence-pool] "
                f"scanned={index} selected_firms={len(selected_ciks)} "
                f"clean_sentences={len(sentence_rows)}",
                flush=True,
            )
        cik = normalize_cik(row["cik"])
        if cik in selected_ciks and len(selected_ciks) < int(target_firms):
            continue
        selection_reason = (
            "quarter_round_robin"
            if len(selected_ciks) < int(target_firms)
            else "sentence_target_extension"
        )
        relative_path = Path(str(row["path"]))
        filing_path = source_root_path / relative_path
        try:
            filing_text = filing_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
            failed_files.append(
                {
                    "path": relative_path.as_posix(),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        if not _has_keyword_hit(filing_text, keywords):
            continue

        manifest_row = {
            "manifest_id": manifest_id,
            "manifest_row_id": compute_manifest_row_id(manifest_id, str(row["path"])),
            "sampling_seed": int(seed),
            "selection_reason": selection_reason,
            "source_window_id": str(row["source_window_id"]),
            "cik": cik,
            "year": int(row["year"]),
            "quarter": int(row["quarter"]),
            "form": str(row["form"]),
            "filename": str(row["filename"]),
            "path": str(row["path"]),
            "sic": str(row["sic"]),
            "ff12_code": int(row["ff12_code"]),
            "ff12_name": str(row["ff12_name"]),
            "industry_metadata_source": str(row["industry_metadata_source"]),
        }
        clean_rows, segmented_count = _build_clean_sentence_rows(
            pd.Series(manifest_row),
            filing_text,
            keywords,
            keyword_version,
            min_tokens=min_tokens,
            max_tokens=max_tokens,
        )
        if not clean_rows:
            continue

        selected_rows.append(manifest_row)
        selected_ciks.add(cik)
        segmented_total += segmented_count
        sentence_rows.extend(clean_rows)
        if len(selected_ciks) >= int(target_firms) and len(sentence_rows) >= int(
            min_clean_sentences
        ):
            break

    if len(selected_ciks) < int(target_firms):
        raise ValueError(
            f"Selected only {len(selected_ciks)} unique firms; target_firms={target_firms}."
        )
    if len(sentence_rows) < int(min_clean_sentences):
        raise ValueError(
            f"Selected only {len(sentence_rows)} clean AI sentences; minimum required is {min_clean_sentences}."
        )

    manifest = pd.DataFrame(selected_rows, columns=MANIFEST_COLUMNS)
    manifest.sort_values(["quarter", "selection_reason", "cik", "filename"], inplace=True)
    manifest.reset_index(drop=True, inplace=True)

    sentence_table = pd.DataFrame(sentence_rows, columns=SENTENCE_COLUMNS)
    sentence_table.sort_values(["source_file", "sentence_index", "sentence_id"], inplace=True)
    sentence_table.reset_index(drop=True, inplace=True)

    output_manifest = Path(output_manifest_path)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output_manifest, index=False)

    output_sentences = Path(output_sentences_path)
    output_sentences.parent.mkdir(parents=True, exist_ok=True)
    sentence_table.to_parquet(
        output_sentences, index=False, engine="pyarrow", compression="snappy"
    )

    report = {
        "manifest": {
            "manifest_id": manifest_id,
            "seed": int(seed),
            "target_firms": int(target_firms),
            "minimum_clean_sentences": int(min_clean_sentences),
            "selected_filing_count": int(len(manifest)),
        },
        "candidate_pool": {
            "firm_count": int(manifest["cik"].astype(str).nunique()),
            "filing_count": int(len(manifest)),
            "clean_sentence_count": int(len(sentence_table)),
            "quarter_counts": {
                str(int(key)): int(value)
                for key, value in manifest["quarter"]
                .astype(int)
                .value_counts()
                .sort_index()
                .items()
            },
            "ff12_known_filing_count": int(
                (manifest["industry_metadata_source"].astype(str).str.lower() != "unknown").sum()
            ),
            "ff12_unknown_filing_count": int(
                (manifest["industry_metadata_source"].astype(str).str.lower() == "unknown").sum()
            ),
        },
        "selection": {
            "firm_target_satisfied": bool(
                manifest["cik"].astype(str).nunique() >= int(target_firms)
            ),
            "clean_sentence_target_satisfied": bool(
                len(sentence_table) >= int(min_clean_sentences)
            ),
            "quarter_coverage": {
                str(int(key)): int(value)
                for key, value in manifest["quarter"]
                .astype(int)
                .value_counts()
                .sort_index()
                .items()
            },
            "selection_reason_counts": {
                str(key): int(value)
                for key, value in manifest["selection_reason"]
                .astype(str)
                .value_counts()
                .sort_index()
                .items()
            },
        },
        "extraction": {
            "total_segmented_sentences": int(segmented_total),
            "read_errors_count": int(len(failed_files)),
            "failed_files": failed_files,
        },
        "artifacts": {
            "manifest": str(output_manifest),
            "expanded_sentence_table": str(output_sentences),
            "manifest_sha256": _sha256_file(output_manifest),
            "expanded_sentence_table_sha256": _sha256_file(output_sentences),
        },
    }

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default=DEFAULT_INDEX)
    parser.add_argument("--output-manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output-sentences", default=DEFAULT_SENTENCE_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    parser.add_argument("--keywords", default=DEFAULT_KEYWORDS)
    parser.add_argument("--source-root", default="")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--form", default=DEFAULT_FORM)
    parser.add_argument("--target-firms", type=int, default=DEFAULT_TARGET_FIRMS)
    parser.add_argument("--min-clean-sentences", type=int, default=DEFAULT_MIN_CLEAN_SENTENCES)
    parser.add_argument("--min-tokens", type=int, default=DEFAULT_MIN_TOKENS)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--manifest-id", default=DEFAULT_MANIFEST_ID)
    parser.add_argument("--seed", type=int, default=DEFAULT_SAMPLE_SEED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_expanded_sentence_pool(
        index_path=args.index,
        output_manifest_path=args.output_manifest,
        output_sentences_path=args.output_sentences,
        report_path=args.report,
        controls_path=args.controls,
        crosswalk_path=args.crosswalk,
        keywords_path=args.keywords,
        source_root=args.source_root,
        year=args.year,
        form=args.form,
        target_firms=args.target_firms,
        min_clean_sentences=args.min_clean_sentences,
        min_tokens=args.min_tokens,
        max_tokens=args.max_tokens,
        manifest_id=args.manifest_id,
        seed=args.seed,
    )
    print(
        "[sentence-pool] "
        f"firms={report['candidate_pool']['firm_count']} "
        f"clean_sentences={report['candidate_pool']['clean_sentence_count']}"
    )
    print(f"[sentence-pool] manifest -> {args.output_manifest}")
    print(f"[sentence-pool] sentences -> {args.output_sentences}")
    print(f"[sentence-pool] summary -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
