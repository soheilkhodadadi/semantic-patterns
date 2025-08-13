
""" 
Extracts AI-related patent counts per firm-year using disambiguated assignee names from PatentsView data.

Steps:
- Load `patent_assignee.tsv` and match `disambig_assignee_organization` to known firms
- Use matching patent_ids to pull from `patent.tsv` and `patent_abstract.tsv`
- Filter for AI keywords in title + abstract
- Aggregate AI patent counts per firm-year

Run:
    python src/patents/extract_filtered_patents.py
"""

import pandas as pd
import os
import re
from tqdm import tqdm

# Updated file location
data_root = "/Users/soheilkhodadadi/DataWork/patentsview"

assignee_path = os.path.join(data_root, "patent_assignee.tsv")
patent_path = os.path.join(data_root, "patent.tsv")
abstract_path = os.path.join(data_root, "patent_abstract.tsv")

# Output
output_path = "data/processed/patents/ai_patent_counts_filtered.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load company lookup
firm_df = pd.read_csv("data/metadata/company_lookup.csv")
firm_df["name_clean"] = firm_df["name_clean"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

# Load assignee file and normalize
print("🔍 Loading assignee data...")
assignees = pd.read_csv(assignee_path, sep="\t", usecols=["patent_id", "disambig_assignee_organization"])
assignees.dropna(subset=["disambig_assignee_organization"], inplace=True)
assignees["org_clean"] = assignees["disambig_assignee_organization"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

print("🔍 Matching firms to assignees...")
matched_patents = []
matched_rows = []

for _, firm in firm_df.iterrows():
    firm_name_clean = firm["name_clean"]
    cik = firm["cik"]
    name = firm["name"]

    subset = assignees[assignees["org_clean"].str.contains(firm_name_clean, na=False)].copy()
    subset["cik"] = cik
    subset["name"] = name
    matched_patents.extend(subset["patent_id"].tolist())
    matched_rows.append(subset)

matched_df = pd.concat(matched_rows).drop_duplicates(subset=["patent_id", "cik"])
print(f"[✓] Matched {len(matched_df)} patent IDs to firms.")

# Load patent and abstract data
print("📄 Loading patent metadata...")
patents = pd.read_csv(patent_path, sep="\t", usecols=["patent_id", "patent_date", "patent_title"])
abstracts = pd.read_csv(abstract_path, sep="\t", usecols=["patent_id", "patent_abstract"])

# Merge all together
df = matched_df.merge(patents, on="patent_id", how="left")
df = df.merge(abstracts, on="patent_id", how="left")
df.dropna(subset=["patent_title", "patent_date"], inplace=True)

df["text"] = (df["patent_title"].fillna("") + " " + df["patent_abstract"].fillna("")).str.lower()
df["year"] = pd.to_datetime(df["patent_date"], errors="coerce").dt.year
df = df[df["year"].notnull()]
df["year"] = df["year"].astype(int)

# Load AI keywords
with open("data/metadata/patent_keywords.txt") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]
pattern = re.compile("|".join([re.escape(k) for k in keywords]), flags=re.IGNORECASE)

# Tag AI patents
df["has_ai"] = df["text"].apply(lambda x: bool(pattern.search(x)))

# Aggregate firm-year counts
print("📊 Aggregating AI patent counts per firm-year...")
agg = (
    df[df["has_ai"]]
    .groupby(["cik", "name", "year"])
    .size()
    .reset_index(name="ai_patent_count")
)

agg.to_csv(output_path, index=False)
print(f"[✓] Saved result to {output_path}")
