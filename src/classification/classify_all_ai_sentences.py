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
import re

# Ensure we can import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classify import classify_sentence, CENTROIDS_PATH  # noqa: E402

# ——— Quick two-stage helpers (rule gate + soft boosts) ———
LISTY_TRIGGERS = re.compile(r"\b(including|such as|as well as|among other|and other)\b", re.I)
CATEGORY_WORDS = re.compile(r"\b(internet|e[- ]?commerce|web services|devices|advertis(ing|ement)|privacy|data protection|tax|employment|antitrust|tariff|omnichannel|electronic|robotics|virtual reality)\b", re.I)
MODALS = re.compile(r"\b(may|might|could|intend|plan|expect|aims?|anticipate|seek|hope)\b", re.I)
ACTION_VERBS = re.compile(r"\b(use|uses|using|deploy|deployed|embed|embedded|launch(?:ed|es)?|implement(?:ed|s)?|roll(?:ed)? out|in production|customers|reduced|improved|increased)\b", re.I)
PCT_OR_NUM = re.compile(r"\b\d+(?:\.\d+)?%|\b\d{2,}\b")


def is_irrelevant_by_rules(text: str, min_tokens: int = 6) -> bool:
    """Lightweight coarse filter for obvious Irrelevant sentences.
    - Very short or header-like lines
    - Laundry-list/regulatory lists where AI is one of many items
    - Glossary/definition style lines
    """
    toks = text.split()
    if len(toks) < min_tokens:
        return True
    if text.endswith(":") or text.isupper():
        return True
    # glossary / definition
    if re.search(r"\b(glossary|definition|defined as)\b", text, re.I):
        return True
    # list/laundry-list style with AI among many items
    commas = text.count(",")
    if LISTY_TRIGGERS.search(text) and CATEGORY_WORDS.search(text) and commas >= 3:
        # light density check so single appositives don't trigger
        if (commas / max(1, len(toks))) >= 0.06 and len(toks) > 12:
            return True
    return False


def adjust_scores(text: str, scores: dict) -> dict:
    """Softly nudge scores using simple lexical cues."""
    s = dict(scores)
    if MODALS.search(text):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.03
    if ACTION_VERBS.search(text) or PCT_OR_NUM.search(text):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.03
    return s


def classify_two_stage(text: str, tau: float = 0.05, eps_irr: float = 0.02, min_tokens: int = 6, use_rule_boosts: bool = False):
    """Two-step decision using existing centroid classifier.
    Step 1: rule gate obvious Irrelevant. Step 2: A vs S with optional soft boosts and margin logic.
    Returns (label, scores_with_margin)
    """
    if is_irrelevant_by_rules(text, min_tokens=min_tokens):
        return "Irrelevant", {"Actionable": 0.0, "Speculative": 0.0, "Irrelevant": 1.0, "fine_margin": None}

    label, scores = classify_sentence(text)
    if use_rule_boosts:
        scores = adjust_scores(text, scores)
    a, s, irr = scores.get("Actionable", 0.0), scores.get("Speculative", 0.0), scores.get("Irrelevant", 0.0)
    fine_margin = abs(a - s)

    # Prefer the stronger of A/S; if very close and Irrelevant is competitive, nudge toward Speculative to avoid over-claiming.
    if fine_margin < tau and irr >= max(a, s) - eps_irr:
        label = "Speculative" if s >= a else "Actionable"
    else:
        label = "Speculative" if s >= a else "Actionable"

    scores["fine_margin"] = round(fine_margin, 3)
    return label, scores


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


def classify_file(
    input_path: str,
    force: bool = False,
    quick_two_stage: bool = False,
    rule_boosts: bool = False,
    tau: float = 0.05,
    eps_irr: float = 0.02,
    min_tokens: int = 6
) -> str:
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
            if quick_two_stage:
                label, scores = classify_two_stage(sent, tau=tau, eps_irr=eps_irr, min_tokens=min_tokens, use_rule_boosts=rule_boosts)
            else:
                label, scores = classify_sentence(sent)
                if rule_boosts:
                    scores = adjust_scores(sent, scores)
                    label = max(scores.items(), key=lambda x: x[1])[0]
            outputs.append(f"{sent} | Label: {label} | Scores: {scores}")
        except Exception as e:
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
    parser.add_argument("--quick-two-stage", action="store_true", help="Use rule gate for Irrelevant, then A/S with margin tweak")
    parser.add_argument("--rule-boosts", action="store_true", help="Apply soft boosts to A/S scores based on lexical cues")
    parser.add_argument("--tau", type=float, default=0.05, help="Fine-stage A/S margin threshold (default 0.05)")
    parser.add_argument("--eps-irr", type=float, default=0.02, help="Irrelevant closeness epsilon (default 0.02)")
    parser.add_argument("--min-tokens", type=int, default=6, help="Minimum tokens to consider non-fragment (default 6)")
    args = parser.parse_args()

    quick_two_stage = args.quick_two_stage
    rule_boosts = args.rule_boosts
    tau = args.tau
    eps_irr = args.eps_irr
    min_tokens = args.min_tokens

    refresh_if_centroids_newer = args.refresh_if_centroids_newer

    base_dir = args.base_dir
    years = args.years
    limit = args.limit
    force = args.force
    # Prepare runtime options for classify_file

    try:
        centroids_mtime = os.path.getmtime(CENTROIDS_PATH)
    except Exception:
        centroids_mtime = None
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

        print(f"🔍 {i:>4}/{len(files)} Classifying → {os.path.relpath(outp)}")
        classify_file(
            inp,
            force=True if force else False,
            quick_two_stage=quick_two_stage,
            rule_boosts=rule_boosts,
            tau=tau,
            eps_irr=eps_irr,
            min_tokens=min_tokens
        )
        processed += 1
    print(f"Base dir: {base_dir}")
    if years:
        print(f"Years: {', '.join(years)}")


if __name__ == "__main__":
    main()