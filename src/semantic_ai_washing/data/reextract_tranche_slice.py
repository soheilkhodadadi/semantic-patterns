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
    clean_extracted_sentence,
    filter_ai_sentences_with_sections,
    load_keywords,
    merge_page_fragments,
    merge_sentence_fragments,
    normalize_sentence_text,
    segment_sentences_fast,
)
from ai_washing_member.data.index_sec_filings import SEC_SOURCE_HINT_FILE, resolve_sec_source

DEFAULT_INPUT_SLICE = "data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv"
DEFAULT_OUTPUT = "data/labels/v1/labeling_batch_v1_reextracted_v2_2_slice40.csv"
DEFAULT_REPORT = "reports/labels/tranche1_reextraction_v2_2_summary.json"
DEFAULT_KEYWORDS = "data/metadata/ai_keywords.txt"
DEFAULT_MATCH_THRESHOLD = 0.65
_CTX_ITEM_1A_RE = re.compile(r"\bitem\s*1a\b", re.I)
_CTX_ITEM_1_RE = re.compile(r"\bitem\s*1\b(?!\s*a\b)", re.I)
_CTX_ITEM_7_RE = re.compile(r"\bitem\s*7\b", re.I)
_TABLE_OF_CONTENTS_RE = re.compile(r"\b\d*\s*table of contents\b", re.I)
_FORM_HEADER_RE = re.compile(
    r"(?:\b(?-i:[A-Z][A-Z0-9&.,' /\-]{2,})\s*\|\s*)?"
    r"\b20\d{2}\s+Form\s+10-K\s+\d+\s+"
    r"(?:Risk Factors|Business|Table of Contents|Management['’]s Discussion and Analysis)\b",
    re.I,
)
_HEADING_PREFIX_RE = re.compile(
    r"^\s*(?:Our Products and Suppliers|Business Overview|Executive Summary|"
    r"Data,\s*Analytics\s+and\s+Artificial\s+Intelligence)\b",
    re.I,
)
_GLOSSARY_RE = re.compile(
    r"^(?:[A-Z0-9]\s+)?AI/ML\s*-\s*Artificial Intelligence/Machine Learning\.?$",
    re.I,
)
_PAGE_NUMBER_PREFIX_RE = re.compile(r"^\s*\d+\s+")
_PRESENT_FACT_RE = re.compile(
    r"^\s*(?:we|our|[A-Z][A-Za-z0-9&.'-]+)\s+"
    r"(?:offer|offers|provide|provides|use|uses|have used|has used|invest|invests|"
    r"have invested|has invested|have expertise|has expertise|are|is|become|became)\b",
    re.I,
)
_AI_MARKER_RE = re.compile(
    r"\b(?:ai|artificial intelligence|machine learning|generative ai|ai-enabled|"
    r"artificial intelligence-enabled)\b",
    re.I,
)

_NOISE_ISSUES = {"glossary_fragment", "table_of_contents", "form_header"}
_ASSISTIVE_COLUMNS = (
    "assistive_label",
    "assistive_confidence",
    "assistive_rationale",
    "assistive_model",
    "assistive_generated_at",
    "assistive_prompt_hash",
)


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


def _detect_cleanup_issues(text: str) -> list[str]:
    candidate = "" if text is None else str(text)
    issues: list[str] = []
    lowered = candidate.lower()
    if _TABLE_OF_CONTENTS_RE.search(candidate):
        issues.append("table_of_contents")
    if _FORM_HEADER_RE.search(candidate):
        issues.append("form_header")
    if _HEADING_PREFIX_RE.search(candidate):
        issues.append("leading_section_title")
    if (
        _GLOSSARY_RE.match(candidate.strip())
        or "ai/ml - artificial intelligence/machine learning" in lowered
    ):
        issues.append("glossary_fragment")
    return issues


def _classify_unmatched_row(*, original_sentence: str, cleaned_sentence: str) -> tuple[bool, str]:
    issues = set(_detect_cleanup_issues(original_sentence)) | set(
        _detect_cleanup_issues(cleaned_sentence)
    )
    if issues & _NOISE_ISSUES:
        return False, "unmatched_noise"
    if "leading_section_title" in issues and not cleaned_sentence.strip():
        return False, "unmatched_noise"
    return True, ""


def _strip_page_number_prefix(text: str) -> str:
    return _PAGE_NUMBER_PREFIX_RE.sub("", text or "").strip()


def _looks_like_present_fact(text: str) -> bool:
    return bool(_PRESENT_FACT_RE.search(text or ""))


def _contains_ai_marker(text: str) -> bool:
    return bool(_AI_MARKER_RE.search(text or ""))


