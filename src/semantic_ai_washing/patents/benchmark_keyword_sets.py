"""Benchmark multiple patent keyword sets on the same matched patent candidate pool."""

from __future__ import annotations

import argparse
import json
import os
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
from semantic_ai_washing.patents.patentsview_sources import (
    load_application_filing_date_lookup,
    resolve_patentsview_paths,
)


def load_company_lookup(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame["name_clean"] = frame["name_clean"].map(normalize_org_name)
    return frame


def load_company_aliases(path: str) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = defaultdict(list)
    if not os.path.exists(path):
        return aliases
    frame = pd.read_csv(path)
    for _, row in frame.iterrows():
        cik = str(row.get("cik", "")).strip()
        alias = normalize_org_name(str(row.get("alias", "")).strip())
        if cik and alias:
            aliases[cik].append(alias)
    return aliases


def build_term_index(
    firms: pd.DataFrame, aliases: dict[str, list[str]]
) -> dict[str, list[dict[str, str]]]:
    raw_index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for _, firm in firms.iterrows():
        cik = str(firm.get("cik", "")).strip()
        name = str(firm.get("name", "")).strip()
        base = normalize_org_name(str(firm.get("name_clean", "")).strip())
        if not cik or not name:
            continue
        terms: list[tuple[str, str]] = []
        if base:
            terms.append((base, "name_exact"))
        for alias in aliases.get(cik, []):
            alias_norm = normalize_org_name(alias)
            if alias_norm:
                terms.append((alias_norm, "alias_exact"))
        seen: set[str] = set()
        for term, rule in terms:
            if term in seen:
                continue
            seen.add(term)
            raw_index[term].append({"cik": cik, "name": name, "match_rule": rule})

    term_index: dict[str, list[dict[str, str]]] = {}
    for term, rows in raw_index.items():
        unique_ciks = {row["cik"] for row in rows}
        if len(unique_ciks) == 1:
            term_index[term] = rows
    return term_index


def stream_assignee_matches(
    path: str,
    term_index: dict[str, list[dict[str, str]]],
    chunk_size: int,
) -> pd.DataFrame:
    matched_blocks = []
    for chunk in pd.read_csv(
        path,
        sep="\t",
        usecols=["patent_id", "disambig_assignee_organization"],
        dtype={"patent_id": str},
        chunksize=chunk_size,
    ):
        chunk = chunk.dropna(subset=["disambig_assignee_organization"]).copy()
        chunk["org_clean"] = chunk["disambig_assignee_organization"].map(normalize_org_name)
        chunk = chunk[chunk["org_clean"].isin(term_index)]
        if chunk.empty:
            continue
        records = []
        for patent_id, org_raw, org_clean in chunk[
            ["patent_id", "disambig_assignee_organization", "org_clean"]
        ].itertuples(index=False):
            for match in term_index.get(org_clean, []):
                records.append(
                    {
                        "patent_id": patent_id,
                        "cik": match["cik"],
                        "name": match["name"],
                        "match_rule": match["match_rule"],
                        "match_term": org_clean,
                        "matched_org": org_raw,
                    }
                )
        if records:
            matched_blocks.append(pd.DataFrame.from_records(records))
    if not matched_blocks:
        return pd.DataFrame(
            columns=["patent_id", "cik", "name", "match_rule", "match_term", "matched_org"]
        )
    return pd.concat(matched_blocks, ignore_index=True).drop_duplicates(
        subset=["patent_id", "cik"]
    )


def load_filtered_patent_rows(
    patent_path: str,
    abstract_path: str,
    patent_ids: set[str],
    *,
    application_path: str | None,
    timing_field: str,
    min_year: int,
    max_year: int,
    patent_chunksize: int,
) -> pd.DataFrame:
    patent_cols = ["patent_id", "patent_date", "patent_title"]
    abstract_cols = ["patent_id", "patent_abstract"]
    patents = []
    for chunk in pd.read_csv(
        patent_path,
        sep="\t",
        usecols=patent_cols,
        dtype={"patent_id": str},
        chunksize=patent_chunksize,
    ):
        chunk = chunk[chunk["patent_id"].isin(patent_ids)].copy()
        if chunk.empty:
            continue
        if not chunk.empty:
            patents.append(chunk)
    patents_df = pd.concat(patents, ignore_index=True) if patents else pd.DataFrame(columns=patent_cols)
    if patents_df.empty:
        return pd.DataFrame(columns=patent_cols + ["filing_date", "timing_date", "year"])
    if timing_field == "application":
        if not application_path:
            raise FileNotFoundError("Application timing requested but no application file was resolved.")
        filing_dates = load_application_filing_date_lookup(
            application_path,
            patent_ids,
            chunksize=patent_chunksize,
        )
        patents_df["filing_date"] = patents_df["patent_id"].map(filing_dates).fillna("")
        patents_df["timing_date"] = patents_df["filing_date"]
    else:
        patents_df["filing_date"] = ""
        patents_df["timing_date"] = patents_df["patent_date"]

    patents_df = patents_df[
        patents_df["timing_date"].notna() & (patents_df["timing_date"].astype(str).str.strip() != "")
    ].copy()
    patents_df["year"] = pd.to_datetime(patents_df["timing_date"], errors="coerce").dt.year
    patents_df = patents_df[patents_df["year"].notna()].copy()
    patents_df["year"] = patents_df["year"].astype(int)
    patents_df = patents_df[patents_df["year"].between(min_year, max_year, inclusive="both")]

    filtered_ids = set(patents_df["patent_id"].astype(str)) if not patents_df.empty else set()

    abstracts = []
    if filtered_ids:
        for chunk in pd.read_csv(
            abstract_path,
            sep="\t",
            usecols=abstract_cols,
            dtype={"patent_id": str},
            chunksize=patent_chunksize,
        ):
            chunk = chunk[chunk["patent_id"].isin(filtered_ids)]
            if not chunk.empty:
                abstracts.append(chunk)
    abstracts_df = (
        pd.concat(abstracts, ignore_index=True) if abstracts else pd.DataFrame(columns=abstract_cols)
    )
    merged = patents_df.merge(abstracts_df, on="patent_id", how="left")
    return merged


def benchmark_keyword_set(
    frame: pd.DataFrame, label: str, path: str, examples_per_set: int
) -> tuple[dict[str, object], pd.DataFrame]:
    keywords = load_keywords(path)
    pattern = compile_boundary_pattern(keywords)
    working = frame.copy()
    working["matched_keywords"] = working["text"].fillna("").map(
        lambda value: matched_keywords(value, pattern)
    )
    working["has_ai"] = working["matched_keywords"] != ""
    positives = working[working["has_ai"]].copy()

    agg = (
        working.groupby(["cik", "name", "year"], as_index=False)
        .agg(
            patents_total=("patent_id", "nunique"),
        )
        .merge(
            positives.groupby(["cik", "name", "year"], as_index=False)
            .agg(patents_ai=("patent_id", "nunique")),
            on=["cik", "name", "year"],
            how="left",
        )
        .fillna({"patents_ai": 0})
    )

    result = {
        "keyword_set": label,
        "keywords_path": path,
        "keyword_count": len(keywords),
        "firm_year_rows": int(len(agg)),
        "firm_years_with_ai_patents": int((agg["patents_ai"] > 0).sum()),
        "firms_with_ai_patents": int(agg.loc[agg["patents_ai"] > 0, "cik"].nunique()),
        "total_patents_ai": int(agg["patents_ai"].sum()),
    }

    example_cols = [
        "cik",
        "name",
        "year",
        "patent_id",
        "patent_title",
        "patent_abstract",
        "matched_keywords",
        "timing_field",
        "timing_date",
        "patent_date",
        "filing_date",
    ]
    for column in example_cols:
        if column not in positives.columns:
            positives[column] = ""
    examples = positives[example_cols].drop_duplicates()
    examples.insert(0, "keyword_set", label)
    return result, examples.head(examples_per_set)


def parse_keyword_set(spec: str) -> tuple[str, str]:
    if "=" not in spec:
        raise ValueError(f"Keyword set spec must be name=path, got: {spec}")
    label, path = spec.split("=", 1)
    return label.strip(), path.strip()


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
    parser.add_argument(
        "--timing-field",
        choices=["application", "grant"],
        default="application",
        help="Which patent date should define year assignment (default: application).",
    )
    parser.add_argument("--assignee-chunksize", type=int, default=250000)
    parser.add_argument("--patent-chunksize", type=int, default=250000)
    parser.add_argument("--examples-per-set", type=int, default=20)
    parser.add_argument(
        "--keyword-set",
        action="append",
        required=True,
        help="Keyword set spec in the form label=path.",
    )
    parser.add_argument(
        "--output-report",
        default="reports/data/patent_keyword_benchmark_v1.json",
    )
    parser.add_argument(
        "--output-examples",
        default="reports/data/patent_keyword_benchmark_examples_v1.csv",
    )
    parser.add_argument(
        "--progress-report",
        default="reports/data/patent_keyword_benchmark_progress_v1.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    progress_path = Path(args.progress_report)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    def write_progress(status: str, **payload: object) -> None:
        progress_path.write_text(
            json.dumps(
                {
                    "status": status,
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "min_year": args.min_year,
                    "max_year": args.max_year,
                    "data_root": args.data_root,
                    "timing_field": args.timing_field,
                    "output_report": args.output_report,
                    "output_examples": args.output_examples,
                    **payload,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    data_root = Path(args.data_root)
    paths = resolve_patentsview_paths(data_root, require_application=args.timing_field == "application")
    assignee_path = paths.assignee
    patent_path = paths.patent
    abstract_path = paths.abstract
    application_path = paths.application

    write_progress("starting")
    firms = load_company_lookup(args.company_lookup)
    aliases = load_company_aliases(args.company_aliases)
    term_index = build_term_index(firms, aliases)
    write_progress("term_index_ready", normalized_company_terms=len(term_index))
    matched = stream_assignee_matches(str(assignee_path), term_index, args.assignee_chunksize)
    write_progress(
        "assignee_matching_complete",
        matched_patent_rows=int(len(matched)),
        matched_firms=int(matched["cik"].nunique()) if not matched.empty else 0,
    )
    patent_ids = set(matched["patent_id"].dropna().astype(str))
    patent_rows = load_filtered_patent_rows(
        str(patent_path),
        str(abstract_path),
        patent_ids,
        application_path=str(application_path) if application_path else None,
        timing_field=args.timing_field,
        min_year=args.min_year,
        max_year=args.max_year,
        patent_chunksize=args.patent_chunksize,
    )
    if patent_rows.empty:
        write_progress("failed", error="No patent rows matched for the requested year window.")
        raise ValueError("No patent rows matched for the requested year window.")

    frame = matched.merge(patent_rows, on="patent_id", how="inner")
    frame["text"] = (
        frame["patent_title"].fillna("").astype(str) + " " + frame["patent_abstract"].fillna("").astype(str)
    ).str.lower()
    write_progress(
        "candidate_pool_ready",
        candidate_patent_rows=int(len(frame)),
        candidate_firms=int(frame["cik"].nunique()),
    )

    results = []
    example_frames = []
    for spec in args.keyword_set:
        label, path = parse_keyword_set(spec)
        result, examples = benchmark_keyword_set(frame, label, path, args.examples_per_set)
        results.append(result)
        example_frames.append(examples)
        write_progress("benchmarking", completed_keyword_sets=results)

    Path(args.output_report).parent.mkdir(parents=True, exist_ok=True)
    report_payload = {
        "min_year": args.min_year,
        "max_year": args.max_year,
        "timing_field": args.timing_field,
        "candidate_patent_rows": int(len(frame)),
        "candidate_firms": int(frame["cik"].nunique()),
        "keyword_sets": results,
    }
    with open(args.output_report, "w", encoding="utf-8") as fh:
        json.dump(report_payload, fh, indent=2)

    examples_out = pd.concat(example_frames, ignore_index=True) if example_frames else pd.DataFrame()
    examples_out.to_csv(args.output_examples, index=False)
    write_progress("completed", **report_payload)
    print(f"[patent-keyword-benchmark] wrote {args.output_report}")
    print(f"[patent-keyword-benchmark] wrote {args.output_examples}")


if __name__ == "__main__":
    main()
