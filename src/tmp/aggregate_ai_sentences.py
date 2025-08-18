# File: src/tmp/aggregate_ai_sentences.py

import os
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


# Only scan classified files under specific year subfolders
INPUT_ROOT = "data/processed/sec"
YEARS = ["2021", "2022", "2023", "2024"]
OUTPUT_FILE = "data/validation/collected_ai_sentences_classified.txt"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

collected_sentences = []
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
                if line:
                    collected_sentences.append(line)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(collected_sentences))

print(f"[✓] Years scanned: {', '.join(YEARS)}")
print(f"[✓] Files read: {files_read}")
print(f"[✓] Sentences collected: {len(collected_sentences)}")
print(f"[✓] Output written to: {OUTPUT_FILE}")