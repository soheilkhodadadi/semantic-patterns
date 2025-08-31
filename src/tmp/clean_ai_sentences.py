"""
Clean an aggregated CSV of AI sentences by removing likely-incomplete lines and duplicates.

Input (auto-detected):
  - Columns may be either (sentence,label) or (sent_text,label_pred).
  - Extra columns are ignored.

Output:
  - CSV with exactly two columns: sentence,label
  - Sidecar report: <output>.report.txt with summary stats.

Heuristics (tunable via CLI flags):
  - Drop if token count < --min-tokens (default: 3)
  - Drop if character count < --min-chars (default: 12)
  - Drop if the first alphabetic character is not uppercase (unless --no-require-capital)
  - Drop if the sentence does not end with terminal punctuation . ! ? (unless --no-require-terminal)
  - Drop if the text is mostly non-letters or numeric fragments
  - Deduplicate on normalized sentence (casefold if --dedupe-casefold)

Example:
  python src/tmp/clean_ai_sentences.py \
    --input data/validation/CollectedAiSentencesClassified.csv \
    --output data/validation/CollectedAiSentencesClassified_clean.csv \
    --min-tokens 3 --min-chars 12 --require-capital --require-terminal --dedupe-casefold
"""
import argparse
import csv
import os
import re
import sys
from typing import Dict

try:
    import pandas as pd
except Exception:
    print("[!] pandas is required. pip install pandas", file=sys.stderr)
    raise

ALLOWED_TERMINALS_RE = re.compile(r"[.!?][\)\]\"'”’]*\s*$")
STRIP_OUTER_QUOTES_RE = re.compile(r'^\s*["“”‘’\']*(.*?)["“”‘’\']*\s*$')
FIRST_ALPHA_RE = re.compile(r"[A-Za-z]")

def normalize_sentence(s: str, drop_outer_quotes: bool = True) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    if drop_outer_quotes:
        m = STRIP_OUTER_QUOTES_RE.match(s)
        if m:
            s = m.group(1).strip()
    s = re.sub(r"\s+", " ", s)  # collapse whitespace
    return s

def first_alpha_is_capital(s: str) -> bool:
    m = FIRST_ALPHA_RE.search(s)
    return bool(m and m.group(0).isupper())

def ends_with_terminal(s: str) -> bool:
    return bool(ALLOWED_TERMINALS_RE.search(s))

def mostly_non_letters(s: str, threshold: float = 0.6) -> bool:
    if not s:
        return True
    letters = sum(ch.isalpha() for ch in s)
    return (len(s) - letters) / max(len(s), 1) >= threshold

def is_incomplete(s: str,
                  min_tokens: int,
                  min_chars: int,
                  require_capital: bool,
                  require_terminal: bool):
    tokens = s.split()
    if len(tokens) < min_tokens:
        return True, f"tokens<{min_tokens}"
    if len(s) < min_chars:
        return True, f"chars<{min_chars}"
    if require_capital and not first_alpha_is_capital(s):
        return True, "no_initial_cap"
    if require_terminal and not ends_with_terminal(s):
        return True, "no_terminal_punct"
    if mostly_non_letters(s):
        return True, "mostly_non_letters"
    return False, ""

def choose_columns(df: "pd.DataFrame"):
    cols_lower = {c.lower(): c for c in df.columns}
    sent_col = cols_lower.get("sentence") or cols_lower.get("sent_text")
    lab_col = cols_lower.get("label") or cols_lower.get("label_pred")
    if not sent_col or not lab_col:
        raise ValueError(
            "Could not detect sentence/label columns. "
            "Expected one of: sentence|sent_text and label|label_pred"
        )
    return sent_col, lab_col

