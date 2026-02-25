"""
Batch classifier for AI-related sentences using SentenceBERT and cosine similarity.

This script searches for *_ai_sentences.txt files under data/processed/sec (including
year subfolders like 2021/, 2022/ ...), classifies each sentence using the classify_sentence() function,
and writes results to sibling *_classified.csv files.

Usage examples:
    # Scan everything recursively under the default base dir
    python src/classification/classify_all_ai_sentences.py

    # Only scan specific years and cap work for a quick check
    python src/classification/classify_all_ai_sentences.py --years 2021 2022 --limit 10

    # Recompute even if *_classified.csv exists
    python src/classification/classify_all_ai_sentences.py --force

    # Rebuild only files older than centroids (default)
    python src/classification/classify_all_ai_sentences.py --years 2024

    # Force rebuild of everything regardless of timestamps
    python src/classification/classify_all_ai_sentences.py --years 2024 --force
"""

import os
import sys
import argparse
import csv
import logging
from typing import List, Optional

CENTROIDS_PATH = "data/validation/centroids_mpnet.json"
logger = logging.getLogger(__name__)

_CLASSIFY_TWO_STAGE = None


def _get_classify_two_stage():
    """Lazy import to keep --help fast and avoid eager model initialization."""
    global _CLASSIFY_TWO_STAGE
    if _CLASSIFY_TWO_STAGE is None:
        from semantic_ai_washing.core.classify import classify_two_stage

        _CLASSIFY_TWO_STAGE = classify_two_stage
    return _CLASSIFY_TWO_STAGE


