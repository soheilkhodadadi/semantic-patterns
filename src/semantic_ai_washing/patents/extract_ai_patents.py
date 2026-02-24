"""Extracts AI-related patents by matching keywords and company names from local patent data.

Assumes a CSV with columns like: assignee, title, abstract, year

Run: python src/patents/extract_ai_patents.py
"""

import pandas as pd
import os

# Load company info
company_df = pd.read_csv("data/metadata/company_lookup.csv")
company_names = company_df["name_clean"].tolist()
cik_lookup = dict(zip(company_df["name_clean"], company_df["cik"]))

# Load keywords
with open("data/metadata/patent_keywords.txt") as f:
    keywords = [line.strip().lower() for line in f if line.strip()]

# Load patent dataset
# Replace this path with your actual patent CSV sample
patent_df = pd.read_csv("data/raw/patents/sample_patents.csv")

# Normalize text columns
patent_df["combined_text"] = (patent_df["title"].fillna("") + " " + patent_df["abstract"].fillna("")).str.lower()

# Normalize assignee
patent_df["assignee_clean"] = patent_df["assignee"].str.lower().str.replace(r"[^\w\s]", "", regex=True)

# Search and count per firm-year
results = []
for name in company_names:
    firm_patents = patent_df[patent_df["assignee_clean"].str.contains(name, na=False)]
    for year in range(2019, 2024):
        yearly = firm_patents[firm_patents["year"] == year]
        matches = yearly[yearly["combined_text"].apply(lambda x: any(kw in x for kw in keywords))]
        count = len(matches)
        results.append({
            "cik": cik_lookup.get(name),
            "company_name": name,
            "year": year,
            "ai_patent_count": count
        })

# Save output
out_path = "data/processed/patents/ai_patent_counts.csv"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pd.DataFrame(results).to_csv(out_path, index=False)
print(f"[✓] Saved firm-year AI patent counts to: {out_path}")