def main():
    ap = argparse.ArgumentParser(description="Clean and deduplicate AI sentences CSV")
    ap.add_argument("--input", required=True, help="Path to input CSV")
    ap.add_argument("--output", required=True, help="Path to output CSV")
    ap.add_argument("--report", default=None, help="Optional path to write a cleaning report (.txt)")
    ap.add_argument("--min-tokens", type=int, default=3)
    ap.add_argument("--min-chars", type=int, default=12)
    ap.add_argument("--require-capital", action="store_true", help="Require first alphabetic char to be uppercase")
    ap.add_argument("--no-require-capital", dest="require_capital", action="store_false")
    ap.add_argument("--require-terminal", action="store_true", help="Require sentence to end with . ! or ?")
    ap.add_argument("--no-require-terminal", dest="require_terminal", action="store_false")
    ap.add_argument("--drop-outer-quotes", action="store_true", help="Strip surrounding quotes before checks (default on)")
    ap.add_argument("--keep-outer-quotes", dest="drop_outer_quotes", action="store_false")
    ap.add_argument("--dedupe-casefold", action="store_true", help="Deduplicate using casefolded sentence")
    ap.set_defaults(require_capital=True, require_terminal=True, drop_outer_quotes=True)

    args = ap.parse_args()

    df = pd.read_csv(args.input)
    sent_col, lab_col = choose_columns(df)

    # Normalize text
    df["sentence_norm"] = df[sent_col].astype(str).map(lambda s: normalize_sentence(s, args.drop_outer_quotes))

    # Filter
    dropped_reasons: Dict[str, int] = {}
    keep_mask = []
    reasons = []
    for s in df["sentence_norm"].tolist():
        drop, why = is_incomplete(
            s,
            min_tokens=args.min_tokens,
            min_chars=args.min_chars,
            require_capital=args.require_capital,
            require_terminal=args.require_terminal,
        )
        keep_mask.append(not drop)
        reasons.append(why)
        if drop:
            dropped_reasons[why] = dropped_reasons.get(why, 0) + 1

    df["_keep"] = keep_mask
    df["_why"] = reasons
    kept = df[df["_keep"]].copy()

    # Deduplicate (preserve order)
    seen = set()
    uniq_rows = []
    key_func = (lambda s: s.casefold()) if args.dedupe_casefold else (lambda s: s)
    for _, r in kept.iterrows():
        key = key_func(r["sentence_norm"])
        if key in seen:
            continue
        seen.add(key)
        uniq_rows.append((r["sentence_norm"], r[lab_col]))

    # Write output (two columns only)
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sentence", "label"])
        for s, lab in uniq_rows:
            if pd.isna(lab):
                continue
            lab_str = str(lab).strip()
            if not lab_str or lab_str.upper() == "ERROR":
                continue
            w.writerow([s, lab_str])

    # Report
    report_path = args.report or (args.output + ".report.txt")
    try:
        total_in = len(df)
        total_kept_basic = len(kept)
        total_kept_final = len(uniq_rows)
        with open(report_path, "w", encoding="utf-8") as rf:
            rf.write("Cleaning report\n")
            rf.write("================\n")
            rf.write(f"Input: {args.input}\n")
            rf.write(f"Output: {args.output}\n")
            rf.write(f"Total rows read: {total_in}\n")
            rf.write(f"After filters kept: {total_kept_basic}\n")
            rf.write(f"After de-duplication kept: {total_kept_final}\n")
            rf.write(f"Dropped (filters): {total_in - total_kept_basic}\n")
            rf.write("\nDrop reasons:\n")
            for k, v in sorted(dropped_reasons.items(), key=lambda kv: (-kv[1], kv[0])):
                rf.write(f"  {k}: {v}\n")
            rf.write("\nFlags:\n")
            rf.write(f"  min_tokens={args.min_tokens}, min_chars={args.min_chars}\n")
            rf.write(f"  require_capital={args.require_capital}, require_terminal={args.require_terminal}\n")
            rf.write(f"  drop_outer_quotes={args.drop_outer_quotes}, dedupe_casefold={args.dedupe_casefold}\n")
        print(f"[✓] Wrote cleaned CSV: {args.output}")
        print(f"[✓] Wrote report: {report_path}")
    except Exception as e:
        print(f"[i] Could not write report: {e}")

if __name__ == "__main__":
    main()