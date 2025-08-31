# File: src/tmp/aggregate_ai_sentences.py

import os
import csv
from glob import glob
input_dir = "data/processed/sec"  # where *_ai_sentences.txt are located
output_file = "data/validation/collected_ai_sentences.txt"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Collect all *_ai_sentences.txt files
collected_sentences = []
for filename in os.listdir(input_dir):
    if filename.endswith("_ai_sentences.txt"):
        with open(os.path.join(input_dir, filename), "r", encoding="utf-8") as f:
            collected_sentences.extend([line.strip() for line in f if line.strip()])

# Save to a single file
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(collected_sentences))

print(f"[✓] Collected {len(collected_sentences)} AI-related sentences into {output_file}")


# --- replace your existing classified OUTPUT_FILE vars with these ---


# --- Aggregate classified CSVs across the entire SEC folder ---
# Goal: read every *_classified.csv under data/processed/sec/** and
# write a single held-out style CSV with two columns: sentence,label

CLASSIFIED_ROOT = "data/processed/sec"
AGG_OUTPUT_CSV = "data/validation/CollectedAiSentencesClassified.csv"

os.makedirs(os.path.dirname(AGG_OUTPUT_CSV), exist_ok=True)

# Find every classified CSV recursively (no year restriction)
classified_paths = sorted(glob(os.path.join(CLASSIFIED_ROOT, "**", "*_classified.csv"), recursive=True))

rows = []          # aggregated rows with keys: sentence, label
files_read = 0
skipped_files = 0

for path in classified_paths:
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                skipped_files += 1
                continue
            # Determine sentence and label columns from common variants
            fns = {name.strip().lower(): name for name in reader.fieldnames}
            sentence_col = fns.get("sentence") or fns.get("sent_text")
            label_col = fns.get("label") or fns.get("label_pred")
            if not sentence_col or not label_col:
                # cannot interpret this file format
                skipped_files += 1
                continue

            files_read += 1
            for row in reader:
                sent = (row.get(sentence_col) or "").strip()
                lab = (row.get(label_col) or "").strip()
                if not sent:
                    continue
                # Skip error placeholders if present
                if lab.upper() == "ERROR" or lab == "":
                    continue
                rows.append({"sentence": sent, "label": lab})
    except Exception:
        skipped_files += 1
        continue

# Optional: deduplicate while preserving order
seen = set()
unique_rows = []
for r in rows:
    key = (r["sentence"], r["label"])
    if key in seen:
        continue
    seen.add(key)
    unique_rows.append(r)

with open(AGG_OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["sentence", "label"])
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"[✓] Classified CSV files scanned: {len(classified_paths)} (read={files_read}, skipped={skipped_files})")
print(f"[✓] Aggregated rows (unique): {len(unique_rows)}")
print(f"[✓] Output written to: {AGG_OUTPUT_CSV}")