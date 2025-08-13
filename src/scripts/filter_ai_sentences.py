"""
Filter AI-related sentences from EDGAR filings.

This script walks a base directory (default: data/processed/sec) that contains
year subfolders (e.g., 2021, 2022, 2023, 2024) and extracts AI-related
sentences into sibling files named *_ai_sentences.txt.

It uses core/sentence_filter.py for:
  - segment_sentences()
  - load_keywords()
  - filter_ai_sentences()

Features
--------
- **Scans only year folders** (YYYY) under the base directory; root-level files are ignored
- Skips already processed outputs unless --force is provided
- Skips derived/non-filing outputs (e.g., *_ai_sentences.txt, *_classified.txt, *_scored*.txt)
- Optional form filtering (e.g., only 10-K)
- Optional limit to process just a few files for quick checks
- Robust file reading (UTF-8 with errors='ignore')
- Per-year and grand total summary

Usage
-----
# Default locations
python src/scripts/filter_ai_sentences.py

# Quick smoke test on 2 filings, only 10-K
python src/scripts/filter_ai_sentences.py --include-forms 10-K --limit 2

# Explicit paths and overwrite
python src/scripts/filter_ai_sentences.py \
  --base-dir data/processed/sec \
  --keywords data/metadata/ai_keywords.txt \
  --force
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Iterator, Tuple, Optional, Set

# Ensure `src/` is on sys.path so we can import core.sentence_filter reliably
THIS_DIR = os.path.dirname(__file__)
SRC_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if SRC_ROOT not in sys.path:
    sys.path.append(SRC_ROOT)

from core.sentence_filter import segment_sentences, load_keywords, filter_ai_sentences  # noqa: E402


DERIVED_SUFFIXES = (
    "_ai_sentences.txt",
    "_classified.txt",
    "_scored.txt",
    "_scored_ai_sentences.txt",
)


def looks_like_year(name: str) -> bool:
    return name.isdigit() and len(name) == 4


def parse_form_from_filename(filename: str) -> Optional[str]:
    """Best-effort extract of form code from EDGAR filename.
    Expected pattern like: YYYYMMDD_10-K_edgar_data_...
    Returns the token between the first and second underscores if it contains a dash or letters/digits.
    """
    base = os.path.basename(filename)
    parts = base.split("_")
    if len(parts) >= 2:
        candidate = parts[1]
        # Basic sanity: typical forms contain a dash or are alnum like 10-K / 10-Q
        if any(c.isalpha() for c in candidate) or "-" in candidate:
            return candidate
    return None


def iter_filings(base_dir: str, include_forms: Optional[Set[str]]) -> Iterator[str]:
    """
    Yield absolute paths to .txt filing files under base_dir **only inside year subfolders**,
    skipping derived outputs and (optionally) non-matching forms.

    Parameters
    ----------
    base_dir : str
        Root directory containing filing .txt files with year subfolders.
    include_forms : Optional[Set[str]]
        If provided, only files whose parsed form is in this set will be yielded.
    """
    for year in sorted(os.listdir(base_dir)):
        year_path = os.path.join(base_dir, year)
        if not os.path.isdir(year_path) or not looks_like_year(year):
            # Ignore root-level files and non-year folders
            continue
        for root, _, files in os.walk(year_path):
            for fn in files:
                if not fn.endswith(".txt"):
                    continue
                # Skip derived outputs in any folder
                if any(fn.endswith(suf) or suf in fn for suf in DERIVED_SUFFIXES):
                    continue
                fpath = os.path.join(root, fn)
                if include_forms:
                    form = parse_form_from_filename(fn)
                    if (form is None) or (form not in include_forms):
                        continue
                yield fpath


def process_file(path: str, keywords, force: bool) -> Tuple[str, int, str]:
    """
    Process a single filing file: segment sentences, filter by AI keywords, write output.

    Returns
    -------
    (status, count, out_path) : Tuple[str, int, str]
        status in {"ok", "skipped_exists", "empty"}
        count  = number of AI sentences written
        out_path = output filepath
    """
    out_path = path[:-4] + "_ai_sentences.txt"
    if (not force) and os.path.exists(out_path):
        return "skipped_exists", 0, out_path

    # Defensive read: some EDGAR text can contain odd encodings / control chars
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        # Touch an empty output to mark it processed
        open(out_path, "w", encoding="utf-8").close()
        return "empty", 0, out_path

    sentences = segment_sentences(text)
    ai_sents = filter_ai_sentences(sentences, keywords)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ai_sents))

    return "ok", len(ai_sents), out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract AI-related sentences from filings.")
    ap.add_argument(
        "--base-dir",
        default="data/processed/sec",
        help="Root directory containing filing .txt files (nested by year).",
    )
    ap.add_argument(
        "--keywords",
        default="data/metadata/ai_keywords.txt",
        help="Path to keyword list (one term/phrase per line).",
    )
    ap.add_argument(
        "--include-forms",
        default="10-K",
        help="Comma-separated list of form codes to include (default: 10-K). Use 'ALL' for no filter.",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process at most N filings (0 = no limit). Useful for quick checks.",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing *_ai_sentences.txt outputs.",
    )
    ap.add_argument(
        "--file",
        default=None,
        help="Path to a single filing file to process (overrides directory scanning).",
    )
    args = ap.parse_args()

    if args.file:
        if not os.path.isfile(args.file):
            raise FileNotFoundError(f"Specified file not found: {args.file}")
        keywords = load_keywords(args.keywords)
        status, count, out_path = process_file(args.file, keywords, args.force)
        if status == "ok":
            print(f"✓ {out_path}  ({count} AI sentences)")
        elif status == "skipped_exists":
            print(f"Skipped existing output: {out_path}")
        else:
            print(f"Empty filing: {args.file}")
        return

    if not os.path.isdir(args.base_dir):
        raise FileNotFoundError(f"Base directory not found: {args.base_dir}")

    keywords = load_keywords(args.keywords)

    include_forms: Optional[Set[str]]
    if args.include_forms.strip().upper() == "ALL":
        include_forms = None
    else:
        include_forms = {tok.strip() for tok in args.include_forms.split(",") if tok.strip()}

    totals = {"seen": 0, "wrote": 0, "skipped": 0, "empty": 0}
    per_year: Dict[str, int] = {}

    print(f"[i] Walking filings under: {args.base_dir}")
    print(f"[i] Using keywords from :  {args.keywords}")
    if include_forms is None:
        print("[i] Form filter       :  ALL")
    else:
        print(f"[i] Form filter       :  {sorted(include_forms)}")
    if args.limit:
        print(f"[i] Limit             :  {args.limit} filings")

    processed = 0
    for path in iter_filings(args.base_dir, include_forms):
        # Stop early if limit is set
        if args.limit and processed >= args.limit:
            break

        # Expect layout .../sec/<YEAR>/<file>.txt
        year = os.path.basename(os.path.dirname(path))
        per_year[year] = per_year.get(year, 0) + 1
        totals["seen"] += 1

        status, count, out_path = process_file(path, keywords, args.force)
        if status == "ok":
            totals["wrote"] += 1
            processed += 1
            print(f"✓ {out_path}  ({count} AI sentences)")
        elif status == "skipped_exists":
            totals["skipped"] += 1
        else:
            totals["empty"] += 1

    # Summary
    print("\n—— Summary ————————————————")
    print(f"Filings scanned   : {totals['seen']}")
    print(f"Wrote new outputs : {totals['wrote']}")
    print(f"Skipped (exists)  : {totals['skipped']}")
    print(f"Empty filings     : {totals['empty']}")
    if per_year:
        print("Per-year scanned:")
        for y in sorted(per_year):
            print(f"  {y}: {per_year[y]}")
    print("\nTip: Press Ctrl+C to stop mid-run. Use --limit for quick checks.")


if __name__ == "__main__":
    main()