def _rescue_clause(
    *,
    original_sentence: str,
    candidates: pd.DataFrame,
    original_index: int,
) -> tuple[dict[str, Any] | None, str, float]:
    cleaned_original = clean_extracted_sentence(original_sentence)
    stripped_original = _strip_page_number_prefix(cleaned_original)
    if not stripped_original:
        return None, "unmatched", 0.0

    rescued_rows: list[dict[str, Any]] = []
    for candidate in candidates.itertuples(index=False):
        candidate_clean = clean_extracted_sentence(str(candidate.sentence))
        if not candidate_clean:
            continue
        search_targets = [cleaned_original.strip(), stripped_original]
        for target in search_targets:
            if not target:
                continue
            position = candidate_clean.find(target)
            if position < 0:
                continue
            rescued_sentence = _strip_page_number_prefix(candidate_clean[position:])
            if not rescued_sentence or rescued_sentence == candidate_clean:
                continue
            score = _match_score(stripped_original, rescued_sentence)
            rescued_rows.append(
                {
                    "candidate": {
                        "source_file": str(candidate.source_file),
                        "candidate_sentence_index": int(candidate.candidate_sentence_index),
                        "sentence": rescued_sentence,
                        "sentence_norm": normalize_sentence_text(rescued_sentence),
                        "source_section": str(candidate.source_section),
                    },
                    "score": score,
                    "index_distance": abs(
                        int(candidate.candidate_sentence_index) - int(original_index)
                    ),
                }
            )
            break
    if not rescued_rows:
        return None, "unmatched", 0.0
    rescued_rows.sort(
        key=lambda item: (
            -float(item["score"]),
            int(item["index_distance"]),
            item["candidate"]["sentence"],
        )
    )
    best = rescued_rows[0]
    if float(best["score"]) < DEFAULT_MATCH_THRESHOLD:
        return None, "unmatched", float(best["score"])
    return best["candidate"], "rescued_clause", float(best["score"])


def _rescue_similarity(
    *,
    original_sentence: str,
    candidates: pd.DataFrame,
) -> tuple[dict[str, Any] | None, str, float]:
    cleaned_original = clean_extracted_sentence(original_sentence)
    original_norm = normalize_sentence_text(cleaned_original)
    original_tokens = set(original_norm.split())
    anchor_tokens = {
        token
        for token in original_tokens
        if token
        in {
            "expertise",
            "provider",
            "service",
            "services",
            "capability",
            "capabilities",
            "data",
            "analytics",
            "cloud",
            "platform",
            "development",
            "investment",
            "invest",
        }
    }
    if not anchor_tokens:
        return None, "unmatched", 0.0

    scored_rows: list[dict[str, Any]] = []
    for candidate in candidates.itertuples(index=False):
        candidate_sentence = clean_extracted_sentence(str(candidate.sentence))
        if not candidate_sentence or not _contains_ai_marker(candidate_sentence):
            continue
        candidate_norm = normalize_sentence_text(candidate_sentence)
        candidate_tokens = set(candidate_norm.split())
        overlap = len(anchor_tokens & candidate_tokens)
        if overlap == 0:
            continue
        provider_bonus = (
            1.0
            if re.search(
                r"\b(provider|offer|offers|provide|provides|service|services)\b", candidate_norm
            )
            else 0.0
        )
        ai_bonus = 1.0
        fact_bonus = 1.0 if _looks_like_present_fact(candidate_sentence) else 0.0
        first_person_bonus = (
            0.25 if candidate_sentence.lower().startswith(("we ", "our ")) else 0.0
        )
        base_score = _match_score(cleaned_original, candidate_sentence)
        rescue_score = (
            (2.0 * overlap)
            + provider_bonus
            + ai_bonus
            + fact_bonus
            + first_person_bonus
            + (0.25 * base_score)
        )
        scored_rows.append(
            {
                "candidate": {
                    "source_file": str(candidate.source_file),
                    "candidate_sentence_index": int(candidate.candidate_sentence_index),
                    "sentence": candidate_sentence,
                    "sentence_norm": normalize_sentence_text(candidate_sentence),
                    "source_section": str(candidate.source_section),
                },
                "rescue_score": rescue_score,
                "match_score": base_score,
            }
        )
    if not scored_rows:
        return None, "unmatched", 0.0
    scored_rows.sort(
        key=lambda item: (
            -float(item["rescue_score"]),
            -float(item["match_score"]),
            item["candidate"]["sentence"],
        )
    )
    best = scored_rows[0]
    runner_up_score = float(scored_rows[1]["rescue_score"]) if len(scored_rows) > 1 else 0.0
    if float(best["rescue_score"]) < 3.0:
        return None, "unmatched", float(best["match_score"])
    if (float(best["rescue_score"]) - runner_up_score) < 0.2:
        return None, "unmatched", float(best["match_score"])
    return best["candidate"], "rescued_similarity", float(best["match_score"])