def find_ai_sentence_files(
    base_dir: str, years: Optional[List[str]] = None, limit: int = 0
) -> List[str]:
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
    min_tokens: int = 6,
) -> str:
    """
    Classify the sentences in a single *_ai_sentences.txt file.

    Returns the output path for the written *_classified.csv file (or existing one if skipped).
    """
    output_path = input_path.replace("_ai_sentences.txt", "_classified.csv")

    # Skip if already classified and not forcing
    if not force and os.path.exists(output_path):
        return output_path

    # Read sentences
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            sentences = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("Input AI sentence file not found: %s", input_path)
        raise
    except PermissionError:
        logger.error("Permission denied reading AI sentence file: %s", input_path)
        raise
    except OSError:
        logger.error("OS error reading AI sentence file: %s", input_path, exc_info=True)
        raise

    if not sentences:
        logger.warning("Input AI sentence file has no non-empty sentences: %s", input_path)

    # Prepare rows for CSV
    rows = []

    def _unpack_scores(scores_obj):
        """
        Try to read probabilities and/or cosine similarities for A/S/I from a variety of dict shapes.
        Returns: (pA, pS, pI, cA, cS, cI) possibly None if not available.
        """
        pA = pS = pI = None
        cA = cS = cI = None

        if isinstance(scores_obj, dict):
            # First pass: flat keys
            for k, v in scores_obj.items():
                kk = str(k).lower()
                if kk in ("a", "actionable", "p_actionable"):
                    pA = v
                elif kk in ("s", "speculative", "p_speculative"):
                    pS = v
                elif kk in ("i", "irrelevant", "p_irrelevant"):
                    pI = v
                elif kk in ("cos_a", "cos_to_a", "sim_a"):
                    cA = v
                elif kk in ("cos_s", "cos_to_s", "sim_s"):
                    cS = v
                elif kk in ("cos_i", "cos_to_i", "sim_i"):
                    cI = v
            # Second pass: common nests
            for nest in ("probs", "scores", "sims", "cos", "cosines"):
                sub = scores_obj.get(nest)
                if isinstance(sub, dict):
                    pA2, pS2, pI2, cA2, cS2, cI2 = _unpack_scores(sub)
                    pA = pA if pA is not None else pA2
                    pS = pS if pS is not None else pS2
                    pI = pI if pI is not None else pI2
                    cA = cA if cA is not None else cA2
                    cS = cS if cS is not None else cS2
                    cI = cI if cI is not None else cI2
        elif isinstance(scores_obj, (list, tuple)) and len(scores_obj) >= 3:
            # Heuristic: treat as [pA, pS, pI]
            pA, pS, pI = scores_obj[:3]

        return pA, pS, pI, cA, cS, cI

    for sent_idx, sent in enumerate(sentences, start=1):
        try:
            classify_two_stage = _get_classify_two_stage()
            label, scores = classify_two_stage(
                sent,
                two_stage=quick_two_stage,
                rule_boosts=rule_boosts,
                tau=tau,
                eps_irr=eps_irr,
                min_tokens=min_tokens,
            )
            pA, pS, pI, cA, cS, cI = _unpack_scores(scores)
            rows.append(
                {
                    "sentence": sent,
                    "label_pred": label,
                    "p_actionable": pA,
                    "p_speculative": pS,
                    "p_irrelevant": pI,
                    "cos_to_A": cA,
                    "cos_to_S": cS,
                    "cos_to_I": cI,
                    "tau": tau,
                    "eps_irr": eps_irr,
                    "min_tokens": min_tokens,
                }
            )
        except (ValueError, RuntimeError, TypeError) as exc:
            logger.warning(
                "Sentence classification failed for %s [idx=%d]: %s",
                input_path,
                sent_idx,
                exc,
                exc_info=True,
            )
            rows.append(
                {
                    "sentence": sent,
                    "label_pred": "ERROR",
                    "p_actionable": None,
                    "p_speculative": None,
                    "p_irrelevant": None,
                    "cos_to_A": None,
                    "cos_to_S": None,
                    "cos_to_I": None,
                    "tau": tau,
                    "eps_irr": eps_irr,
                    "min_tokens": min_tokens,
                }
            )
        except Exception:
            logger.exception(
                "Unexpected sentence classification failure for %s [idx=%d]",
                input_path,
                sent_idx,
            )
            rows.append(
                {
                    "sentence": sent,
                    "label_pred": "ERROR",
                    "p_actionable": None,
                    "p_speculative": None,
                    "p_irrelevant": None,
                    "cos_to_A": None,
                    "cos_to_S": None,
                    "cos_to_I": None,
                    "tau": tau,
                    "eps_irr": eps_irr,
                    "min_tokens": min_tokens,
                }
            )

    # Ensure directory exists and write CSV (held-out-friendly columns)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = [
        "sentence",
        "label_pred",
        "p_actionable",
        "p_speculative",
        "p_irrelevant",
        "cos_to_A",
        "cos_to_S",
        "cos_to_I",
        "tau",
        "eps_irr",
        "min_tokens",
    ]
    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError:
        logger.error("Permission denied writing classification output: %s", output_path)
        raise
    except OSError:
        logger.error("OS error writing classification output: %s", output_path, exc_info=True)
        raise

    return output_path


