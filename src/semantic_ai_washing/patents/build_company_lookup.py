# src/patents/build_company_lookup.py
"""
Build a normalized company lookup table for patent matching.

The broader Iteration 3 patent lane needs a company lookup that can be built from
CIK-only filing universes, optionally enriched with a WRDS crosswalk and a CIK→ticker
reference file. This script keeps the original 50-firm path working while allowing the
lookup to scale to the active filing universe.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable

import pandas as pd

SRC = "data/metadata/company_list_50.csv"
OUT_MAIN = "data/metadata/company_lookup.csv"
OUT_ALIASES = "data/metadata/company_aliases.csv"


def clean_company_name(name: str) -> str:
    """Lowercase, strip common suffixes, remove punctuation, and normalize spaces."""
    if pd.isna(name):
        return ""
    s = str(name).lower()
    suffixes = [
        r"\s+inc\.?$",
        r"\s+corp\.?$",
        r"\s+corporation$",
        r"\s+ltd\.?$",
        r"\s+llc$",
        r"\s+plc$",
        r"\s+co\.?$",
        r"\s+company$",
        r"\s+holdings?$",
        r"\s+group$",
    ]
    for suf in suffixes:
        s = re.sub(suf, "", s)
    s = re.sub(r"[^\w\s]", "", s)
    s = " ".join(s.split())
    return s.strip()


def normalize_cik(x) -> str:
    if pd.isna(x) or str(x).strip() == "":
        return ""
    digits = re.sub(r"\D", "", str(x))
    if digits == "":
        return ""
    return digits.zfill(10)


def normalize_ticker(x) -> str:
    if pd.isna(x) or str(x).strip() == "":
        return ""
    return str(x).upper().strip()


def infer_columns(df: pd.DataFrame):
    cols = {c.lower(): c for c in df.columns}

    def find(*cands):
        for cand in cands:
            if cand in cols:
                return cols[cand]
        return None

    name_col = find("name", "company", "company_name", "issuer", "issuer_name", "conm")
    cik_col = find("cik", "cik_code", "sec_cik")
    ticker_col = find("ticker", "symbol", "tic", "ticker_comp")
    alias_col = find("alias", "alt_name", "aka")
    gvkey_col = find("gvkey")
    sic_col = find("sic")
    return {
        "name": name_col,
        "cik": cik_col,
        "ticker": ticker_col,
        "alias": alias_col,
        "gvkey": gvkey_col,
        "sic": sic_col,
    }


def load_company_source(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing input: {path}")

    raw = pd.read_csv(path)
    cols = infer_columns(raw)
    if cols["name"] is None and cols["cik"] is None and cols["ticker"] is None:
        raise ValueError(
            f"{path} must contain at least one of: company name, cik, or ticker columns."
        )

    out = pd.DataFrame(index=raw.index)
    out["cik"] = raw[cols["cik"]].apply(normalize_cik) if cols["cik"] else ""
    out["name"] = raw[cols["name"]].fillna("").astype(str).str.strip() if cols["name"] else ""
    out["ticker"] = (
        raw[cols["ticker"]].apply(normalize_ticker)
        if cols["ticker"]
        else pd.Series([""] * len(raw), index=raw.index)
    )
    out["gvkey"] = (
        raw[cols["gvkey"]].fillna("").astype(str).str.strip()
        if cols["gvkey"]
        else pd.Series([""] * len(raw), index=raw.index)
    )
    out["sic"] = (
        raw[cols["sic"]] if cols["sic"] else pd.Series([pd.NA] * len(raw), index=raw.index)
    )

    alias_rows = pd.DataFrame(columns=["cik", "alias", "alias_source"])
    if cols["alias"] is not None:
        alias_rows = pd.DataFrame(
            {
                "cik": out["cik"],
                "alias": raw[cols["alias"]].fillna("").astype(str).str.strip(),
                "alias_source": "input_alias",
            }
        )
        alias_rows = alias_rows[alias_rows["alias"] != ""]

    out = out[(out["cik"] != "") | (out["name"] != "") | (out["ticker"] != "")].copy()
    out.reset_index(drop=True, inplace=True)
    alias_rows.reset_index(drop=True, inplace=True)
    return out, alias_rows


def coalesce_nonblank(first: pd.Series, *rest: Iterable[pd.Series]) -> pd.Series:
    result = first.astype("object")
    result = result.where(result.fillna("").astype(str).str.strip() != "", pd.NA)
    for series in rest:
        candidate = series.astype("object")
        candidate = candidate.where(candidate.fillna("").astype(str).str.strip() != "", pd.NA)
        result = result.combine_first(candidate)
    return result


def build_lookup(
    base: pd.DataFrame, crosswalk: pd.DataFrame | None, ticker_map: pd.DataFrame | None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    lookup = base.copy()

    if crosswalk is not None and not crosswalk.empty:
        cross = crosswalk.copy()
        cross.columns = [str(c) for c in cross.columns]
        cross["cik"] = cross["cik"].apply(normalize_cik)
        if "ticker_comp" in cross.columns:
            cross["ticker_comp"] = cross["ticker_comp"].apply(normalize_ticker)
        else:
            cross["ticker_comp"] = ""
        cross["name"] = (
            cross.get("name", pd.Series([""] * len(cross))).fillna("").astype(str).str.strip()
        )
        cross["gvkey"] = (
            cross.get("gvkey", pd.Series([""] * len(cross))).fillna("").astype(str).str.strip()
        )
        cross = cross.rename(
            columns={
                "name": "name_crosswalk",
                "gvkey": "gvkey_crosswalk",
                "sic": "sic_crosswalk",
            }
        )
        lookup = lookup.merge(
            cross[
                ["cik", "name_crosswalk", "ticker_comp", "gvkey_crosswalk", "sic_crosswalk"]
            ].drop_duplicates(subset=["cik"]),
            on="cik",
            how="left",
        )
    else:
        lookup["name_crosswalk"] = ""
        lookup["ticker_comp"] = ""
        lookup["sic_crosswalk"] = pd.NA

    if ticker_map is not None and not ticker_map.empty:
        tick = ticker_map.copy()
        tick.columns = [str(c) for c in tick.columns]
        cols = infer_columns(tick)
        tick_out = pd.DataFrame()
        tick_out["cik"] = tick[cols["cik"]].apply(normalize_cik) if cols["cik"] else ""
        tick_out["name_ticker_map"] = (
            tick[cols["name"]].fillna("").astype(str).str.strip()
            if cols["name"]
            else pd.Series([""] * len(tick), index=tick.index)
        )
        tick_out["ticker_map"] = (
            tick[cols["ticker"]].apply(normalize_ticker)
            if cols["ticker"]
            else pd.Series([""] * len(tick), index=tick.index)
        )
        tick_out["sic_ticker_map"] = (
            tick[cols["sic"]] if cols["sic"] else pd.Series([pd.NA] * len(tick), index=tick.index)
        )
        tick_out = tick_out[tick_out["cik"] != ""].drop_duplicates(subset=["cik"])
        lookup = lookup.merge(tick_out, on="cik", how="left")
    else:
        lookup["name_ticker_map"] = ""
        lookup["ticker_map"] = ""
        lookup["sic_ticker_map"] = pd.NA

    lookup["name_final"] = coalesce_nonblank(
        lookup["name"], lookup["name_crosswalk"], lookup["name_ticker_map"]
    )
    lookup["ticker_final"] = coalesce_nonblank(
        lookup["ticker"], lookup["ticker_comp"], lookup["ticker_map"]
    )
    lookup["gvkey_final"] = coalesce_nonblank(lookup["gvkey"], lookup["gvkey_crosswalk"])
    lookup["sic_final"] = coalesce_nonblank(
        lookup["sic"], lookup["sic_crosswalk"], lookup["sic_ticker_map"]
    )

    lookup["name_source"] = pd.Series([""] * len(lookup), index=lookup.index, dtype="object")
    lookup.loc[lookup["name"].fillna("").astype(str).str.strip() != "", "name_source"] = "base"
    lookup.loc[
        (lookup["name_source"] == "")
        & (lookup["name_crosswalk"].fillna("").astype(str).str.strip() != ""),
        "name_source",
    ] = "crosswalk"
    lookup.loc[
        (lookup["name_source"] == "")
        & (lookup["name_ticker_map"].fillna("").astype(str).str.strip() != ""),
        "name_source",
    ] = "ticker_map"

    out = pd.DataFrame(
        {
            "cik": lookup["cik"],
            "name": lookup["name_final"].fillna("").astype(str).str.strip(),
            "name_clean": lookup["name_final"].apply(clean_company_name),
            "ticker": lookup["ticker_final"].fillna("").astype(str).str.strip(),
            "gvkey": lookup["gvkey_final"].fillna("").astype(str).str.strip(),
            "sic": lookup["sic_final"],
            "name_source": lookup["name_source"].replace("", pd.NA),
        }
    )

    out = out[(out["cik"] != "") | (out["name_clean"] != "")].copy()
    out = out[out["name_clean"] != ""].copy()
    with_cik = (
        out[out["cik"] != ""]
        .sort_values(["cik", "name"])
        .drop_duplicates(subset=["cik"], keep="first")
    )
    without_cik = (
        out[out["cik"] == ""]
        .sort_values(["name_clean", "name"])
        .drop_duplicates(subset=["name_clean"], keep="first")
    )
    out = pd.concat([with_cik, without_cik], ignore_index=True)
    out.reset_index(drop=True, inplace=True)

    alias_frames = []
    for label, col in [
        ("base_name", "name"),
        ("crosswalk_name", "name_crosswalk"),
        ("ticker_map_name", "name_ticker_map"),
    ]:
        if col in lookup.columns:
            alias = pd.DataFrame(
                {"cik": lookup["cik"], "alias": lookup[col], "alias_source": label}
            )
            alias_frames.append(alias)

    if alias_frames:
        aliases = pd.concat(alias_frames, ignore_index=True)
        aliases["alias"] = aliases["alias"].fillna("").astype(str).str.strip()
        aliases["alias_clean"] = aliases["alias"].apply(clean_company_name)
        aliases = aliases[aliases["alias_clean"] != ""]
        aliases = aliases.merge(out[["cik", "name", "name_clean"]], on="cik", how="inner")
        aliases = aliases[aliases["alias_clean"] != aliases["name_clean"]]
        aliases = aliases[
            ["cik", "name", "alias", "alias_clean", "alias_source"]
        ].drop_duplicates()
    else:
        aliases = pd.DataFrame(columns=["cik", "name", "alias", "alias_clean", "alias_source"])

    return out, aliases


def main():
    ap = argparse.ArgumentParser(description="Build a normalized company lookup for patents work.")
    ap.add_argument("--company-list", default=SRC, help="Base company list / universe CSV.")
    ap.add_argument(
        "--crosswalk",
        default="",
        help="Optional WRDS crosswalk CSV to enrich gvkey/sic/name by CIK.",
    )
    ap.add_argument(
        "--ticker-map",
        default="",
        help="Optional CIK->ticker/name CSV (for example data/external/cik_ticker_list.csv).",
    )
    ap.add_argument("--out-main", default=OUT_MAIN, help="Lookup CSV output path.")
    ap.add_argument("--out-aliases", default=OUT_ALIASES, help="Alias CSV output path.")
    args = ap.parse_args()

    try:
        base, input_aliases = load_company_source(args.company_list)
    except Exception as exc:
        print(f"[x] {exc}", file=sys.stderr)
        sys.exit(1)

    crosswalk = (
        pd.read_csv(args.crosswalk) if args.crosswalk and os.path.exists(args.crosswalk) else None
    )
    ticker_map = (
        pd.read_csv(args.ticker_map)
        if args.ticker_map and os.path.exists(args.ticker_map)
        else None
    )
    lookup, derived_aliases = build_lookup(base, crosswalk, ticker_map)

    os.makedirs(os.path.dirname(args.out_main), exist_ok=True)
    lookup.to_csv(args.out_main, index=False)
    print(f"[✓] Saved lookup to: {args.out_main}")
    print(f"[✓] Companies in lookup: {len(lookup)}")
    n_blank_ticker = lookup["ticker"].fillna("").astype(str).str.strip().eq("").sum()
    if n_blank_ticker:
        print(f"[!] {n_blank_ticker} companies still missing ticker after enrichment.")

    all_aliases = pd.concat([input_aliases, derived_aliases], ignore_index=True, sort=False)
    if not all_aliases.empty:
        all_aliases["alias"] = all_aliases["alias"].fillna("").astype(str).str.strip()
        all_aliases["alias_clean"] = all_aliases["alias"].apply(clean_company_name)
        all_aliases = all_aliases[all_aliases["alias_clean"] != ""]
        all_aliases = all_aliases.drop(columns=["name", "name_clean"], errors="ignore")
        all_aliases = all_aliases.merge(
            lookup[["cik", "name", "name_clean"]], on="cik", how="inner"
        )
        all_aliases = all_aliases[all_aliases["alias_clean"] != all_aliases["name_clean"]]
        all_aliases = all_aliases[
            ["cik", "name", "alias", "alias_clean", "alias_source"]
        ].drop_duplicates()
        if not all_aliases.empty:
            all_aliases.to_csv(args.out_aliases, index=False)
            print(f"[✓] Saved aliases to: {args.out_aliases}")

    print("\nSample:")
    print(lookup.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
