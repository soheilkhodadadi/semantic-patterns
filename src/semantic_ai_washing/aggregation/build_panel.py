# src/aggregation/build_panel.py
import os
import argparse
import pandas as pd


def normalize_cik(x):
    s = "".join([c for c in str(x) if c.isdigit()])
    return s.zfill(10) if s else ""


def ensure_dirs():
    os.makedirs("data/processed/panel", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


def read_csv_safely(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing input: {path}")
    return pd.read_csv(path)


def write_qc_report(path_md, panel):
    lines = []
    lines.append("# Merge QC\n")
    lines.append(f"- Rows: **{len(panel)}**")
    if not panel.empty:
        # basic coverage/missingness
        miss = panel.isna().mean().sort_values(ascending=False).round(3)
        miss_tbl = miss.to_frame("missing_share").reset_index().rename(columns={"index": "column"})

        # markdown fallback without tabulate
        def df_to_md(df):
            cols = list(df.columns)
            out = []
            out.append("| " + " | ".join(cols) + " |")
            out.append("| " + " | ".join(["---"] * len(cols)) + " |")
            for _, r in df.iterrows():
                out.append(
                    "| " + " | ".join("" if pd.isna(r[c]) else str(r[c]) for c in cols) + " |"
                )
            return "\n".join(out)

        lines.append("\n## Missingness\n")
        lines.append(df_to_md(miss_tbl))
        # duplicate keys check
        dup = panel.duplicated(subset=["cik", "year"], keep=False).sum()
        lines.append(f"\n- Duplicate (cik,year) rows: **{int(dup)}**")
        # year span
        yr = pd.to_numeric(panel["year"], errors="coerce")
        if yr.notna().any():
            lines.append(f"- Year span: {int(yr.min())}–{int(yr.max())}")
    with open(path_md, "w") as f:
        f.write("\n".join(lines))
    print(f"[✓] Wrote QC: {path_md}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ai-patents",
        default="data/processed/ai_freq_patents_firm_year.csv",
        help="AI frequencies with patents by firm-year (left table).",
    )
    ap.add_argument(
        "--controls",
        default="data/interim/controls/controls_by_firm_year.csv",
        help="Compustat controls by firm-year (right table).",
    )
    ap.add_argument("--out", default="data/processed/panel/panel_ai_patents_controls.csv")
    ap.add_argument("--qc", default="reports/merge_qc.md")
    args = ap.parse_args()

    ensure_dirs()

    left = read_csv_safely(
        args.ai_patents
    ).copy()  # expect keys: cik, year (+ doc_count, n_A, n_S, n_I, ai_total, patents_ai, etc.)
    right = read_csv_safely(
        args.controls
    ).copy()  # expect keys: cik, year (+ gvkey, sic, ln_assets, ...)

    # Normalize keys
    left["cik"] = left["cik"].apply(normalize_cik)
    right["cik"] = right["cik"].apply(normalize_cik)

    # Coerce year to int where possible
    for df in (left, right):
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # Deduplicate within each source on (cik, year) keeping the last (often most complete)
    left = left.sort_values(["cik", "year"]).drop_duplicates(subset=["cik", "year"], keep="last")
    right = right.sort_values(["cik", "year"]).drop_duplicates(subset=["cik", "year"], keep="last")

    # Merge (left join to keep all AI frequency rows)
    panel = left.merge(right, on=["cik", "year"], how="left", suffixes=("", "_ctrl"))

    # Optional: tidy columns order (keeps what exists, ignores missing gracefully)
    preferred = [
        "cik",
        "year",
        "gvkey",
        "sic",
        # AI frequency side (adjust names to your file’s columns)
        "doc_count",
        "n_total",
        "n_A",
        "n_S",
        "n_I",
        "ai_total",
        "share_A",
        "share_S",
        "share_I",
        "patents_ai",
        "patents_total",
        # controls
        "ln_assets",
        "leverage",
        "cash",
        "rd_intensity",
        "capx_at",
        "roa",
        "sales_growth",
        "emp",
    ]
    cols = [c for c in preferred if c in panel.columns] + [
        c for c in panel.columns if c not in preferred
    ]
    panel = panel[cols]

    # Final basic sanity
    if "share_A" in panel and "share_S" in panel and "share_I" in panel:
        shares = panel[["share_A", "share_S", "share_I"]].sum(axis=1)
        bad = (~shares.isna()) & ((shares < 0.95) | (shares > 1.05))
        if bad.any():
            n = int(bad.sum())
            print(f"[!] {n} rows where shares don’t sum ≈ 1 (±0.05).")

    panel.to_csv(args.out, index=False)
    print(f"[✓] Saved panel to {args.out} (rows={len(panel)})")

    write_qc_report(args.qc, panel)


if __name__ == "__main__":
    main()
