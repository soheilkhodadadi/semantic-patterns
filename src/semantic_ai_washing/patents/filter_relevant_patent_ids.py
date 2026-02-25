"""
Filters patent_assignee.tsv to extract patent_ids linked to your companies of interest.
Matches are based on fuzzy lowercase name matching from your company_lookup.csv.

Output:
- data/processed/patents/filtered_patent_ids.csv

Run:
    python src/patents/filter_relevant_patent_ids.py
"""

import pandas as pd
import os

# Load company lookup table
firms = pd.read_csv("data/metadata/company_lookup.csv")
firms["name_clean"] = firms["name_clean"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

# Load patent_assignee.tsv
assignee_path = "data/raw/patents/patentsview/patent_assignee.tsv"
df = pd.read_csv(assignee_path, sep="\t", usecols=["patent_id", "assignee_organization"])
df.dropna(subset=["assignee_organization"], inplace=True)
df["assignee_clean"] = (
    df["assignee_organization"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
)

# Match each firm to assignees
matched_ids = []
for _, firm in firms.iterrows():
    firm_name = firm["name_clean"]
    matches = df[df["assignee_clean"].str.contains(firm_name, na=False)]
    matched_ids.extend(matches["patent_id"].tolist())

# Deduplicate and save
matched_ids = list(set(matched_ids))
out_path = "data/processed/patents/filtered_patent_ids.csv"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

pd.DataFrame({"patent_id": matched_ids}).to_csv(out_path, index=False)
print(f"[✓] Saved {len(matched_ids)} filtered patent_ids to: {out_path}")
