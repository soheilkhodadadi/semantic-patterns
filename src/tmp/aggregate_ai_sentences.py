# File: src/tmp/aggregate_ai_sentences.py

import os
from glob import glob
import csv
import re
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
# Only scan classified files under specific year subfolders
INPUT_ROOT = "data/processed/sec"
YEARS = ["2021", "2022", "2023", "2024"]
OUTPUT_TXT = "data/validation/collected_ai_sentences_classified.txt"
OUTPUT_CSV = "data/validation/collected_ai_sentences_classified.csv"  # held-out style: sentence,label

os.makedirs(os.path.dirname(OUTPUT_TXT), exist_ok=True)

# Helper: parse a classified line into (label, sentence)
LABELS = {"Actionable", "Speculative", "Irrelevant"}
label_prefix_re = re.compile(r"^\s*(Actionable|Speculative|Irrelevant)\s*[:\-\t]\s*(.*)$", re.IGNORECASE)

def parse_labeled_line(line: str):
    # Try TAB-delimited: LABEL\tSENTENCE
    parts = line.split("\t", 1)
    if len(parts) == 2 and parts[0].strip():
        lab = parts[0].strip().capitalize()
        sent = parts[1].strip()
        if lab in LABELS:
            return lab, sent
    # Try prefix like "Actionable: ..." or "Speculative - ..."
    m = label_prefix_re.match(line)
    if m:
        lab = m.group(1).capitalize()
        sent = m.group(2).strip()
        return lab, sent
    # Fallback: unknown format → empty label, full line as sentence
    return "", line.strip()

# Collect classified lines and also build CSV rows
collected_sentences = []  # plain text for TXT (preserve current behavior)
rows = []                 # list of {"sentence": ..., "label": ...}
files_read = 0

for year in YEARS:
    year_dir = os.path.join(INPUT_ROOT, year)
    if not os.path.isdir(year_dir):
        print(f"[!] Missing year directory: {year_dir} — skipping")
        continue

    pattern = os.path.join(year_dir, "**", "*_classified.txt")
    for path in sorted(glob(pattern, recursive=True)):
        files_read += 1
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                collected_sentences.append(line)
                label, sentence = parse_labeled_line(line)
                rows.append({"sentence": sentence, "label": label})

# Write TXT (unchanged behavior)
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(collected_sentences))

# Write CSV in held-out format: sentence,label
with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["sentence", "label"])
    writer.writeheader()
    writer.writerows(rows)

print(f"[✓] Years scanned: {', '.join(YEARS)}")
print(f"[✓] Files read: {files_read}")
print(f"[✓] Sentences collected: {len(collected_sentences)}")
print(f"[✓] Output written to: {OUTPUT_TXT}")
print(f"[✓] CSV written to: {OUTPUT_CSV}")