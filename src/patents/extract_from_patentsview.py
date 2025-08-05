
""" 
Extracts AI-related patent counts by firm and year using real PatentsView data.

Inputs:
- patent.tsv: contains patent_id, patent_date, patent_title
- patent_abstract.tsv: contains patent_id, abstract
- patent_assignee.tsv: contains patent_id, assignee_organization
- company_lookup.csv: cleaned CIK ↔ firm name mapping
- patent_keywords.txt: AI-related keyword list

Run:
    python src/patents/extract_from_patentsview.py
"""

import pandas as pd
import os
import re
from tqdm import tqdm

# File paths
base_path = "data/raw/patents/patentsview"
patent_file = os.path.join(base_path, "patent.tsv")
abstract_file = os.path.join(base_path, "patent_abstract.tsv")
assignee_file = os.path.join(base_path, "patent_assignee.tsv")

# Output file
output_path = "data/processed/patents/ai_patent_counts.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Load data
print("🔍 Loading data...")
patents = pd.read_csv(patent_file, sep="\t", usecols=["patent_id", "patent_date", "patent_title"])
abstracts = pd.read_csv(abstract_file, sep="\t", usecols=["patent_id", "abstract"])
assignees = pd.read_csv(assignee_file, sep="\t", usecols=["patent_id", "assignee_organization"])

# Merge all data into one table
df = patents.merge(abstracts, on="patent_id", how="left")
df = df.merge(assignees, on="patent_id", how="left")

df.dropna(subset=["assignee_organization", "patent_date"], inplace=True)

# Normalize fields
df["text"] = (df["patent_title"].fillna("") + " " + df["abstract"].fillna("")).str.lower()
df["assignee_clean"] = df["assignee_organization"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
df["year"] = pd.to_datetime(df["patent_date"], errors="coerce").dt.year
df = df[df["year"].notnull()]
df["year"] = df["year"].astype(int)

# Load AI keyword list
with open("data/metadata/patent_keywords.txt") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]
keyword_pattern = re.compile("|".join([re.escape(k) for k in keywords]), flags=re.IGNORECASE)

# Load company lookup
firm_df = pd.read_csv("data/metadata/company_lookup.csv")
firm_df["name_clean"] = firm_df["name_clean"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

# Aggregate AI patent counts by firm-year
results = []
print("📊 Counting patents...")
for _, firm in tqdm(firm_df.iterrows(), total=len(firm_df)):
    cik = firm["cik"]
    firm_name = firm["name_clean"]

    # Fuzzy match assignee org
    firm_patents = df[df["assignee_clean"].str.contains(firm_name, na=False)].copy()
    firm_patents["has_ai"] = firm_patents["text"].apply(lambda x: bool(keyword_pattern.search(x)))

    grouped = (
        firm_patents[firm_patents["has_ai"]]
        .groupby("year")
        .size()
        .reset_index(name="ai_patent_count")
    )

    for _, row in grouped.iterrows():
        results.append({
            "cik": cik,
            "company_name": firm["company_name"],
            "year": int(row["year"]),
            "ai_patent_count": int(row["ai_patent_count"])
        })

# Save result
pd.DataFrame(results).to_csv(output_path, index=False)
print(f"[✓] Saved: {output_path}")
