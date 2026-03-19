"""Lightweight patent keyword benchmark using only the Python standard library."""

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
    parser.add_argument("--min-year", type=int, required=True)
    parser.add_argument("--max-year", type=int, required=True)
    parser.add_argument("--examples-per-set", type=int, default=20)
    parser.add_argument(
        "--keyword-set",
        action="append",
        required=True,
        help="Keyword set spec in the form label=path.",
    )
    parser.add_argument(
        "--output-report",
        default="reports/data/patent_keyword_benchmark_lightweight_v1.json",
    )
    parser.add_argument(
        "--output-examples",
        default="reports/data/patent_keyword_benchmark_lightweight_examples_v1.csv",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/data/patent_keyword_benchmark_lightweight_progress_v1.json",
    )
    return parser.parse_args()


def parse_keyword_set(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise ValueError(f"Keyword set spec must be name=path, got: {spec}")
    label, path = spec.split("=", 1)
    return label.strip(), path.strip()


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
    progress_path = Path(args.progress_report)
    data_root = Path(args.data_root)
    assignee_path = data_root / "patent_assignee.tsv"
    patent_path = data_root / "patent.tsv"
    abstract_path = data_root / "patent_abstract.tsv"

    firms = load_company_lookup(args.company_lookup)
    aliases = load_company_aliases(args.company_aliases)
    term_index = build_term_index(firms, aliases)
    write_progress(progress_path, "term_index_ready", normalized_company_terms=len(term_index))

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
            if not (args.min_year <= year <= args.max_year):
                continue
            patents[patent_id] = {
                "patent_title": str(row.get("patent_title", "")).strip(),
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

    rows: list[dict[str, object]] = []
    for patent_id in filtered_ids:
        patent = patents[patent_id]
        title = str(patent["patent_title"])
        abstract = abstracts.get(patent_id, "")
        text = (title + " " + abstract).lower()
        seen_pairs: set[tuple[str, str]] = set()
        for cik, name in matched_by_patent[patent_id]:
            pair = (cik, name)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            rows.append(
                {
                    "cik": cik,
                    "name": name,
                    "year": int(patent["year"]),
                    "patent_id": patent_id,
                    "patent_title": title,
                    "patent_abstract": abstract,
                    "text": text,
                }
            )
    write_progress(
        progress_path,
        "candidate_pool_ready",
        candidate_patent_rows=len(rows),
        candidate_firms=len({row["cik"] for row in rows}),
    )

    keyword_specs = [parse_keyword_set(spec) for spec in args.keyword_set]
    results: list[dict[str, object]] = []
    example_rows: list[dict[str, object]] = []
    for label, keywords_path in keyword_specs:
        pattern = compile_boundary_pattern(load_keywords(keywords_path))
        firm_year_hits: dict[tuple[str, int], set[str]] = defaultdict(set)
        firm_hits: set[str] = set()
        patent_hits: set[str] = set()
        captured = 0
        for row in rows:
            matched = matched_keywords(str(row["text"]), pattern)
            if not matched:
                continue
            cik = str(row["cik"])
            year = int(row["year"])
            patent_id = str(row["patent_id"])
            firm_year_hits[(cik, year)].add(patent_id)
            firm_hits.add(cik)
            patent_hits.add(patent_id)
            if captured < args.examples_per_set:
                example_rows.append(
                    {
                        "keyword_set": label,
                        "cik": cik,
                        "name": row["name"],
                        "year": year,
                        "patent_id": patent_id,
                        "patent_title": row["patent_title"],
                        "patent_abstract": row["patent_abstract"],
                        "matched_keywords": matched,
                    }
                )
                captured += 1
        results.append(
            {
                "keyword_set": label,
                "keywords_path": keywords_path,
                "keyword_count": len(load_keywords(keywords_path)),
                "firm_year_rows": len({(row["cik"], row["year"]) for row in rows}),
                "firm_years_with_ai_patents": len(firm_year_hits),
                "firms_with_ai_patents": len(firm_hits),
                "total_patents_ai": len(patent_hits),
            }
        )
        write_progress(progress_path, "benchmarking", completed_keyword_sets=results)

    report = {
        "min_year": args.min_year,
        "max_year": args.max_year,
        "candidate_patent_rows": len(rows),
        "candidate_firms": len({row["cik"] for row in rows}),
        "keyword_sets": results,
    }
    Path(args.output_report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_examples).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    with open(args.output_examples, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "keyword_set",
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
        writer.writerows(example_rows)
    write_progress(progress_path, "completed", **report)


if __name__ == "__main__":
    main()
