"""Lightweight pregrant extractor for AI-related application counts per firm-year."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from semantic_ai_washing.patents.keyword_matching import (
    compile_boundary_pattern,
    load_keywords,
    matched_keywords,
    normalize_org_name,
)
from semantic_ai_washing.patents.pregrant_sources import resolve_pregrant_patentsview_layout


def _ensure_large_csv_field_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit = limit // 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-year", type=int, default=2014)
    parser.add_argument(
        "--data-root",
        default=os.getenv("PATENT_PREGRANT_DATA_ROOT", "/Users/soheilkhodadadi/DataWork/patentsview/pregrant"),
    )
    parser.add_argument(
        "--company-lookup",
        default="data/metadata/company_lookup_ever_speaker_2016_2025_hybrid_v1.csv",
    )
    parser.add_argument(
        "--company-aliases",
        default="data/metadata/company_aliases_ever_speaker_2016_2025_hybrid_v1.csv",
    )
    parser.add_argument(
        "--output-counts",
        default="data/processed/patents/ai_application_counts_filtered_{suffix}.csv",
    )
    parser.add_argument(
        "--output-examples",
        default="data/processed/patents/ai_application_examples_{suffix}.csv",
    )
    parser.add_argument(
        "--output-diag",
        default="data/processed/patents/application_diagnostics_{suffix}.csv",
    )
    parser.add_argument(
        "--keywords-path",
        default="data/metadata/patent_keywords.txt",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/data/pregrant_application_extraction_progress_{suffix}.json",
    )
    return parser.parse_args()


def write_progress(path: Path, status: str, **payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": status,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                **payload,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _clean_field(value: object) -> str:
    text = "" if value is None else str(value).strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return text[1:-1]
    return text


def _truthy_flag(value: object) -> int:
    return 1 if _clean_field(value).upper() == "TRUE" else 0


def load_company_lookup(path: str) -> list[dict[str, str]]:
    firms: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            firms.append(
                {
                    "cik": str(row.get("cik", "")).strip(),
                    "name": str(row.get("name", "")).strip(),
                    "name_clean": str(row.get("name_clean", "")).strip(),
                }
            )
    return firms


def load_company_aliases(path: str) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = defaultdict(list)
    if not os.path.exists(path):
        return aliases
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            cik = str(row.get("cik", "")).strip()
            alias = normalize_org_name(str(row.get("alias", "")).strip())
            if cik and alias:
                aliases[cik].append(alias)
    return aliases


def build_term_index(
    firms: list[dict[str, str]], aliases: dict[str, list[str]]
) -> dict[str, list[tuple[str, str]]]:
    raw_index: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for firm in firms:
        cik = firm["cik"]
        name = firm["name"]
        if not cik or not name:
            continue
        terms: list[str] = []
        base = normalize_org_name(firm["name_clean"])
        if base:
            terms.append(base)
        for alias in aliases.get(cik, []):
            alias_norm = normalize_org_name(alias)
            if alias_norm:
                terms.append(alias_norm)
        seen: set[str] = set()
        for term in terms:
            if term in seen:
                continue
            seen.add(term)
            raw_index[term].append((cik, name))

    term_index: dict[str, list[tuple[str, str]]] = {}
    for term, rows in raw_index.items():
        unique_ciks = {cik for cik, _ in rows}
        if len(unique_ciks) == 1:
            term_index[term] = rows
    return term_index


def append_pgpub_matches_from_org_file(
    matched_by_pgpub: dict[str, list[tuple[str, str]]],
    *,
    path: str | Path,
    org_column: str,
    term_index: dict[str, list[tuple[str, str]]],
    fallback_only: bool,
) -> tuple[int, int]:
    """Append matched firm rows from a pregrant org-name file."""

    rows_added = 0
    pgpubs_added = 0
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if not pgpub_id:
                continue
            if fallback_only and pgpub_id in matched_by_pgpub:
                continue
            org = _clean_field(row.get(org_column))
            if not org:
                continue
            org_clean = normalize_org_name(org)
            if org_clean not in term_index:
                continue
            existing = set(matched_by_pgpub.get(pgpub_id, []))
            before = len(existing)
            for item in term_index[org_clean]:
                existing.add(item)
            after = len(existing)
            if after > before:
                matched_by_pgpub[pgpub_id] = sorted(existing)
                rows_added += after - before
                if before == 0:
                    pgpubs_added += 1
    return rows_added, pgpubs_added


def _dedupe_application_matches(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame

    working = frame.copy()
    working["current_pgpub_id_flag"] = working["current_pgpub_id_flag"].map(_truthy_flag)
    working["current_patent_id_flag"] = working["current_patent_id_flag"].map(_truthy_flag)
    working["published_date_rank"] = pd.to_datetime(
        working["published_date"], errors="coerce"
    ).fillna(pd.Timestamp.min)
    working["has_abstract"] = working["application_abstract"].fillna("").str.len() > 0

    working = working.sort_values(
        [
            "cik",
            "application_id",
            "current_pgpub_id_flag",
            "current_patent_id_flag",
            "published_date_rank",
            "has_abstract",
            "pgpub_id",
        ],
        ascending=[True, True, False, False, False, False, False],
    )
    return working.drop_duplicates(["cik", "application_id"], keep="first").drop(
        columns=["published_date_rank", "has_abstract"]
    )


def main() -> None:
    args = parse_args()
    _ensure_large_csv_field_limit()
    suffix = f"{args.min_year}plus"
    progress_path = Path(args.progress_report.format(suffix=suffix))
    output_counts = Path(args.output_counts.format(suffix=suffix))
    output_examples = Path(args.output_examples.format(suffix=suffix))
    output_diag = Path(args.output_diag.format(suffix=suffix))
    for path in [output_counts, output_examples, output_diag]:
        path.parent.mkdir(parents=True, exist_ok=True)

    layout = resolve_pregrant_patentsview_layout(args.data_root)

    firms = load_company_lookup(args.company_lookup)
    aliases = load_company_aliases(args.company_aliases)
    term_index = build_term_index(firms, aliases)
    write_progress(
        progress_path,
        "term_index_ready",
        min_year=args.min_year,
        keywords_path=args.keywords_path,
        normalized_company_terms=len(term_index),
        data_root=str(layout.root),
    )

    matched_by_pgpub: dict[str, list[tuple[str, str]]] = defaultdict(list)
    assignee_rows_added, assignee_pgpubs_added = append_pgpub_matches_from_org_file(
        matched_by_pgpub,
        path=layout.assignee,
        org_column="disambig_assignee_organization",
        term_index=term_index,
        fallback_only=False,
    )
    applicant_rows_added = 0
    applicant_pgpubs_added = 0
    if layout.applicant is not None:
        applicant_rows_added, applicant_pgpubs_added = append_pgpub_matches_from_org_file(
            matched_by_pgpub,
            path=layout.applicant,
            org_column="raw_applicant_organization",
            term_index=term_index,
            fallback_only=True,
        )
    matched_pgpub_ids = set(matched_by_pgpub)
    write_progress(
        progress_path,
        "assignee_matching_complete",
        matched_pgpub_rows=len(matched_pgpub_ids),
        matched_firms=len({cik for rows in matched_by_pgpub.values() for cik, _ in rows}),
        assignee_rows_added=assignee_rows_added,
        assignee_pgpubs_added=assignee_pgpubs_added,
        applicant_rows_added=applicant_rows_added,
        applicant_pgpubs_added=applicant_pgpubs_added,
    )

    applications: dict[str, dict[str, str]] = {}
    with open(layout.published_application, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if pgpub_id not in matched_pgpub_ids:
                continue
            applications[pgpub_id] = {
                "pgpub_id": pgpub_id,
                "application_id": _clean_field(row.get("application_id")),
                "filing_date": _clean_field(row.get("filing_date")),
                "published_date": _clean_field(row.get("published_date")),
                "application_title": _clean_field(row.get("application_title")),
            }
    write_progress(
        progress_path,
        "published_application_loaded",
        matched_pgpub_rows=len(matched_pgpub_ids),
        application_rows_loaded=len(applications),
    )

    abstracts: dict[str, str] = {}
    with open(layout.abstract, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if pgpub_id in applications:
                abstracts[pgpub_id] = _clean_field(row.get("application_abstract"))
    write_progress(
        progress_path,
        "abstracts_loaded",
        application_rows_loaded=len(applications),
        abstracts_loaded=len(abstracts),
    )

    crosswalk: dict[str, dict[str, str]] = {}
    with open(layout.crosswalk, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if not pgpub_id or pgpub_id not in applications:
                continue
            crosswalk[pgpub_id] = {
                "patent_id": _clean_field(row.get("patent_id")),
                "current_pgpub_id_flag": _clean_field(row.get("current_pgpub_id_flag")),
                "current_patent_id_flag": _clean_field(row.get("current_patent_id_flag")),
            }
    write_progress(
        progress_path,
        "crosswalk_loaded",
        crosswalk_rows=len(crosswalk),
    )

    pattern = compile_boundary_pattern(load_keywords(args.keywords_path))
    rows: list[dict[str, object]] = []
    for pgpub_id, matches in matched_by_pgpub.items():
        application = applications.get(pgpub_id)
        if not application:
            continue
        filing_date = application.get("filing_date", "")
        try:
            year = int(filing_date[:4])
        except Exception:
            continue
        if year < args.min_year:
            continue

        title = application.get("application_title", "")
        abstract = abstracts.get(pgpub_id, "")
        text = f"{title} {abstract}".lower()
        mk = matched_keywords(text, pattern)
        cross = crosswalk.get(
            pgpub_id,
            {
                "patent_id": "",
                "current_pgpub_id_flag": "",
                "current_patent_id_flag": "",
            },
        )
        seen_pairs: set[tuple[str, str]] = set()
        for cik, name in matches:
            pair = (cik, name)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            rows.append(
                {
                    "cik": cik,
                    "name": name,
                    "year": year,
                    "pgpub_id": pgpub_id,
                    "application_id": application.get("application_id", ""),
                    "patent_id": cross.get("patent_id", ""),
                    "filing_date": filing_date,
                    "published_date": application.get("published_date", ""),
                    "application_title": title,
                    "application_abstract": abstract,
                    "matched_keywords": mk,
                    "is_ai": int(bool(mk)),
                    "current_pgpub_id_flag": cross.get("current_pgpub_id_flag", ""),
                    "current_patent_id_flag": cross.get("current_patent_id_flag", ""),
                }
            )

    frame = pd.DataFrame.from_records(rows)
    frame = _dedupe_application_matches(frame)
    write_progress(
        progress_path,
        "application_rows_deduped",
        candidate_rows=len(rows),
        deduped_rows=len(frame),
    )

    totals: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    ai_hits: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    for row in frame.itertuples(index=False):
        key = (str(row.cik), str(row.name), int(row.year))
        app_id = str(row.application_id)
        totals[key].add(app_id)
        if int(row.is_ai) == 1:
            ai_hits[key].add(app_id)

    counts_rows: list[dict[str, object]] = []
    for key in sorted(totals):
        cik, name, year = key
        applications_total = len(totals[key])
        applications_ai = len(ai_hits.get(key, set()))
        counts_rows.append(
            {
                "cik": cik,
                "name": name,
                "year": year,
                "applications_total": applications_total,
                "applications_ai": applications_ai,
                "ai_share_applications": (
                    applications_ai / applications_total if applications_total else ""
                ),
            }
        )
    pd.DataFrame.from_records(counts_rows).to_csv(output_counts, index=False)

    example_rows = (
        frame.loc[frame["is_ai"] == 1]
        .sort_values(["cik", "year", "filing_date", "application_id"])
        .drop_duplicates(["cik", "year"], keep="last")
        [
            [
                "cik",
                "name",
                "year",
                "application_id",
                "pgpub_id",
                "patent_id",
                "filing_date",
                "published_date",
                "application_title",
                "application_abstract",
                "matched_keywords",
            ]
        ]
    )
    example_rows.to_csv(output_examples, index=False)

    diag = (
        frame.groupby(["cik", "name"], as_index=False)
        .agg(
            applications_total=("application_id", "nunique"),
            applications_ai=("is_ai", "sum"),
            matched_pgpub_rows_premerge=("pgpub_id", "count"),
            crosswalk_linked_rows=("patent_id", lambda s: int((s.fillna("") != "").sum())),
        )
        .sort_values(["cik", "name"])
    )
    diag["ai_share_overall"] = diag["applications_ai"] / diag["applications_total"].replace(0, pd.NA)
    diag.to_csv(output_diag, index=False)

    write_progress(
        progress_path,
        "completed",
        output_counts_path=str(output_counts),
        output_examples_path=str(output_examples),
        output_diag_path=str(output_diag),
        firm_year_rows=len(counts_rows),
        firms_with_any_applications=int((diag["applications_total"] > 0).sum()),
        firms_with_ai_applications=int((diag["applications_ai"] > 0).sum()),
        examples_rows=len(example_rows),
    )


if __name__ == "__main__":
    main()