def _build_candidate_frame(
    *,
    source_file: str,
    filing_text: str,
    keywords: list[str],
) -> pd.DataFrame:
    # Calibration loops should stay fast; use the regex splitter here rather
    # than the heavier spaCy-backed path from the full extraction pipeline.
    segmented = segment_sentences_fast(filing_text)
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

    cleaned_original = clean_extracted_sentence(original_sentence)
    original_for_match = cleaned_original or original_sentence
    original_norm = normalize_sentence_text(original_for_match)
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
        score = _match_score(original_for_match, str(candidate.sentence))
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
    rescued_clause_rows = 0
    rescued_similarity_rows = 0
    rescued_sentence_ids: list[str] = []
    unmatched = 0
    cleaned_rows = 0
    unmatched_noise_rows = 0
    unmatched_meaningful_rows = 0
    prelabel_ineligible_rows = 0
    cleanup_hits = {
        "table_of_contents": 0,
        "form_header": 0,
        "leading_section_title": 0,
        "glossary_fragment": 0,
    }
    row_outcomes: list[dict[str, Any]] = []

    for original in frame.itertuples(index=False):
        original_sentence = str(original.sentence)
        source_file = str(original.source_file)
        candidates = candidates_by_file[source_file]
        cleaned_original = clean_extracted_sentence(original_sentence)
        match, match_status, match_score = _best_match(
            original_sentence=original_sentence,
            original_index=int(original.sentence_index),
            candidates=candidates,
        )
        if match_status != "exact":
            clause_match, clause_status, clause_score = _rescue_clause(
                original_sentence=original_sentence,
                candidates=candidates,
                original_index=int(original.sentence_index),
            )
            if clause_status == "rescued_clause" and (
                match_status == "unmatched" or float(clause_score) >= float(match_score)
            ):
                match, match_status, match_score = clause_match, clause_status, clause_score
        if match_status == "unmatched":
            match, match_status, match_score = _rescue_similarity(
                original_sentence=original_sentence,
                candidates=candidates,
            )
        if match_status == "exact":
            exact_matches += 1
        elif match_status == "similarity":
            similarity_matches += 1
        elif match_status == "rescued_clause":
            rescued_clause_rows += 1
            rescued_sentence_ids.append(str(original.sentence_id))
        elif match_status == "rescued_similarity":
            rescued_similarity_rows += 1
            rescued_sentence_ids.append(str(original.sentence_id))
        else:
            unmatched += 1

        rebuilt_sentence = cleaned_original
        rebuilt_norm = normalize_sentence_text(cleaned_original)
        source_section = "other"
        candidate_sentence_index = int(original.sentence_index)
        if match is not None:
            rebuilt_sentence = str(match["sentence"])
            rebuilt_norm = str(match["sentence_norm"])
            source_section = str(match["source_section"])
            candidate_sentence_index = int(match["candidate_sentence_index"])
        issues_before = _detect_cleanup_issues(original_sentence)
        issues_after = _detect_cleanup_issues(rebuilt_sentence)
        row_cleaned = rebuilt_sentence != original_sentence or (
            bool(issues_before) and len(issues_after) < len(issues_before)
        )
        if row_cleaned:
            cleaned_rows += 1
        for issue in issues_before:
            if issue not in issues_after:
                cleanup_hits[issue] += 1

        prelabel_eligible = True
        skip_reason = ""
        if match_status == "unmatched":
            prelabel_eligible, skip_reason = _classify_unmatched_row(
                original_sentence=original_sentence,
                cleaned_sentence=cleaned_original,
            )
            if prelabel_eligible:
                unmatched_meaningful_rows += 1
            else:
                unmatched_noise_rows += 1
                prelabel_ineligible_rows += 1
                rebuilt_sentence = ""
                rebuilt_norm = ""
        if not prelabel_eligible:
            source_section = "other"

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
        output_row["prelabel_eligible"] = bool(prelabel_eligible)
        output_row["skip_reason"] = skip_reason
        output_row["label"] = ""
        output_row["is_uncertain"] = ""
        output_row["uncertainty_note"] = ""
        for column in _ASSISTIVE_COLUMNS:
            if column in output_row:
                output_row[column] = ""
        rows.append(output_row)
        row_outcomes.append(
            {
                "sentence_id": str(original.sentence_id),
                "source_file": source_file,
                "match_status": match_status,
                "match_score": round(float(match_score), 6),
                "issues_before": issues_before,
                "issues_after": issues_after,
                "row_cleaned": row_cleaned,
                "prelabel_eligible": bool(prelabel_eligible),
                "skip_reason": skip_reason,
            }
        )

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
            "matched_rows": int(
                exact_matches + similarity_matches + rescued_clause_rows + rescued_similarity_rows
            ),
            "exact_matches": int(exact_matches),
            "similarity_matches": int(similarity_matches),
            "rescued_clause_rows": int(rescued_clause_rows),
            "rescued_similarity_rows": int(rescued_similarity_rows),
            "unmatched_rows": int(unmatched),
            "unmatched_noise_rows": int(unmatched_noise_rows),
            "unmatched_meaningful_rows": int(unmatched_meaningful_rows),
            "prelabel_ineligible_rows": int(prelabel_ineligible_rows),
            "file_read_failures": int(len(file_failures)),
            "cleaned_rows": int(cleaned_rows),
        },
        "section_counts": {
            str(section): int(count)
            for section, count in rebuilt["source_section"]
            .fillna("other")
            .astype(str)
            .value_counts()
            .items()
        },
        "cleanup_hits": cleanup_hits,
        "unmatched_sentence_ids": rebuilt.loc[
            rebuilt["match_status"].astype(str) == "unmatched", "sentence_id"
        ]
        .astype(str)
        .tolist(),
        "rescued_sentence_ids": rescued_sentence_ids,
        "row_outcomes": row_outcomes,
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
