"""
Extracts AI-related patent counts per firm-year using disambiguated assignee names from PatentsView data.

Steps:
- Load PatentsView assignee rows and match `disambig_assignee_organization` to known firms
- Use matching patent_ids to pull from grant tables and, when requested,
  application filing dates
- Filter for AI keywords in title + abstract
- Aggregate AI patent counts per firm-year

Run:
    python -m semantic_ai_washing.patents.extract_filtered_patents --min-year 2014
Outputs:
    - data/processed/patents/ai_patent_counts_filtered_2014plus.csv
    - data/processed/patents/ai_patent_examples_2014plus.csv
    - data/processed/patents/patents_diagnostics_2014plus.csv
"""

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

import pandas as pd

from semantic_ai_washing.patents.keyword_matching import (
    compile_boundary_pattern,
    load_keywords,
    matched_keywords,
    normalize_org_name,
)
from semantic_ai_washing.patents.patentsview_sources import (
    attach_patent_timing,
    load_application_filing_date_lookup,
    resolve_patentsview_paths,
)

parser = argparse.ArgumentParser(
    description="Extract AI-related patents per firm-year with example titles/abstracts."
)
parser.add_argument(
    "--min-year", type=int, default=2014, help="Minimum patent year to include (default: 2014)."
)
parser.add_argument(
    "--max-year",
    type=int,
    default=None,
    help="Maximum patent year to include (default: no upper bound).",
)
parser.add_argument(
    "--data-root",
    default=os.getenv("PATENT_DATA_ROOT", "/Users/soheilkhodadadi/DataWork/patentsview"),
    help="PatentsView root containing PatentsView grant/application files.",
)
parser.add_argument(
    "--timing-field",
    choices=["application", "grant"],
    default="application",
    help="Which date field to use for year assignment (default: application).",
)
parser.add_argument(
    "--company-lookup",
    default="data/metadata/company_lookup_active_annual_allyears_2021_2024.csv",
    help="Canonical company lookup CSV with columns cik/name/name_clean.",
)
parser.add_argument(
    "--company-aliases",
    default="data/metadata/company_aliases_active_annual_allyears_2021_2024.csv",
    help="Optional aliases CSV with cik/alias entries.",
)
parser.add_argument(
    "--output-counts",
    default="data/processed/patents/ai_patent_counts_filtered_{suffix}.csv",
    help="Path to write counts (supports {suffix}).",
)
parser.add_argument(
    "--output-examples",
    default="data/processed/patents/ai_patent_examples_{suffix}.csv",
    help="Path to write example titles/abstracts (supports {suffix}).",
)
parser.add_argument(
    "--output-diag",
    default="data/processed/patents/patents_diagnostics_{suffix}.csv",
    help="Diagnostics CSV path (supports {suffix}).",
)
parser.add_argument(
    "--keywords-path",
    default="data/metadata/patent_keywords.txt",
    help="Keyword file used to tag AI-related patent text.",
)
parser.add_argument(
    "--progress-report",
    default="reports/data/patent_extraction_progress_{suffix}.json",
    help="Progress JSON path (supports {suffix}).",
)
parser.add_argument(
    "--assignee-chunksize",
    type=int,
    default=250000,
    help="Chunk size for streaming patent_assignee.tsv (default: 250000).",
)
parser.add_argument(
    "--patent-chunksize",
    type=int,
    default=250000,
    help="Chunk size for streaming patent/patent_abstract tables (default: 250000).",
)
parser.add_argument(
    "--application-chunksize",
    type=int,
    default=250000,
    help="Chunk size for streaming g_application.tsv (default: 250000).",
)
args = parser.parse_args()
min_year = args.min_year
suffix = f"{min_year}_{args.max_year}" if args.max_year is not None else f"{min_year}plus"

paths = resolve_patentsview_paths(args.data_root, require_application=args.timing_field == "application")
assignee_path = str(paths.assignee)
patent_path = str(paths.patent)
abstract_path = str(paths.abstract)
application_path = str(paths.application) if paths.application else ""
data_root = args.data_root

output_counts_path = args.output_counts.format(suffix=suffix)
output_examples_path = args.output_examples.format(suffix=suffix)
diag_path = args.output_diag.format(suffix=suffix)
progress_path = args.progress_report.format(suffix=suffix)
os.makedirs(os.path.dirname(output_counts_path), exist_ok=True)
os.makedirs(os.path.dirname(output_examples_path), exist_ok=True)
os.makedirs(os.path.dirname(progress_path), exist_ok=True)

firm_lookup_path = args.company_lookup
firm_aliases_path = args.company_aliases

