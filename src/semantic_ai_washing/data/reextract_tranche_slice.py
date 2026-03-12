"""Rebuild a tranche calibration slice from raw SEC filings."""

from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
import re

import pandas as pd

from semantic_ai_washing.core.sentence_filter import (
    filter_ai_sentences_with_sections,
    load_keywords,
    merge_page_fragments,
    merge_sentence_fragments,
    normalize_sentence_text,
    segment_sentences,
)
from semantic_ai_washing.data.index_sec_filings import SEC_SOURCE_HINT_FILE, resolve_sec_source

DEFAULT_INPUT_SLICE = "data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv"
DEFAULT_OUTPUT = "data/labels/v1/labeling_batch_v1_reextracted_v2_2_slice40.csv"
DEFAULT_REPORT = "reports/labels/tranche1_reextraction_v2_2_summary.json"
DEFAULT_KEYWORDS = "data/metadata/ai_keywords.txt"
DEFAULT_MATCH_THRESHOLD = 0.65
_CTX_ITEM_1A_RE = re.compile(r"\bitem\s*1a\b", re.I)
_CTX_ITEM_1_RE = re.compile(r"\bitem\s*1\b(?!\s*a\b)", re.I)
_CTX_ITEM_7_RE = re.compile(r"\bitem\s*7\b", re.I)


def _resolve_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _token_set(text: str) -> set[str]:
    return {
        token for token in normalize_sentence_text(text).split() if token and not token.isdigit()
    }


