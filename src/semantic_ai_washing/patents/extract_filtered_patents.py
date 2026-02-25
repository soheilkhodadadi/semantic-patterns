"""
Extracts AI-related patent counts per firm-year using disambiguated assignee names from PatentsView data.

Steps:
- Load `patent_assignee.tsv` and match `disambig_assignee_organization` to known firms
- Use matching patent_ids to pull from `patent.tsv` and `patent_abstract.tsv`
- Filter for AI keywords in title + abstract
- Aggregate AI patent counts per firm-year

Run:
    python src/patents/extract_filtered_patents.py --min-year 2019
Outputs:
    - data/processed/patents/ai_patent_counts_filtered_2019plus.csv
    - data/processed/patents/ai_patent_examples_2019plus.csv
    - data/processed/patents/patents_diagnostics_2019plus.csv
"""

import pandas as pd
import os
import re
import argparse
from collections import defaultdict, Counter

# Updated file location
data_root = "/Users/soheilkhodadadi/DataWork/patentsview"

assignee_path = os.path.join(data_root, "patent_assignee.tsv")
patent_path = os.path.join(data_root, "patent.tsv")
abstract_path = os.path.join(data_root, "patent_abstract.tsv")

# Outputs (suffix updates with --min-year)
parser = argparse.ArgumentParser(
    description="Extract AI-related patents per firm-year with example titles/abstracts."
)
parser.add_argument(
    "--min-year", type=int, default=2019, help="Minimum patent year to include (default: 2019)."
)
args = parser.parse_args()
min_year = args.min_year
suffix = f"{min_year}plus"

output_counts_path = f"data/processed/patents/ai_patent_counts_filtered_{suffix}.csv"
output_examples_path = f"data/processed/patents/ai_patent_examples_{suffix}.csv"
os.makedirs(os.path.dirname(output_counts_path), exist_ok=True)
os.makedirs(os.path.dirname(output_examples_path), exist_ok=True)

# Load company lookup
firm_df = pd.read_csv("data/metadata/company_lookup.csv")
firm_df["name_clean"] = firm_df["name_clean"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

# Optional aliases
aliases_path = "data/metadata/company_aliases.csv"
firm_aliases = defaultdict(list)
if os.path.exists(aliases_path):
    ali_df = pd.read_csv(aliases_path)
    for _, r in ali_df.iterrows():
        cik_ = str(r.get("cik", "")).strip()
        alias_raw = str(r.get("alias", "")).strip()
        alias_clean = re.sub(r"[^\w\s]", "", alias_raw.lower())
        if alias_clean:
            firm_aliases[cik_].append(alias_clean)

# Load assignee file and normalize
print("🔍 Loading assignee data...")
assignees = pd.read_csv(
    assignee_path, sep="\t", usecols=["patent_id", "disambig_assignee_organization"]
)
assignees.dropna(subset=["disambig_assignee_organization"], inplace=True)
assignees["org_clean"] = (
    assignees["disambig_assignee_organization"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
)

print("🔍 Matching firms to assignees (regex word-boundaries, aliases supported)...")
matched_blocks = []
match_stats = Counter()

for _, firm in firm_df.iterrows():
    cik = str(firm.get("cik", "")).strip()
    name = str(firm.get("name", "")).strip()
    base = str(firm.get("name_clean", "")).strip()

    # Build candidate patterns: cleaned name + any aliases
    terms = [t for t in [base] + firm_aliases.get(cik, []) if t]
    if not terms:
        continue

    firm_hits = []
    for t in terms:
        # Robust word-boundary regex; allow whitespace between tokens
        tokenized = re.escape(t).replace(r"\ ", r"\s+")
        pat = re.compile(rf"\b{tokenized}\b", flags=re.IGNORECASE)
        hit = assignees[assignees["org_clean"].str.contains(pat, na=False, regex=True)].copy()
        if not hit.empty:
            hit["match_term"] = t
            firm_hits.append(hit)

    if firm_hits:
        sub = pd.concat(firm_hits, ignore_index=True).drop_duplicates(subset=["patent_id"])
        sub["cik"] = cik
        sub["name"] = name
        sub["match_rule"] = sub["match_term"].apply(
            lambda x: "alias_regex" if x in firm_aliases.get(cik, []) else "name_regex"
        )
        matched_blocks.append(sub)
        match_stats["firms_matched"] += 1
        match_stats["patents_matched"] += len(sub)
    else:
        match_stats["firms_unmatched"] += 1

if matched_blocks:
    matched_df = pd.concat(matched_blocks, ignore_index=True).drop_duplicates(
        subset=["patent_id", "cik"]
    )
else:
    matched_df = pd.DataFrame(columns=["patent_id", "cik", "name", "match_rule"])

print(
    f"[✓] Firms matched: {match_stats.get('firms_matched', 0)} | Firms unmatched: {match_stats.get('firms_unmatched', 0)}"
)
print(f"[✓] Patent rows matched (pre-merge): {match_stats.get('patents_matched', 0)}")

# Load patent and abstract data
print("📄 Loading patent metadata...")
patents = pd.read_csv(
    patent_path,
    sep="\t",
    usecols=["patent_id", "patent_date", "patent_title"],
    dtype={"patent_id": str},
    low_memory=False,
)
abstracts = pd.read_csv(
    abstract_path,
    sep="\t",
    usecols=["patent_id", "patent_abstract"],
    dtype={"patent_id": str},
    low_memory=False,
)

# Merge all together
df = matched_df.merge(patents, on="patent_id", how="left")
df = df.merge(abstracts, on="patent_id", how="left")
df.dropna(subset=["patent_title", "patent_date"], inplace=True)

df["text"] = (df["patent_title"].fillna("") + " " + df["patent_abstract"].fillna("")).str.lower()
df["year"] = pd.to_datetime(df["patent_date"], errors="coerce").dt.year
df = df[df["year"].notnull()]
df["year"] = df["year"].astype(int)

# Filter to requested year range
df = df[df["year"] >= min_year].copy()
df["patent_dt"] = pd.to_datetime(df["patent_date"], errors="coerce")

# Load AI keywords
with open("data/metadata/patent_keywords.txt") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]
pattern = re.compile("|".join([re.escape(k) for k in keywords]), flags=re.IGNORECASE)

# Tag AI patents
df["has_ai"] = df["text"].apply(lambda x: bool(pattern.search(x)))

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
        ["cik", "name", "year", "patent_id", "patent_title", "patent_abstract"]
    ].drop_duplicates()
    examples_out.to_csv(output_examples_path, index=False)
    print(f"[✓] Saved example titles/abstracts to {output_examples_path}")
else:
    print("[!] No AI patents found after filtering; no examples file written.")

# === Diagnostics report ===
diag_path = f"data/processed/patents/patents_diagnostics_{suffix}.csv"
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