firm_df = pd.read_csv(firm_lookup_path)
firm_df["name_clean"] = firm_df["name_clean"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

firm_aliases = defaultdict(list)
if os.path.exists(firm_aliases_path):
    ali_df = pd.read_csv(firm_aliases_path)
    for _, r in ali_df.iterrows():
        cik_ = str(r.get("cik", "")).strip()
        alias_raw = str(r.get("alias", "")).strip()
        alias_clean = re.sub(r"[^\w\s]", "", alias_raw.lower())
        if alias_clean:
            firm_aliases[cik_].append(alias_clean)


def write_progress(status: str, **payload) -> None:
    report = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "min_year": min_year,
        "max_year": args.max_year,
        "data_root": data_root,
        "keywords_path": args.keywords_path,
        "output_counts_path": output_counts_path,
        "output_examples_path": output_examples_path,
        "output_diag_path": diag_path,
        "timing_field": args.timing_field,
    }
    report.update(payload)
    with open(progress_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
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
        terms = []
        if base:
            terms.append((base, "name_exact"))
        for alias in aliases.get(cik, []):
            alias_norm = normalize_org_name(alias)
            if alias_norm:
                terms.append((alias_norm, "alias_exact"))
        seen = set()
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
    chunks_scanned = 0
    for chunk in pd.read_csv(
        path,
        sep="\t",
        usecols=["patent_id", "disambig_assignee_organization"],
        dtype={"patent_id": str},
        chunksize=chunk_size,
    ):
        chunks_scanned += 1
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
        if chunks_scanned % 10 == 0:
            matched_rows = sum(len(block) for block in matched_blocks)
            write_progress(
                "matching_assignees",
                assignee_chunks_scanned=chunks_scanned,
                assignee_matches_accumulated=matched_rows,
            )

    if not matched_blocks:
        return pd.DataFrame(
            columns=["patent_id", "cik", "name", "match_rule", "match_term", "matched_org"]
        )
    return pd.concat(matched_blocks, ignore_index=True).drop_duplicates(
        subset=["patent_id", "cik"]
    )

write_progress("starting")

term_index = build_term_index(firm_df, firm_aliases)
write_progress("term_index_ready", normalized_company_terms=len(term_index))
print(f"🔍 Streaming assignee matches against {len(term_index)} normalized company terms...")
matched_df = stream_assignee_matches(assignee_path, term_index, args.assignee_chunksize)
matched_firms = matched_df["cik"].nunique() if not matched_df.empty else 0
write_progress(
    "assignee_matching_complete",
    firms_matched=int(matched_firms),
    patent_rows_matched=int(len(matched_df)),
)
print(f"[✓] Firms matched: {matched_firms} | Firms unmatched: {len(firm_df) - matched_firms}")
print(f"[✓] Patent rows matched (pre-merge): {len(matched_df)}")

PATENT_COLUMNS = ["patent_id", "patent_date", "patent_title"]
ABSTRACT_COLUMNS = ["patent_id", "patent_abstract"]


def load_filtered_patent_rows(path: str, cols: list[str], patent_ids: set[str]) -> pd.DataFrame:
    result = []
    if not patent_ids:
        return pd.DataFrame(columns=cols)
    chunks_scanned = 0
    for chunk in pd.read_csv(
        path,
        sep="\t",
        usecols=cols,
        dtype={"patent_id": str},
        chunksize=args.patent_chunksize,
    ):
        chunks_scanned += 1
        mask = chunk["patent_id"].isin(patent_ids)
        chunk = chunk.loc[mask]
        if not chunk.empty:
            result.append(chunk)
        if chunks_scanned % 10 == 0:
            matched_rows = sum(len(block) for block in result)
            write_progress(
                "loading_patent_rows",
                loading_path=os.path.basename(path),
                patent_chunks_scanned=chunks_scanned,
                filtered_rows_accumulated=matched_rows,
            )
    if not result:
        return pd.DataFrame(columns=cols)
    return pd.concat(result, ignore_index=True)


patent_ids = set(matched_df["patent_id"].dropna())

if matched_df.empty:
    print("[!] No firm matches found. Writing empty patent outputs.")
    pd.DataFrame(
        columns=["cik", "name", "year", "patents_total", "patents_ai", "ai_share"]
    ).to_csv(output_counts_path, index=False)
    pd.DataFrame(
        columns=["cik", "name", "year", "patent_id", "patent_title", "patent_abstract"]
    ).to_csv(output_examples_path, index=False)
    pd.DataFrame(columns=["cik", "name", "patents_total", "patents_ai"]).to_csv(
        diag_path, index=False
    )
    write_progress("completed_empty", firms_matched=0, patent_rows_matched=0)
    raise SystemExit(0)

print("📄 Loading filtered patent and abstract data...")
patents = load_filtered_patent_rows(patent_path, PATENT_COLUMNS, patent_ids)
abstracts = load_filtered_patent_rows(abstract_path, ABSTRACT_COLUMNS, patent_ids)
filing_dates = {}
if args.timing_field == "application":
    filing_dates = load_application_filing_date_lookup(
        application_path,
        patent_ids,
        chunksize=args.application_chunksize,
    )
write_progress(
    "patent_rows_loaded",
    patent_rows=int(len(patents)),
    abstract_rows=int(len(abstracts)),
    application_rows=int(len(filing_dates)),
)

df = matched_df.merge(patents, on="patent_id", how="inner")
df = df.merge(abstracts, on="patent_id", how="left")
df = attach_patent_timing(
    df,
    timing_field=args.timing_field,
    filing_date_lookup=filing_dates or None,
)
df.dropna(subset=["patent_title", "timing_date"], inplace=True)

df["text"] = (df["patent_title"].fillna("") + " " + df["patent_abstract"].fillna("")).str.lower()
df["year"] = pd.to_datetime(df["timing_date"], errors="coerce").dt.year
df = df[df["year"].notnull()]
df["year"] = df["year"].astype(int)

# Filter to requested year range
df = df[df["year"] >= min_year].copy()
if args.max_year is not None:
    df = df[df["year"] <= args.max_year].copy()
df["patent_dt"] = pd.to_datetime(df["timing_date"], errors="coerce")

keywords = load_keywords(args.keywords_path)
pattern = compile_boundary_pattern(keywords)
write_progress("keywords_loaded", keyword_count=len(keywords))

# Tag AI patents
df["matched_keywords"] = df["text"].apply(
    lambda value: matched_keywords(value, pattern)
)
df["has_ai"] = df["matched_keywords"] != ""
write_progress(
    "keyword_tagging_complete",
    candidate_patent_rows=int(len(df)),
    ai_patent_rows=int(df["has_ai"].sum()),
)

# Aggregate totals and AI counts per firm-year
print("📊 Aggregating patent counts per firm-year...")
totals = df.groupby(["cik", "name", "year"]).size().reset_index(name="patents_total")
ai_only = df[df["has_ai"]].groupby(["cik", "name", "year"]).size().reset_index(name="patents_ai")
agg = totals.merge(ai_only, on=["cik", "name", "year"], how="left").fillna({"patents_ai": 0})
agg["ai_share"] = agg["patents_ai"] / agg["patents_total"].replace(0, pd.NA)

# Save counts with the min-year suffix
agg.to_csv(output_counts_path, index=False)
print(f"[✓] Saved patent totals + AI counts to {output_counts_path}")

# Select one example AI patent per (cik, name, year): choose the most recent
df_ai = df[df["has_ai"]].copy()
if not df_ai.empty:
    examples = (
        df_ai.sort_values(["cik", "name", "year", "patent_dt"])
        .groupby(["cik", "name", "year"], as_index=False)
        .tail(1)
    )
    examples_out = examples[
        [
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
    ].drop_duplicates()
    examples_out.to_csv(output_examples_path, index=False)
    print(f"[✓] Saved example titles/abstracts to {output_examples_path}")
else:
    print("[!] No AI patents found after filtering; no examples file written.")

# === Diagnostics report ===
firm_diag = agg.groupby(["cik", "name"], as_index=False).agg(
    patents_total=("patents_total", "sum"), patents_ai=("patents_ai", "sum")
)
firm_diag["ai_share_overall"] = firm_diag["patents_ai"] / firm_diag["patents_total"].replace(
    0, pd.NA
)

# Add simple match coverage info
coverage = (
    matched_df.groupby(["cik", "name"], as_index=False)
    .size()
    .rename(columns={"size": "matched_patent_rows_premerge"})
)
firm_diag = firm_diag.merge(coverage, on=["cik", "name"], how="left")

firm_diag.to_csv(diag_path, index=False)
print(f"[✓] Wrote diagnostics to {diag_path}")

# Console summary
n_firms_any = (firm_diag["patents_total"] > 0).sum()
n_firms_ai = (firm_diag["patents_ai"] > 0).sum()
print(f"📌 Firms with ≥1 patent since {min_year}: {n_firms_any}")
print(f"📌 Firms with ≥1 AI patent since {min_year}: {n_firms_ai}")
top_ai = firm_diag.sort_values("patents_ai", ascending=False).head(10)
if not top_ai.empty:
    print("🏆 Top firms by AI patents:")
    for _, r in top_ai.iterrows():
        print(
            f"   - {r['name']} (cik={r['cik']}): AI {int(r['patents_ai'])} / Total {int(r['patents_total'])}"
        )

write_progress(
    "completed",
    firm_year_rows=int(len(agg)),
    firms_with_any_patents=int(n_firms_any),
    firms_with_ai_patents=int(n_firms_ai),
    examples_rows=int(len(examples_out)) if "examples_out" in locals() else 0,
)
