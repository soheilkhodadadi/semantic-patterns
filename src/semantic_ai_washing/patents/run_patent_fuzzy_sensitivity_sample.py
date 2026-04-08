"""Run a bounded fuzzy-matching sensitivity sample for patent/app data."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

from semantic_ai_washing.patents.extract_filtered_patents_lightweight import (
    build_term_index as build_grant_term_index,
    load_company_aliases as load_grant_company_aliases,
    load_company_lookup as load_grant_company_lookup,
)
from semantic_ai_washing.patents.extract_filtered_pregrant_applications_lightweight import (
    _clean_field,
    _dedupe_application_matches,
)
from semantic_ai_washing.patents.keyword_matching import (
    compile_boundary_pattern,
    load_keywords,
    matched_keywords,
    normalize_org_name,
)
from semantic_ai_washing.patents.patentsview_sources import resolve_patentsview_layout
from semantic_ai_washing.patents.pregrant_sources import resolve_pregrant_patentsview_layout


@dataclass(frozen=True)
class TermRecord:
    term: str
    cik: str
    name: str
    tokens: frozenset[str]


def _partial_ratio(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    if shorter in longer:
        return 1.0
    best = 0.0
    matcher = SequenceMatcher(None, shorter, longer)
    for block in matcher.get_matching_blocks():
        start = max(0, block[1] - block[0])
        window = longer[start : start + len(shorter)]
        if not window:
            continue
        best = max(best, SequenceMatcher(None, shorter, window).ratio())
    return best


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument(
        "--family",
        choices=["grant", "pregrant", "both"],
        default="both",
    )
    parser.add_argument(
        "--threshold",
        action="append",
        type=float,
        dest="thresholds",
        default=[],
        help="Similarity threshold between 0 and 1. May be repeated. Default: 0.90 and 0.95.",
    )
    parser.add_argument(
        "--min-gap",
        type=float,
        default=0.03,
        help="Minimum gap between best and second-best fuzzy scores.",
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
        "--keywords-path",
        default="data/metadata/patent_keywords.txt",
    )
    parser.add_argument(
        "--grant-data-root",
        default="/Users/soheilkhodadadi/DataWork/patentsview",
    )
    parser.add_argument(
        "--pregrant-data-root",
        default="/Users/soheilkhodadadi/DataWork/patentsview/pregrant",
    )
    parser.add_argument(
        "--output-report",
        default="reports/final/ai_washing_patent_fuzzy_sensitivity_2024_v1.json",
    )
    parser.add_argument(
        "--output-examples",
        default="reports/final/ai_washing_patent_fuzzy_sensitivity_2024_v1_examples.csv",
    )
    return parser.parse_args()


def build_term_catalog(
    company_lookup_path: str, company_aliases_path: str
) -> tuple[dict[str, list[tuple[str, str]]], list[TermRecord]]:
    firms = load_grant_company_lookup(company_lookup_path)
    aliases = load_grant_company_aliases(company_aliases_path)
    term_index = build_grant_term_index(firms, aliases)
    catalog = [
        TermRecord(
            term=term,
            cik=rows[0][0],
            name=rows[0][1],
            tokens=frozenset(token for token in term.split() if token),
        )
        for term, rows in term_index.items()
    ]
    return term_index, catalog


def fuzzy_best_match(
    org_clean: str,
    *,
    catalog: list[TermRecord],
    threshold: float,
    min_gap: float,
) -> tuple[TermRecord | None, float, float | None]:
    if not org_clean:
        return None, 0.0, None

    org_tokens = {token for token in org_clean.split() if token}
    if not org_tokens:
        return None, 0.0, None

    candidates = [record for record in catalog if record.tokens & org_tokens]
    if not candidates:
        return None, 0.0, None

    if max(len(org_clean.replace(" ", "")), *(len(rec.term.replace(" ", "")) for rec in candidates)) <= 4:
        return None, 0.0, None

    scored: list[tuple[float, TermRecord]] = []
    for record in candidates:
        full_ratio = SequenceMatcher(None, org_clean, record.term).ratio()
        partial_ratio = _partial_ratio(org_clean, record.term)
        score = max(full_ratio, partial_ratio)
        if score >= threshold:
            scored.append((score, record))
    if not scored:
        return None, 0.0, None

    scored.sort(key=lambda item: item[0], reverse=True)
    top_score, top_record = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else None
    if second_score is not None and (top_score - second_score) < min_gap:
        return None, top_score, second_score
    return top_record, top_score, second_score


def _load_grant_target_patents(layout, *, year: int) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    patents: dict[str, dict[str, str]] = {}
    with open(layout.patent, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            patent_id = str(row.get("patent_id", "")).strip()
            patent_date = str(row.get("patent_date", "")).strip()
            try:
                patent_year = int(patent_date[:4])
            except Exception:
                continue
            if patent_year != year:
                continue
            patents[patent_id] = {
                "patent_date": patent_date,
                "patent_title": str(row.get("patent_title", "")).strip(),
            }

    abstracts: dict[str, str] = {}
    patent_ids = set(patents)
    with open(layout.abstract, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            patent_id = str(row.get("patent_id", "")).strip()
            if patent_id in patent_ids:
                abstracts[patent_id] = str(row.get("patent_abstract", "")).strip()
    return patents, abstracts


def evaluate_grant_sample(
    *,
    year: int,
    threshold: float,
    min_gap: float,
    term_index: dict[str, list[tuple[str, str]]],
    catalog: list[TermRecord],
    keywords_path: str,
    data_root: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    layout = resolve_patentsview_layout(data_root)
    patents, abstracts = _load_grant_target_patents(layout, year=year)
    target_patent_ids = set(patents)
    pattern = compile_boundary_pattern(load_keywords(keywords_path))

    exact_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    fuzzy_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    fuzzy_examples: list[dict[str, object]] = []
    resolution_cache: dict[str, tuple[str, tuple[str, str] | None, float, float | None, str | None]] = {}

    with open(layout.assignee, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            patent_id = str(row.get("patent_id", "")).strip()
            if patent_id not in target_patent_ids:
                continue
            org_raw = str(row.get("disambig_assignee_organization", "")).strip()
            if not org_raw:
                continue
            org_clean = normalize_org_name(org_raw)
            cached = resolution_cache.get(org_clean)
            if cached is None:
                exact = term_index.get(org_clean)
                if exact:
                    resolution_cache[org_clean] = ("exact", exact[0], 1.0, None, org_clean)
                    cached = resolution_cache[org_clean]
                else:
                    match, score, second_score = fuzzy_best_match(
                        org_clean,
                        catalog=catalog,
                        threshold=threshold,
                        min_gap=min_gap,
                    )
                    if match is None:
                        resolution_cache[org_clean] = ("none", None, score, second_score, None)
                    else:
                        resolution_cache[org_clean] = (
                            "fuzzy",
                            (match.cik, match.name),
                            score,
                            second_score,
                            match.term,
                        )
                    cached = resolution_cache[org_clean]

            match_type, pair, score, second_score, matched_term = cached
            if match_type == "exact" and pair is not None:
                exact_pairs[patent_id].add(pair)
                continue
            if match_type != "fuzzy" or pair is None:
                continue

            fuzzy_pairs[patent_id].add(pair)
            fuzzy_examples.append(
                {
                    "family": "grant",
                    "year": year,
                    "threshold": threshold,
                    "id": patent_id,
                    "org_raw": org_raw,
                    "org_clean": org_clean,
                    "matched_term": matched_term or "",
                    "score": round(score, 4),
                    "second_score": round(second_score, 4) if second_score is not None else "",
                    "cik": pair[0],
                    "name": pair[1],
                    "title": patents[patent_id]["patent_title"],
                    "matched_keywords": matched_keywords(
                        f"{patents[patent_id]['patent_title']} {abstracts.get(patent_id, '')}".lower(),
                        pattern,
                    ),
                }
            )

    def aggregate(pair_map: dict[str, set[tuple[str, str]]]) -> tuple[int, int, int]:
        totals = 0
        ai_total = 0
        firms = set()
        for patent_id, pairs in pair_map.items():
            title = patents[patent_id]["patent_title"]
            abstract = abstracts.get(patent_id, "")
            mk = matched_keywords(f"{title} {abstract}".lower(), pattern)
            for cik, _ in pairs:
                firms.add(cik)
                totals += 1
                if mk:
                    ai_total += 1
        return totals, ai_total, len(firms)

    exact_total, exact_ai, exact_firms = aggregate(exact_pairs)
    combined_pairs = {
        patent_id: set(exact_pairs.get(patent_id, set())) | set(fuzzy_pairs.get(patent_id, set()))
        for patent_id in target_patent_ids
        if exact_pairs.get(patent_id) or fuzzy_pairs.get(patent_id)
    }
    fuzzy_total, fuzzy_ai, fuzzy_firms = aggregate(combined_pairs)
    summary = {
        "family": "grant",
        "year": year,
        "threshold": threshold,
        "min_gap": min_gap,
        "baseline_total_patent_matches": exact_total,
        "baseline_ai_patent_matches": exact_ai,
        "baseline_firms": exact_firms,
        "fuzzy_total_patent_matches": fuzzy_total,
        "fuzzy_ai_patent_matches": fuzzy_ai,
        "fuzzy_firms": fuzzy_firms,
        "added_total_patent_matches": fuzzy_total - exact_total,
        "added_ai_patent_matches": fuzzy_ai - exact_ai,
        "added_firm_count": fuzzy_firms - exact_firms,
        "fuzzy_only_patent_ids": len(fuzzy_pairs),
    }
    return summary, fuzzy_examples


def _load_pregrant_target_applications(layout, *, year: int) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, dict[str, str]]]:
    applications: dict[str, dict[str, str]] = {}
    with open(layout.published_application, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            filing_date = _clean_field(row.get("filing_date"))
            try:
                filing_year = int(filing_date[:4])
            except Exception:
                continue
            if filing_year != year:
                continue
            applications[pgpub_id] = {
                "pgpub_id": pgpub_id,
                "application_id": _clean_field(row.get("application_id")),
                "filing_date": filing_date,
                "published_date": _clean_field(row.get("published_date")),
                "application_title": _clean_field(row.get("application_title")),
            }

    abstracts: dict[str, str] = {}
    with open(layout.abstract, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if pgpub_id in applications:
                abstracts[pgpub_id] = _clean_field(row.get("application_abstract"))

    crosswalk: dict[str, dict[str, str]] = {}
    with open(layout.crosswalk, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            pgpub_id = _clean_field(row.get("pgpub_id"))
            if pgpub_id in applications:
                crosswalk[pgpub_id] = {
                    "patent_id": _clean_field(row.get("patent_id")),
                    "current_pgpub_id_flag": _clean_field(row.get("current_pgpub_id_flag")),
                    "current_patent_id_flag": _clean_field(row.get("current_patent_id_flag")),
                }
    return applications, abstracts, crosswalk


def evaluate_pregrant_sample(
    *,
    year: int,
    threshold: float,
    min_gap: float,
    term_index: dict[str, list[tuple[str, str]]],
    catalog: list[TermRecord],
    keywords_path: str,
    data_root: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    layout = resolve_pregrant_patentsview_layout(data_root)
    applications, abstracts, crosswalk = _load_pregrant_target_applications(layout, year=year)
    target_pgpub_ids = set(applications)
    pattern = compile_boundary_pattern(load_keywords(keywords_path))

    exact_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    fuzzy_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
    fuzzy_examples: list[dict[str, object]] = []
    resolution_cache: dict[str, tuple[str, tuple[str, str] | None, float, float | None, str | None]] = {}

    def process_org_file(path: Path, *, org_column: str, exact_fallback_only: bool, fuzzy_fallback_only: bool) -> None:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                pgpub_id = _clean_field(row.get("pgpub_id"))
                if pgpub_id not in target_pgpub_ids:
                    continue
                if exact_fallback_only and exact_pairs.get(pgpub_id):
                    continue
                org_raw = _clean_field(row.get(org_column))
                if not org_raw:
                    continue
                org_clean = normalize_org_name(org_raw)
                cached = resolution_cache.get(org_clean)
                if cached is None:
                    exact = term_index.get(org_clean)
                    if exact:
                        resolution_cache[org_clean] = ("exact", exact[0], 1.0, None, org_clean)
                        cached = resolution_cache[org_clean]
                    else:
                        match, score, second_score = fuzzy_best_match(
                            org_clean,
                            catalog=catalog,
                            threshold=threshold,
                            min_gap=min_gap,
                        )
                        if match is None:
                            resolution_cache[org_clean] = ("none", None, score, second_score, None)
                        else:
                            resolution_cache[org_clean] = (
                                "fuzzy",
                                (match.cik, match.name),
                                score,
                                second_score,
                                match.term,
                            )
                        cached = resolution_cache[org_clean]

                match_type, pair, score, second_score, matched_term = cached
                if match_type == "exact" and pair is not None:
                    exact_pairs[pgpub_id].add(pair)
                    continue
                if fuzzy_fallback_only and (exact_pairs.get(pgpub_id) or fuzzy_pairs.get(pgpub_id)):
                    continue
                if match_type != "fuzzy" or pair is None:
                    continue

                fuzzy_pairs[pgpub_id].add(pair)
                application = applications[pgpub_id]
                fuzzy_examples.append(
                    {
                        "family": "pregrant",
                        "year": year,
                        "threshold": threshold,
                        "id": pgpub_id,
                        "org_raw": org_raw,
                        "org_clean": org_clean,
                        "matched_term": matched_term or "",
                        "score": round(score, 4),
                        "second_score": round(second_score, 4) if second_score is not None else "",
                        "cik": pair[0],
                        "name": pair[1],
                        "title": application["application_title"],
                        "matched_keywords": matched_keywords(
                            f"{application['application_title']} {abstracts.get(pgpub_id, '')}".lower(),
                            pattern,
                        ),
                    }
                )

    process_org_file(
        layout.assignee,
        org_column="disambig_assignee_organization",
        exact_fallback_only=False,
        fuzzy_fallback_only=False,
    )
    if layout.applicant is not None:
        process_org_file(
            layout.applicant,
            org_column="raw_applicant_organization",
            exact_fallback_only=True,
            fuzzy_fallback_only=True,
        )

    def aggregate(pair_map: dict[str, set[tuple[str, str]]]) -> tuple[int, int, int]:
        rows: list[dict[str, object]] = []
        for pgpub_id, pairs in pair_map.items():
            application = applications[pgpub_id]
            cross = crosswalk.get(
                pgpub_id,
                {
                    "patent_id": "",
                    "current_pgpub_id_flag": "",
                    "current_patent_id_flag": "",
                },
            )
            title = application["application_title"]
            abstract = abstracts.get(pgpub_id, "")
            mk = matched_keywords(f"{title} {abstract}".lower(), pattern)
            for cik, name in pairs:
                rows.append(
                    {
                        "cik": cik,
                        "name": name,
                        "year": year,
                        "pgpub_id": pgpub_id,
                        "application_id": application["application_id"],
                        "patent_id": cross["patent_id"],
                        "filing_date": application["filing_date"],
                        "published_date": application["published_date"],
                        "application_title": title,
                        "application_abstract": abstract,
                        "matched_keywords": mk,
                        "is_ai": int(bool(mk)),
                        "current_pgpub_id_flag": cross["current_pgpub_id_flag"],
                        "current_patent_id_flag": cross["current_patent_id_flag"],
                    }
                )
        frame = pd.DataFrame.from_records(rows)
        if frame.empty:
            return 0, 0, 0
        frame = _dedupe_application_matches(frame)
        applications_total = int(frame["application_id"].nunique())
        applications_ai = int(frame.loc[frame["is_ai"] == 1, "application_id"].nunique())
        firms = int(frame["cik"].nunique())
        return applications_total, applications_ai, firms

    exact_total, exact_ai, exact_firms = aggregate(exact_pairs)
    combined_pairs = {
        pgpub_id: set(exact_pairs.get(pgpub_id, set())) | set(fuzzy_pairs.get(pgpub_id, set()))
        for pgpub_id in target_pgpub_ids
        if exact_pairs.get(pgpub_id) or fuzzy_pairs.get(pgpub_id)
    }
    fuzzy_total, fuzzy_ai, fuzzy_firms = aggregate(combined_pairs)
    summary = {
        "family": "pregrant",
        "year": year,
        "threshold": threshold,
        "min_gap": min_gap,
        "baseline_total_applications": exact_total,
        "baseline_ai_applications": exact_ai,
        "baseline_firms": exact_firms,
        "fuzzy_total_applications": fuzzy_total,
        "fuzzy_ai_applications": fuzzy_ai,
        "fuzzy_firms": fuzzy_firms,
        "added_total_applications": fuzzy_total - exact_total,
        "added_ai_applications": fuzzy_ai - exact_ai,
        "added_firm_count": fuzzy_firms - exact_firms,
        "fuzzy_only_pgpub_ids": len(fuzzy_pairs),
    }
    return summary, fuzzy_examples


def main() -> None:
    args = parse_args()
    thresholds = args.thresholds or [0.90, 0.95]
    term_index, catalog = build_term_catalog(args.company_lookup, args.company_aliases)

    summaries: list[dict[str, object]] = []
    examples: list[dict[str, object]] = []

    families = ["grant", "pregrant"] if args.family == "both" else [args.family]
    for family in families:
        for threshold in thresholds:
            if family == "grant":
                summary, family_examples = evaluate_grant_sample(
                    year=args.year,
                    threshold=threshold,
                    min_gap=args.min_gap,
                    term_index=term_index,
                    catalog=catalog,
                    keywords_path=args.keywords_path,
                    data_root=args.grant_data_root,
                )
            else:
                summary, family_examples = evaluate_pregrant_sample(
                    year=args.year,
                    threshold=threshold,
                    min_gap=args.min_gap,
                    term_index=term_index,
                    catalog=catalog,
                    keywords_path=args.keywords_path,
                    data_root=args.pregrant_data_root,
                )
            summaries.append(summary)
            examples.extend(family_examples)

    output_report = Path(args.output_report)
    output_examples = Path(args.output_examples)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_examples.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(
        json.dumps(
            {
                "status": "passed",
                "year": args.year,
                "thresholds": thresholds,
                "min_gap": args.min_gap,
                "results": summaries,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    pd.DataFrame.from_records(examples).sort_values(
        ["family", "threshold", "score"], ascending=[True, True, False]
    ).to_csv(output_examples, index=False)
    print(output_report)
    print(output_examples)


if __name__ == "__main__":
    main()
