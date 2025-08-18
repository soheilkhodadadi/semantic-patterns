"""
Batch classifier for AI-related sentences using SentenceBERT and cosine similarity.

This script searches for *_ai_sentences.txt files under data/processed/sec (including
year subfolders like 2021/, 2022/ ...), classifies each sentence using the classify_sentence() function,
and writes results to sibling *_classified.txt files.

Usage examples:
  # Scan everything recursively under the default base dir
  python src/classification/classify_all_ai_sentences.py

  # Only scan specific years and cap work for a quick check
  python src/classification/classify_all_ai_sentences.py --years 2021 2022 --limit 10

  # Recompute even if *_classified.txt exists
  python src/classification/classify_all_ai_sentences.py --force

  # Rebuild only files older than centroids (default)
  python src/classification/classify_all_ai_sentences.py --years 2024

  # Force rebuild of everything regardless of timestamps
  python src/classification/classify_all_ai_sentences.py --years 2024 --force
"""

import os
import sys
import argparse
from typing import List, Optional

# Ensure we can import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classify import classify_sentence, CENTROIDS_PATH  # noqa: E402


def find_ai_sentence_files(base_dir: str, years: Optional[List[str]] = None, limit: int = 0) -> List[str]:
    """
    Find all *_ai_sentences.txt files under base_dir.
    If years are provided (e.g., ["2021","2022"]), only search those subfolders.
    """
    candidates: List[str] = []

    if years:
        for y in years:
            year_dir = os.path.join(base_dir, y)
            if not os.path.isdir(year_dir):
                continue
            for name in os.listdir(year_dir):
                if name.endswith("_ai_sentences.txt"):
                    candidates.append(os.path.join(year_dir, name))
    else:
        # Recurse
        for root, _dirs, files in os.walk(base_dir):
            for name in files:
                if name.endswith("_ai_sentences.txt"):
                    candidates.append(os.path.join(root, name))

    # Stable sort for reproducibility
    candidates.sort()
    if limit and len(candidates) > limit:
        candidates = candidates[:limit]
    return candidates


def classify_file(input_path: str, force: bool = False) -> str:
    """
    Classify the sentences in a single *_ai_sentences.txt file.

    Returns the output path for the written *_classified.txt file (or existing one if skipped).
    """
    output_path = input_path.replace("_ai_sentences.txt", "_classified.txt")

    # Skip if already classified and not forcing
    if not force and os.path.exists(output_path):
        return output_path

    # Read sentences
    with open(input_path, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    outputs = []
    for sent in sentences:
        try:
            label, scores = classify_sentence(sent)
            outputs.append(f"{sent} | Label: {label} | Scores: {scores}")
        except Exception as e:
            # Keep going even if one sentence fails
            outputs.append(f"{sent} | Label: ERROR | Scores: {{}} | Error: {e}")

    # Write results next to the input
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(outputs))

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Batch classify AI sentences across filings.")
    parser.add_argument("--base-dir", default="data/processed/sec", help="Root dir containing filings.")
    parser.add_argument(
        "--years", nargs="*", default=None, help="Optional list of year folders to scan (e.g., 2021 2022 2023 2024)."
    )
    parser.add_argument("--limit", type=int, default=0, help="Max files to process (0 = no limit).")
    parser.add_argument("--force", action="store_true", help="Recompute even if *_classified.txt exists.")
    parser.add_argument(
        "--refresh-if-centroids-newer",
        action="store_true",
        default=True,
        help="Rebuild outputs if centroids file is newer than existing *_classified.txt (default: on)",
    )
    parser.add_argument(
        "--no-refresh-if-centroids-newer",
        dest="refresh_if_centroids_newer",
        action="store_false",
        help="Disable timestamp-based refresh logic",
    )
    args = parser.parse_args()

    refresh_if_centroids_newer = args.refresh_if_centroids_newer

    base_dir = args.base_dir
    years = args.years
    limit = args.limit
    force = args.force

    try:
        centroids_mtime = os.path.getmtime(CENTROIDS_PATH)
    except Exception:
        centroids_mtime = None

    if not os.path.isdir(base_dir):
        print(f"❌ Base directory not found: {base_dir}")
        sys.exit(1)

    files = find_ai_sentence_files(base_dir, years, limit)
    print(f"[✓] Found {len(files)} AI sentence files under {base_dir}" + (f" for years {years}" if years else ""))

    processed = 0
    skipped = 0
    for i, inp in enumerate(files, 1):
        outp = inp.replace("_ai_sentences.txt", "_classified.txt")
        # Decide whether to skip or rebuild
        if os.path.exists(outp) and not force:
            # If centroids are newer than the existing output, rebuild (unless disabled)
            if refresh_if_centroids_newer and centroids_mtime is not None:
                try:
                    out_mtime = os.path.getmtime(outp)
                except Exception:
                    out_mtime = -1
                if out_mtime < centroids_mtime:
                    print(f"♻️  {i:>4}/{len(files)} Rebuild (centroids newer): {os.path.relpath(outp)}")
                else:
                    skipped += 1
                    print(f"⏭️  {i:>4}/{len(files)} Skip (up-to-date): {os.path.relpath(outp)}")
                    continue
            else:
                skipped += 1
                print(f"⏭️  {i:>4}/{len(files)} Skip (exists): {os.path.relpath(outp)}")
                continue

        print(f"🔍 {i:>4}/{len(files)} Classifying → {os.path.relpath(outp)}")
        classify_file(inp, force=True if force else False)
        processed += 1

    print("\n—— Summary ————————————————")
    print(f"Processed (new/updated): {processed}")
    print(f"Skipped (already existed): {skipped}")
    print(f"Base dir: {base_dir}")
    if years:
        print(f"Years: {', '.join(years)}")


if __name__ == "__main__":
    main()