def _overlap_score(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(len(left_tokens), len(right_tokens))


def _sequence_score(left: str, right: str) -> float:
    return SequenceMatcher(
        None, normalize_sentence_text(left), normalize_sentence_text(right)
    ).ratio()


def _match_score(left: str, right: str) -> float:
    overlap = _overlap_score(left, right)
    sequence = _sequence_score(left, right)
    return round((0.55 * sequence) + (0.45 * overlap), 6)


def _build_candidate_frame(
    *,
    source_file: str,
    filing_text: str,
    keywords: list[str],
) -> pd.DataFrame:
    segmented = segment_sentences(filing_text)
    page_merged = merge_page_fragments(segmented, raw_text=filing_text)
    merged = merge_sentence_fragments(page_merged)
    tagged = filter_ai_sentences_with_sections(merged, keywords)

    rows: list[dict[str, Any]] = []
    for candidate_index, (sentence, source_section) in enumerate(tagged, start=1):
        if source_section == "other":
            source_section = _infer_section_from_raw_context(
                filing_text=filing_text,
                sentence=sentence,
                default=source_section,
            )
        rows.append(
            {
                "source_file": source_file,
                "candidate_sentence_index": candidate_index,
                "sentence": sentence,
                "sentence_norm": normalize_sentence_text(sentence),
                "source_section": str(source_section),
            }
        )
    return pd.DataFrame(rows)


def _infer_section_from_raw_context(
    *,
    filing_text: str,
    sentence: str,
    default: str = "other",
) -> str:
    lowered = filing_text.lower()
    sentence_lower = sentence.lower()
    location = lowered.find(sentence_lower)
    if location < 0:
        return default
    context = lowered[:location]
    last_item_1a = max((m.start() for m in _CTX_ITEM_1A_RE.finditer(context)), default=-1)
    last_item_7 = max((m.start() for m in _CTX_ITEM_7_RE.finditer(context)), default=-1)
    last_item_1 = max((m.start() for m in _CTX_ITEM_1_RE.finditer(context)), default=-1)
    best = max(
        [
            (last_item_1a, "item_1a_risk_factors"),
            (last_item_7, "item_7_mda"),
            (last_item_1, "item_1_business"),
        ],
        key=lambda item: item[0],
    )
    return best[1] if best[0] >= 0 else default


def _best_match(
    original_sentence: str,
    original_index: int,
    candidates: pd.DataFrame,
) -> tuple[dict[str, Any] | None, str, float]:
    if candidates.empty:
        return None, "unmatched", 0.0

    original_norm = normalize_sentence_text(original_sentence)
    exact = candidates[candidates["sentence_norm"] == original_norm].copy()
    if not exact.empty:
        exact["index_distance"] = (
            exact["candidate_sentence_index"].astype(int) - int(original_index)
        ).abs()
        best_exact = exact.sort_values(
            by=["index_distance", "candidate_sentence_index", "sentence"]
        ).iloc[0]
        return best_exact.to_dict(), "exact", 1.0

    scored_rows: list[dict[str, Any]] = []
    for candidate in candidates.itertuples(index=False):
        score = _match_score(original_sentence, str(candidate.sentence))
        scored_rows.append(
            {
                "candidate": {
                    "source_file": str(candidate.source_file),
                    "candidate_sentence_index": int(candidate.candidate_sentence_index),
                    "sentence": str(candidate.sentence),
                    "sentence_norm": str(candidate.sentence_norm),
                    "source_section": str(candidate.source_section),
                },
                "score": score,
                "index_distance": abs(
                    int(candidate.candidate_sentence_index) - int(original_index)
                ),
            }
        )
    if not scored_rows:
        return None, "unmatched", 0.0
    scored_rows.sort(
        key=lambda item: (
            -float(item["score"]),
            int(item["index_distance"]),
            item["candidate"]["sentence"],
        )
    )
    best = scored_rows[0]
    if float(best["score"]) < DEFAULT_MATCH_THRESHOLD:
        return None, "unmatched", float(best["score"])
    return best["candidate"], "similarity", float(best["score"])


def reextract_tranche_slice(
    *,
    input_csv: str = DEFAULT_INPUT_SLICE,
    output_csv: str = DEFAULT_OUTPUT,
    report_path: str = DEFAULT_REPORT,
    source_root: str = "",
    keywords_path: str = DEFAULT_KEYWORDS,
    match_threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> dict[str, Any]:
    if match_threshold != DEFAULT_MATCH_THRESHOLD:
        raise ValueError(
            "Only the approved match threshold is supported in this calibration harness."
        )

    input_path = _resolve_path(input_csv)
    output_path = _resolve_path(output_csv)
    report_file = _resolve_path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(input_path)
    required_columns = ["source_file", "sentence_id", "sentence_index", "sentence"]
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Slice CSV missing required columns: {missing}")

    source_root_path = resolve_sec_source(source_root=source_root, hint_file=SEC_SOURCE_HINT_FILE)
    keywords = load_keywords(str(_resolve_path(keywords_path)))
    if not keywords:
        raise ValueError(f"Keyword file is empty: {keywords_path}")

    unique_files = sorted(frame["source_file"].fillna("").astype(str).unique().tolist())
    candidates_by_file: dict[str, pd.DataFrame] = {}
    file_failures: list[dict[str, str]] = []
    total_candidates = 0

    for source_file in unique_files:
        filing_path = source_root_path / source_file
        try:
            filing_text = filing_path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
            file_failures.append(
                {
                    "source_file": source_file,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            candidates_by_file[source_file] = pd.DataFrame(
                columns=[
                    "source_file",
                    "candidate_sentence_index",
                    "sentence",
                    "sentence_norm",
                    "source_section",
                ]
            )
            continue

        candidate_frame = _build_candidate_frame(
            source_file=source_file,
            filing_text=filing_text,
            keywords=keywords,
        )
        candidates_by_file[source_file] = candidate_frame
        total_candidates += int(len(candidate_frame))

    rows: list[dict[str, Any]] = []
    exact_matches = 0
    similarity_matches = 0
    unmatched = 0

    for original in frame.itertuples(index=False):
        original_sentence = str(original.sentence)
        source_file = str(original.source_file)
        candidates = candidates_by_file[source_file]
        match, match_status, match_score = _best_match(
            original_sentence=original_sentence,
            original_index=int(original.sentence_index),
            candidates=candidates,
        )
        if match_status == "exact":
            exact_matches += 1
        elif match_status == "similarity":
            similarity_matches += 1
        else:
            unmatched += 1

        rebuilt_sentence = original_sentence
        rebuilt_norm = normalize_sentence_text(original_sentence)
        source_section = "other"
        candidate_sentence_index = int(original.sentence_index)
        if match is not None:
            rebuilt_sentence = str(match["sentence"])
            rebuilt_norm = str(match["sentence_norm"])
            source_section = str(match["source_section"])
            candidate_sentence_index = int(match["candidate_sentence_index"])

        output_row = original._asdict()
        output_row["original_sentence"] = original_sentence
        output_row["original_sentence_index"] = int(original.sentence_index)
        output_row["prior_manual_label"] = str(getattr(original, "label", "") or "")
        output_row["prior_assistive_label"] = str(getattr(original, "assistive_label", "") or "")
        output_row["sentence"] = rebuilt_sentence
        output_row["sentence_norm"] = rebuilt_norm
        output_row["source_section"] = source_section
        output_row["match_status"] = match_status
        output_row["match_score"] = round(float(match_score), 6)
        output_row["candidate_sentence_index"] = candidate_sentence_index
        output_row["label"] = ""
        output_row["is_uncertain"] = ""
        output_row["uncertainty_note"] = ""
        rows.append(output_row)

    rebuilt = pd.DataFrame(rows)
    rebuilt.sort_values(by=["source_file", "sentence_index", "sentence_id"], inplace=True)
    rebuilt.to_csv(output_path, index=False)

    report = {
        "input_csv": str(input_path),
        "output_csv": str(output_path),
        "source_root": str(source_root_path),
        "counts": {
            "slice_rows": int(len(frame)),
            "unique_source_files": int(len(unique_files)),
            "candidate_sentence_count": int(total_candidates),
            "matched_rows": int(exact_matches + similarity_matches),
            "exact_matches": int(exact_matches),
            "similarity_matches": int(similarity_matches),
            "unmatched_rows": int(unmatched),
            "file_read_failures": int(len(file_failures)),
        },
        "section_counts": {
            str(section): int(count)
            for section, count in rebuilt["source_section"]
            .fillna("other")
            .astype(str)
            .value_counts()
            .items()
        },
        "unmatched_sentence_ids": rebuilt.loc[
            rebuilt["match_status"].astype(str) == "unmatched", "sentence_id"
        ]
        .astype(str)
        .tolist(),
        "file_failures": file_failures,
    }
    report_file.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", default=DEFAULT_INPUT_SLICE)
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--source-root", default="")
    parser.add_argument("--keywords", default=DEFAULT_KEYWORDS)
    parser.add_argument("--match-threshold", type=float, default=DEFAULT_MATCH_THRESHOLD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reextract_tranche_slice(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        report_path=args.report,
        source_root=args.source_root,
        keywords_path=args.keywords,
        match_threshold=args.match_threshold,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
