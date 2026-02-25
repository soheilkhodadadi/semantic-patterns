"""
Filter AI-related sentences from EDGAR filings.

This script walks an input directory (default: data/processed/sec) that contains
year subfolders (e.g., 2021, 2022, 2023, 2024) and extracts AI-related
sentences into sibling files named *_ai_sentences.txt.

It uses core/sentence_filter.py for:
  - segment_sentences()
  - merge_page_fragments()
  - merge_sentence_fragments()
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
  --input-dir data/processed/sec \
  --keywords data/metadata/ai_keywords.txt \
  --force

# Only process 2023–2024 10‑K
python src/scripts/filter_ai_sentences.py --include-forms 10-K --years 2023,2024
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from typing import Dict, Iterator, Tuple, Optional, Set

from semantic_ai_washing.core.sentence_filter import (
    filter_ai_sentences,
    load_keywords,
    merge_page_fragments,
    merge_sentence_fragments,
    segment_sentences,
)


DERIVED_SUFFIXES = (
    "_ai_sentences.txt",
    "_classified.txt",
    "_scored.txt",
    "_scored_ai_sentences.txt",
)

SKIP_SUBSTRINGS = (
    "_ai_sentences.txt",
    "_classified.txt",
    "_scored.txt",
    "_scored_ai_sentences.txt",
)

SENTENCE_ENDINGS = (".", "!", "?")
PAGE_MARKER_REGEX = re.compile(r"[\-\u2013\u2014]\s*\d+\s*[\-\u2013\u2014]")
CIK_REGEX = re.compile(r"edgar_data_(\d+)_")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
logger = logging.getLogger(__name__)


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


def parse_cik_from_filename(filename: str) -> Optional[str]:
    """Best-effort extract of CIK from EDGAR filename."""
    match = CIK_REGEX.search(filename)
    if match:
        return match.group(1)
    return None


def filing_context(path: str) -> Tuple[str, str, str]:
    """Return best-effort (year, form, cik) context for a filing path."""
    base = os.path.basename(path)
    year = os.path.basename(os.path.dirname(path))
    if not looks_like_year(year):
        year_match = re.match(r"(\d{4})", base)
        year = year_match.group(1) if year_match else "unknown"
    form = parse_form_from_filename(base) or "unknown"
    cik = parse_cik_from_filename(base) or "unknown"
    return year, form, cik


def iter_filings(
    base_dir: str, include_forms: Optional[Set[str]], include_years: Optional[Set[str]]
) -> Iterator[str]:
    """
    Yield absolute paths to .txt filing files under base_dir **only inside year subfolders**,
    skipping derived outputs and (optionally) non-matching forms.

    Parameters
    ----------
    base_dir : str
        Root directory containing filing .txt files with year subfolders.
    include_forms : Optional[Set[str]]
        If provided, only files whose parsed form is in this set will be yielded.
    include_years : Optional[Set[str]]
        If provided, only year folders in this set will be scanned.
    """
    for year in sorted(os.listdir(base_dir)):
        if include_years is not None and year not in include_years:
            continue
        year_path = os.path.join(base_dir, year)
        if not os.path.isdir(year_path) or not looks_like_year(year):
            # Ignore root-level files and non-year folders
            continue
        for root, _, files in os.walk(year_path):
            for fn in files:
                if not fn.endswith(".txt"):
                    continue
                # Skip derived/secondary outputs in any folder
                base = fn
                if any(base.endswith(suf) for suf in DERIVED_SUFFIXES):
                    continue
                if any(substr in base for substr in SKIP_SUBSTRINGS):
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
        status in {"ok", "skipped_exists", "empty", "error"}
        count  = number of AI sentences written
        out_path = output filepath
    """
    base = os.path.basename(path)
    if any(base.endswith(suf) for suf in DERIVED_SUFFIXES):
        return "empty", 0, path[:-4] + "_ai_sentences.txt"

    out_path = path[:-4] + "_ai_sentences.txt"
    if (not force) and os.path.exists(out_path):
        return "skipped_exists", 0, out_path

    try:
        try:
            # Read as strict UTF-8; decoding issues are reported and the file is skipped.
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            logger.error("Input filing not found: %s", path)
            return "error", 0, out_path
        except PermissionError:
            logger.error("Permission denied reading filing: %s", path)
            return "error", 0, out_path
        except UnicodeDecodeError:
            logger.error("Failed to decode filing as UTF-8: %s", path)
            return "error", 0, out_path
        except OSError:
            logger.error("OS error reading filing: %s", path, exc_info=True)
            return "error", 0, out_path

        if not text.strip():
            # Touch an empty output to mark it processed
            try:
                with open(out_path, "w", encoding="utf-8"):
                    pass
            except PermissionError:
                logger.error("Permission denied writing empty output: %s", out_path)
                return "error", 0, out_path
            except OSError:
                logger.error("OS error writing empty output: %s", out_path, exc_info=True)
                return "error", 0, out_path
            return "empty", 0, out_path

        try:
            sentences = segment_sentences(text)
            page_marker_candidate_count = sum(1 for s in sentences if PAGE_MARKER_REGEX.search(s))
            segmented_count = len(sentences)
            page_merged = merge_page_fragments(sentences, raw_text=text)
            after_page_merge_count = len(page_merged)
            merged = merge_sentence_fragments(page_merged)
            after_sentence_merge_count = len(merged)
            page_fragments_merged = max(0, segmented_count - after_page_merge_count)
            sentence_fragments_merged = max(0, after_page_merge_count - after_sentence_merge_count)
            total_fragments_merged = max(0, segmented_count - after_sentence_merge_count)
            validate_sentence_completion(merged, path)
            ai_sents = filter_ai_sentences(merged, keywords)
            ai_sentence_count = len(ai_sents)
        except (IndexError, TypeError, ValueError, RuntimeError) as exc:
            logger.error("Sentence extraction/merge failed for %s: %s", path, exc, exc_info=True)
            return "error", 0, out_path

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ai_sents))
        except PermissionError:
            logger.error("Permission denied writing output: %s", out_path)
            return "error", 0, out_path
        except OSError:
            logger.error("OS error writing output: %s", out_path, exc_info=True)
            return "error", 0, out_path

        logger.info(
            "Extraction complete for %s: ai_sentences=%d page_marker_candidates=%d "
            "page_fragments_merged=%d sentence_fragments_merged=%d total_fragments_merged=%d",
            path,
            ai_sentence_count,
            page_marker_candidate_count,
            page_fragments_merged,
            sentence_fragments_merged,
            total_fragments_merged,
        )
        if total_fragments_merged > 0:
            logger.debug(
                "Merge detail for %s: segmented_count=%d after_page_merge_count=%d "
                "after_sentence_merge_count=%d",
                path,
                segmented_count,
                after_page_merge_count,
                after_sentence_merge_count,
            )
        if ai_sentence_count == 0:
            logger.debug("No AI sentences found for %s after filtering.", path)

        return "ok", ai_sentence_count, out_path
    except Exception:
        logger.exception("Failed to process filing: %s", path)
        return "error", 0, out_path