def main():
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Batch classify AI sentences across filings.")
    parser.add_argument(
        "--base-dir", default="data/processed/sec", help="Root dir containing filings."
    )
    parser.add_argument(
        "--years",
        nargs="*",
        default=None,
        help="Optional list of year folders to scan (e.g., 2021 2022 2023 2024).",
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Max files to process (0 = no limit)."
    )
    parser.add_argument(
        "--force", action="store_true", help="Recompute even if *_classified.csv exists."
    )
    parser.add_argument(
        "--refresh-if-centroids-newer",
        action="store_true",
        default=True,
        help="Rebuild outputs if centroids file is newer than existing *_classified.csv (default: on)",
    )
    parser.add_argument(
        "--no-refresh-if-centroids-newer",
        dest="refresh_if_centroids_newer",
        action="store_false",
        help="Disable timestamp-based refresh logic",
    )
    parser.add_argument(
        "--two-stage",
        dest="two_stage",
        action="store_true",
        help="Enable Irrelevant gate + A/S margin logic (two-stage)",
    )
    parser.add_argument(
        "--rule-boosts",
        dest="rule_boosts",
        action="store_true",
        help="Apply regex/lexical boosts used in evaluation",
    )
    # Back-compat aliases
    parser.add_argument(
        "--quick-two-stage", dest="two_stage", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--tau", type=float, default=0.05, help="Fine-stage A/S margin threshold (default 0.05)"
    )
    parser.add_argument(
        "--eps-irr", type=float, default=0.02, help="Irrelevant closeness epsilon (default 0.02)"
    )
    parser.add_argument(
        "--min-tokens",
        type=int,
        default=6,
        help="Minimum tokens to consider non-fragment (default 6)",
    )
    args = parser.parse_args()

    quick_two_stage = getattr(args, "two_stage", False)
    rule_boosts = getattr(args, "rule_boosts", False)
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
    except OSError:
        centroids_mtime = None

    if not os.path.isdir(base_dir):
        logger.error("Base directory not found: %s", base_dir)
        sys.exit(1)
    if not os.path.isfile(CENTROIDS_PATH):
        logger.error("Centroids file not found: %s", CENTROIDS_PATH)
        sys.exit(1)
    if centroids_mtime is None:
        logger.error("Centroids file is not readable: %s", CENTROIDS_PATH)
        sys.exit(1)
    try:
        _get_classify_two_stage()
    except Exception:
        logger.exception(
            "Classifier initialization failed (model/centroids). "
            "Verify local model dependencies and centroids file: %s",
            CENTROIDS_PATH,
        )
        sys.exit(1)

    files = find_ai_sentence_files(base_dir, years, limit)
    print(
        f"[✓] Found {len(files)} AI sentence files under {base_dir}"
        + (f" for years {years}" if years else "")
    )

    processed = 0
    skipped = 0
    errors = 0
    for i, inp in enumerate(files, 1):
        outp = inp.replace("_ai_sentences.txt", "_classified.csv")
        # Decide whether to skip or rebuild
        if os.path.exists(outp) and not force:
            # If centroids are newer than the existing output, rebuild (unless disabled)
            if refresh_if_centroids_newer and centroids_mtime is not None:
                try:
                    out_mtime = os.path.getmtime(outp)
                except OSError:
                    out_mtime = -1
                if out_mtime < centroids_mtime:
                    print(
                        f"♻️  {i:>4}/{len(files)} Rebuild (centroids newer): {os.path.relpath(outp)}"
                    )
                else:
                    skipped += 1
                    print(f"⏭️  {i:>4}/{len(files)} Skip (up-to-date): {os.path.relpath(outp)}")
                    continue
            else:
                skipped += 1
                print(f"⏭️  {i:>4}/{len(files)} Skip (exists): {os.path.relpath(outp)}")
                continue

        print(f"🔍 {i:>4}/{len(files)} Classifying → {os.path.relpath(outp)}")
        try:
            classify_file(
                inp,
                force=bool(force),
                quick_two_stage=quick_two_stage,
                rule_boosts=rule_boosts,
                tau=tau,
                eps_irr=eps_irr,
                min_tokens=min_tokens,
            )
            processed += 1
        except (FileNotFoundError, PermissionError, OSError, ValueError, RuntimeError) as exc:
            errors += 1
            logger.error(
                "Failed classifying file %s (%d/%d): %s",
                inp,
                i,
                len(files),
                exc,
                exc_info=True,
            )
            continue
        except Exception:
            errors += 1
            logger.exception("Unexpected failure classifying file %s (%d/%d)", inp, i, len(files))
            continue

    print(
        f"[Summary] processed={processed}, skipped={skipped}, errors={errors}, total={len(files)}"
    )
    print(f"Base dir: {base_dir}")
    if years:
        print(f"Years: {', '.join(years)}")


if __name__ == "__main__":
    main()
