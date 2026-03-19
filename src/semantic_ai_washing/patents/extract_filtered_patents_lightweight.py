"""Lightweight PatentsView extractor using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from semantic_ai_washing.patents.keyword_matching import (
    compile_boundary_pattern,
    load_keywords,
    matched_keywords,
    normalize_org_name,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-year", type=int, default=2019)
    parser.add_argument(
        "--data-root",
        default=os.getenv("PATENT_DATA_ROOT", "/Users/soheilkhodadadi/DataWork/patentsview"),
    )
    parser.add_argument(
        "--company-lookup",
        default="data/metadata/company_lookup_active_annual_allyears_2021_2024.csv",
    )
    parser.add_argument(
        "--company-aliases",
        default="data/metadata/company_aliases_active_annual_allyears_2021_2024.csv",
    )
    parser.add_argument(
        "--output-counts",
        default="data/processed/patents/ai_patent_counts_filtered_{suffix}.csv",
    )
    parser.add_argument(
        "--output-examples",
        default="data/processed/patents/ai_patent_examples_{suffix}.csv",
    )
    parser.add_argument(
        "--output-diag",
        default="data/processed/patents/patents_diagnostics_{suffix}.csv",
    )
    parser.add_argument(
        "--keywords-path",
        default="data/metadata/patent_keywords.txt",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/data/patent_extraction_progress_{suffix}.json",
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


def main() -> None:
    args = parse_args()
    suffix = f"{args.min_year}plus"
    progress_path = Path(args.progress_report.format(suffix=suffix))
    output_counts = Path(args.output_counts.format(suffix=suffix))
    output_examples = Path(args.output_examples.format(suffix=suffix))
    output_diag = Path(args.output_diag.format(suffix=suffix))
    for path in [output_counts, output_examples, output_diag]:
        path.parent.mkdir(parents=True, exist_ok=True)

    data_root = Path(args.data_root)
    assignee_path = data_root / "patent_assignee.tsv"
    patent_path = data_root / "patent.tsv"
    abstract_path = data_root / "patent_abstract.tsv"

    firms = load_company_lookup(args.company_lookup)
    aliases = load_company_aliases(args.company_aliases)
    term_index = build_term_index(firms, aliases)
    write_progress(
        progress_path,
        "term_index_ready",
        min_year=args.min_year,
        keywords_path=args.keywords_path,
        normalized_company_terms=len(term_index),
    )

    matched_by_patent: dict[str, list[tuple[str, str]]] = defaultdict(list)
    with open(assignee_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            org = row.get("disambig_assignee_organization")
            if not org:
                continue
            org_clean = normalize_org_name(org)
            if org_clean not in term_index:
                continue
            patent_id = str(row.get("patent_id", "")).strip()
            for item in term_index[org_clean]:
                matched_by_patent[patent_id].append(item)
    patent_ids = set(matched_by_patent)
    write_progress(
        progress_path,
        "assignee_matching_complete",
        matched_patent_rows=len(patent_ids),
        matched_firms=len({cik for rows in matched_by_patent.values() for cik, _ in rows}),
    )

    patents: dict[str, dict[str, object]] = {}
    with open(patent_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            patent_id = str(row.get("patent_id", "")).strip()
            if patent_id not in patent_ids:
                continue
            patent_date = str(row.get("patent_date", "")).strip()
            try:
                year = int(patent_date[:4])
            except Exception:
                continue
            if year < args.min_year:
                continue
            patents[patent_id] = {
                "patent_title": str(row.get("patent_title", "")).strip(),
                "patent_date": patent_date,
                "year": year,
            }
    filtered_ids = set(patents)
    write_progress(progress_path, "patent_rows_filtered", filtered_patent_rows=len(filtered_ids))

    abstracts: dict[str, str] = {}
    with open(abstract_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            patent_id = str(row.get("patent_id", "")).strip()
            if patent_id in filtered_ids:
                abstracts[patent_id] = str(row.get("patent_abstract", "")).strip()
    write_progress(
        progress_path,
        "abstracts_loaded",
        filtered_patent_rows=len(filtered_ids),
        abstracts_loaded=len(abstracts),
    )

    pattern = compile_boundary_pattern(load_keywords(args.keywords_path))
    rows: list[dict[str, object]] = []
    totals: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    ai_hits: dict[tuple[str, str, int], set[str]] = defaultdict(set)
    matched_premerge: dict[tuple[str, str], int] = defaultdict(int)

    for patent_id in filtered_ids:
        patent = patents[patent_id]
        title = str(patent["patent_title"])
        abstract = abstracts.get(patent_id, "")
        text = (title + " " + abstract).lower()
        mk = matched_keywords(text, pattern)
        seen_pairs: set[tuple[str, str]] = set()
        for cik, name in matched_by_patent[patent_id]:
            pair = (cik, name)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            matched_premerge[pair] += 1
            key = (cik, name, int(patent["year"]))
            totals[key].add(patent_id)
            if mk:
                ai_hits[key].add(patent_id)
                rows.append(
                    {
                        "cik": cik,
                        "name": name,
                        "year": int(patent["year"]),
                        "patent_id": patent_id,
                        "patent_title": title,
                        "patent_abstract": abstract,
                        "matched_keywords": mk,
                        "patent_date": patent["patent_date"],
                    }
                )

    write_progress(
        progress_path,
        "keyword_tagging_complete",
        candidate_patent_rows=sum(len(v) for v in totals.values()),
        ai_patent_rows=len(rows),
    )

    counts_rows: list[dict[str, object]] = []
    for key in sorted(totals):
        cik, name, year = key
        patents_total = len(totals[key])
        patents_ai = len(ai_hits.get(key, set()))
        counts_rows.append(
            {
                "cik": cik,
                "name": name,
                "year": year,
                "patents_total": patents_total,
                "patents_ai": patents_ai,
                "ai_share": (patents_ai / patents_total) if patents_total else "",
            }
        )
    with open(output_counts, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["cik", "name", "year", "patents_total", "patents_ai", "ai_share"],
        )
        writer.writeheader()
        writer.writerows(counts_rows)

    example_rows: list[dict[str, object]] = []
    latest_by_key: dict[tuple[str, str, int], dict[str, object]] = {}
    for row in rows:
        key = (str(row["cik"]), str(row["name"]), int(row["year"]))
        prev = latest_by_key.get(key)
        if prev is None or str(row["patent_date"]) >= str(prev["patent_date"]):
            latest_by_key[key] = row
    for row in latest_by_key.values():
        example_rows.append(
            {
                "cik": row["cik"],
                "name": row["name"],
                "year": row["year"],
                "patent_id": row["patent_id"],
                "patent_title": row["patent_title"],
                "patent_abstract": row["patent_abstract"],
                "matched_keywords": row["matched_keywords"],
            }
        )
    with open(output_examples, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cik",
                "name",
                "year",
                "patent_id",
                "patent_title",
                "patent_abstract",
                "matched_keywords",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(example_rows, key=lambda row: (row["cik"], row["year"])))

    diag_rows: list[dict[str, object]] = []
    firm_totals: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"patents_total": 0, "patents_ai": 0})
    for row in counts_rows:
        key = (str(row["cik"]), str(row["name"]))
        firm_totals[key]["patents_total"] += int(row["patents_total"])
        firm_totals[key]["patents_ai"] += int(row["patents_ai"])
    for (cik, name), payload in sorted(firm_totals.items()):
        patents_total = payload["patents_total"]
        patents_ai = payload["patents_ai"]
        diag_rows.append(
            {
                "cik": cik,
                "name": name,
                "patents_total": patents_total,
                "patents_ai": patents_ai,
                "ai_share_overall": (patents_ai / patents_total) if patents_total else "",
                "matched_patent_rows_premerge": matched_premerge.get((cik, name), 0),
            }
        )
    with open(output_diag, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cik",
                "name",
                "patents_total",
                "patents_ai",
                "ai_share_overall",
                "matched_patent_rows_premerge",
            ],
        )
        writer.writeheader()
        writer.writerows(diag_rows)

    write_progress(
        progress_path,
        "completed",
        output_counts_path=str(output_counts),
        output_examples_path=str(output_examples),
        output_diag_path=str(output_diag),
        firm_year_rows=len(counts_rows),
        firms_with_any_patents=sum(1 for payload in firm_totals.values() if payload["patents_total"] > 0),
        firms_with_ai_patents=sum(1 for payload in firm_totals.values() if payload["patents_ai"] > 0),
        examples_rows=len(example_rows),
    )


if __name__ == "__main__":
    main()