def validate_sentence_completion(sentences: list[str], source_path: str) -> None:
    """
    Warn when sentence completion checks fail after merge steps.
    Checks:
    - starts with capital letter
    - ends with terminal punctuation (., !, ?)
    """
    for idx, sentence in enumerate(sentences, start=1):
        text = sentence.strip()
        if not text:
            logger.warning("Incomplete sentence in %s [idx=%d]: empty sentence", source_path, idx)
            continue
        starts_with_capital = text[0].isupper()
        ends_with_terminal_punct = text.endswith(SENTENCE_ENDINGS)
        if not starts_with_capital or not ends_with_terminal_punct:
            logger.warning(
                "Incomplete sentence in %s [idx=%d]: starts_with_capital=%s "
                "ends_with_terminal_punct=%s sentence=%r",
                source_path,
                idx,
                starts_with_capital,
                ends_with_terminal_punct,
                text,
            )


def configure_logging(level_name: str) -> None:
    """Initialize logging with a simple console format for CLI runs."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    else:
        root_logger.setLevel(level)
    logger.setLevel(level)


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract AI-related sentences from filings.")
    ap.add_argument(
        "--log-level",
        default="INFO",
        choices=LOG_LEVELS,
        help="Logging verbosity (default: INFO).",
    )
    ap.add_argument(
        "--input-dir",
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
        "--years",
        default="ALL",
        help="Comma-separated list of years to include (e.g., 2021,2022). Use 'ALL' for no filter.",
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
    configure_logging(args.log_level)

    if args.file:
        if not os.path.isfile(args.file):
            logger.error("Specified file not found: %s", args.file)
            sys.exit(1)
    if not os.path.isfile(args.keywords):
        logger.error("Keyword file not found: %s", args.keywords)
        sys.exit(1)
    keywords = load_keywords(args.keywords)
    if not keywords:
        logger.error("Keyword list is empty; cannot run extraction: %s", args.keywords)
        sys.exit(1)

    if args.file:
        year, form, cik = filing_context(args.file)
        logger.info("Processing filing year=%s form=%s cik=%s path=%s", year, form, cik, args.file)
        status, count, out_path = process_file(args.file, keywords, args.force)
        if status == "ok":
            logger.info(
                "Completed filing year=%s form=%s cik=%s status=ok ai_sentences=%d output=%s",
                year,
                form,
                cik,
                count,
                out_path,
            )
        elif status == "skipped_exists":
            logger.info(
                "Completed filing year=%s form=%s cik=%s status=skipped_exists output=%s",
                year,
                form,
                cik,
                out_path,
            )
        elif status == "error":
            logger.error(
                "Completed filing year=%s form=%s cik=%s status=error output=%s",
                year,
                form,
                cik,
                out_path,
            )
        else:
            logger.warning(
                "Completed filing year=%s form=%s cik=%s status=empty output=%s",
                year,
                form,
                cik,
                out_path,
            )
        return

    if not os.path.isdir(args.input_dir):
        logger.error("Input directory not found: %s", args.input_dir)
        sys.exit(1)

    include_forms: Optional[Set[str]]
    if args.include_forms.strip().upper() == "ALL":
        include_forms = None
    else:
        include_forms = {tok.strip() for tok in args.include_forms.split(",") if tok.strip()}

    include_years: Optional[Set[str]]
    if args.years.strip().upper() == "ALL":
        include_years = None
    else:
        include_years = {y.strip() for y in args.years.split(",") if y.strip()}

    totals = {"seen": 0, "wrote": 0, "skipped": 0, "empty": 0, "errors": 0}
    per_year: Dict[str, int] = {}

    logger.info("Starting AI sentence extraction run.")
    logger.info("Walking filings under: %s", args.input_dir)
    logger.info("Using keywords from: %s", args.keywords)
    logger.info("Loaded %d keywords.", len(keywords))
    if include_forms is None:
        logger.info("Form filter: ALL")
    else:
        logger.info("Form filter: %s", sorted(include_forms))
    if include_years is None:
        logger.info("Years filter: ALL")
    else:
        logger.info("Years filter: %s", sorted(include_years))
    if args.limit:
        logger.info("Limit: %d filings", args.limit)

    processed = 0
    for path in iter_filings(args.input_dir, include_forms, include_years):
        # Stop early if limit is set
        if args.limit and processed >= args.limit:
            break

        # Expect layout .../sec/<YEAR>/<file>.txt
        year = os.path.basename(os.path.dirname(path))
        _year, form, cik = filing_context(path)
        logger.info("Processing filing year=%s form=%s cik=%s path=%s", _year, form, cik, path)
        per_year[year] = per_year.get(year, 0) + 1
        totals["seen"] += 1

        status, count, out_path = process_file(path, keywords, args.force)
        if status == "ok":
            totals["wrote"] += 1
            processed += 1
            logger.info(
                "Completed filing year=%s form=%s cik=%s status=ok ai_sentences=%d output=%s",
                _year,
                form,
                cik,
                count,
                out_path,
            )
        elif status == "skipped_exists":
            totals["skipped"] += 1
            logger.info(
                "Completed filing year=%s form=%s cik=%s status=skipped_exists output=%s",
                _year,
                form,
                cik,
                out_path,
            )
        elif status == "error":
            totals["errors"] += 1
            logger.error(
                "Completed filing year=%s form=%s cik=%s status=error output=%s",
                _year,
                form,
                cik,
                out_path,
            )
        else:
            totals["empty"] += 1
            logger.warning(
                "Completed filing year=%s form=%s cik=%s status=empty output=%s",
                _year,
                form,
                cik,
                out_path,
            )

    # Summary
    logger.info(
        "Run summary: filings_scanned=%d wrote_new_outputs=%d skipped_exists=%d "
        "empty_filings=%d errors=%d",
        totals["seen"],
        totals["wrote"],
        totals["skipped"],
        totals["empty"],
        totals["errors"],
    )
    if per_year:
        logger.info("Per-year scanned:")
        for y in sorted(per_year):
            logger.info("  %s: %d", y, per_year[y])
    logger.debug("Tip: Press Ctrl+C to stop mid-run. Use --limit for quick checks.")


if __name__ == "__main__":
    main()
