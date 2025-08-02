import os
import math
from collections import Counter
import pandas as pd

# Path to classified sentence files
classified_dir = "data/processed/sec"

# Store aggregated results
rows = []

for filename in os.listdir(classified_dir):
    if not filename.endswith("_classified.txt"):
        continue

    path = os.path.join(classified_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        labels = [
            line.split(" | Label: ")[1].split(" |")[0]
            for line in f if " | Label: " in line
        ]
        if not labels:
            continue
        counts = Counter(labels)

    # Extract CIK and year from filename
    parts = filename.split("_")
    year = parts[0][:4]
    cik = parts[4] if len(parts) > 4 else "unknown"

    # Compute log-transformed counts
    actionable = counts.get("Actionable", 0)
    speculative = counts.get("Speculative", 0)
    irrelevant = counts.get("Irrelevant", 0)
    total = actionable + speculative + irrelevant

    row = {
        "cik": cik,
        "year": int(year),
        "AI_frequencyA": math.log(actionable + 1),
        "AI_frequencyS": math.log(speculative + 1),
        "AI_frequencyI": math.log(irrelevant + 1),
        "AI_frequency_total": math.log(total + 1)
    }
    rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(rows)
df.sort_values(by=["cik", "year"], inplace=True)

# Save
output_path = "data/final/ai_frequencies_by_firm_year.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)
print(f"[✓] Saved {len(df)} firm-year rows with total frequency to: {output_path}")
