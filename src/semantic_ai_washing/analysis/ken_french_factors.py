"""Download and parse monthly Ken French factor files from the official data library."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
import io
import json
from pathlib import Path
from urllib.request import urlopen
import zipfile

import pandas as pd

KEN_FRENCH_LIBRARY_ROOT = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french"
FF5_2X3_MONTHLY_URL = (
    f"{KEN_FRENCH_LIBRARY_ROOT}/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip"
)
MOM_MONTHLY_URL = f"{KEN_FRENCH_LIBRARY_ROOT}/ftp/F-F_Momentum_Factor_CSV.zip"
MISSING_SENTINELS = {-99.99, -999.0}


@dataclass(frozen=True)
class FactorBundlePaths:
    root: Path
    raw_dir: Path
    extracted_dir: Path
    parsed_dir: Path
    ff5_zip: Path
    mom_zip: Path
    ff5_text: Path
    mom_text: Path
    ff5_csv: Path
    mom_csv: Path
    merged_csv: Path
    merged_parquet: Path
    manifest: Path


def _bundle_paths(root: Path) -> FactorBundlePaths:
    raw_dir = root / "raw"
    extracted_dir = root / "extracted"
    parsed_dir = root / "parsed"
    return FactorBundlePaths(
        root=root,
        raw_dir=raw_dir,
        extracted_dir=extracted_dir,
        parsed_dir=parsed_dir,
        ff5_zip=raw_dir / "F-F_Research_Data_5_Factors_2x3_CSV.zip",
        mom_zip=raw_dir / "F-F_Momentum_Factor_CSV.zip",
        ff5_text=extracted_dir / "F-F_Research_Data_5_Factors_2x3.csv",
        mom_text=extracted_dir / "F-F_Momentum_Factor.csv",
        ff5_csv=parsed_dir / "ff5_monthly.csv",
        mom_csv=parsed_dir / "momentum_monthly.csv",
        merged_csv=parsed_dir / "ff5_momentum_monthly.csv",
        merged_parquet=parsed_dir / "ff5_momentum_monthly.parquet",
        manifest=parsed_dir / "factor_bundle_manifest.json",
    )


def _ensure_dirs(paths: FactorBundlePaths) -> None:
    for path in [paths.raw_dir, paths.extracted_dir, paths.parsed_dir]:
        path.mkdir(parents=True, exist_ok=True)


def _download_bytes(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def _extract_single_member_text(zip_bytes: bytes) -> tuple[str, str]:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        names = archive.namelist()
        if len(names) != 1:
            raise ValueError(f"Expected exactly one file in archive, found {len(names)}")
        member = names[0]
        text = archive.read(member).decode("latin-1")
    return member, text


def _find_monthly_table_lines(text: str, expected_headers: list[str]) -> list[str]:
    lines = text.splitlines()
    header_idx = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith(","):
            continue
        if all(header in stripped for header in expected_headers):
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError("Could not locate monthly factor table header")

    table_lines = [lines[header_idx]]
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped:
            break
        first_field = stripped.split(",", 1)[0].strip()
        if not (first_field.isdigit() and len(first_field) == 6):
            break
        table_lines.append(line)
    if len(table_lines) <= 1:
        raise ValueError("Monthly factor table did not contain any data rows")
    return table_lines


def _parse_monthly_table(text: str, expected_headers: list[str]) -> pd.DataFrame:
    rows = list(csv.reader(_find_monthly_table_lines(text, expected_headers)))
    header = rows[0]
    if not header or header[0] != "":
        raise ValueError("Unexpected leading column in monthly factor table")
    header[0] = "yyyymm"
    return pd.DataFrame(rows[1:], columns=header)


def _finalize_monthly_frame(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    out = df.rename(columns=rename_map).copy()
    out["yyyymm"] = out["yyyymm"].astype(str).str.strip()
    out = out.loc[out["yyyymm"].str.fullmatch(r"\d{6}")].copy()
    out["month"] = pd.PeriodIndex(pd.to_datetime(out["yyyymm"], format="%Y%m"), freq="M")
    keep = ["month", *rename_map.values()]
    out = out[["month", *rename_map.values()]].copy()
    for column in rename_map.values():
        out[column] = pd.to_numeric(out[column], errors="coerce")
        out[column] = out[column].where(~out[column].isin(MISSING_SENTINELS))
        out[column] = out[column] / 100.0
    return out.sort_values("month").reset_index(drop=True)


def parse_ff5_monthly_text(text: str) -> pd.DataFrame:
    raw = _parse_monthly_table(text, ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"])
    return _finalize_monthly_frame(
        raw,
        {
            "Mkt-RF": "mkt_rf",
            "SMB": "smb",
            "HML": "hml",
            "RMW": "rmw",
            "CMA": "cma",
            "RF": "rf",
        },
    )


def parse_momentum_monthly_text(text: str) -> pd.DataFrame:
    raw = _parse_monthly_table(text, ["Mom"])
    return _finalize_monthly_frame(raw, {"Mom": "mom"})


def stage_ken_french_monthly_factors(
    output_root: str | Path,
    *,
    refresh: bool = False,
) -> tuple[pd.DataFrame, dict[str, object]]:
    root = Path(output_root)
    paths = _bundle_paths(root)
    _ensure_dirs(paths)

    if refresh or not paths.ff5_zip.exists():
        paths.ff5_zip.write_bytes(_download_bytes(FF5_2X3_MONTHLY_URL))
    if refresh or not paths.mom_zip.exists():
        paths.mom_zip.write_bytes(_download_bytes(MOM_MONTHLY_URL))

    ff5_member, ff5_text = _extract_single_member_text(paths.ff5_zip.read_bytes())
    mom_member, mom_text = _extract_single_member_text(paths.mom_zip.read_bytes())
    paths.ff5_text.write_text(ff5_text, encoding="latin-1")
    paths.mom_text.write_text(mom_text, encoding="latin-1")

    ff5 = parse_ff5_monthly_text(ff5_text)
    mom = parse_momentum_monthly_text(mom_text)
    merged = ff5.merge(mom, on="month", how="inner", validate="one_to_one")

    ff5_csv = ff5.copy()
    ff5_csv["month"] = ff5_csv["month"].astype(str)
    ff5_csv.to_csv(paths.ff5_csv, index=False)

    mom_csv = mom.copy()
    mom_csv["month"] = mom_csv["month"].astype(str)
    mom_csv.to_csv(paths.mom_csv, index=False)

    merged_csv = merged.copy()
    merged_csv["month"] = merged_csv["month"].astype(str)
    merged_csv.to_csv(paths.merged_csv, index=False)
    merged.to_parquet(paths.merged_parquet, index=False)

    manifest = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_urls": {
            "ff5_monthly": FF5_2X3_MONTHLY_URL,
            "momentum_monthly": MOM_MONTHLY_URL,
        },
        "raw_members": {
            "ff5": ff5_member,
            "momentum": mom_member,
        },
        "row_count": int(len(merged)),
        "month_min": str(merged["month"].min()),
        "month_max": str(merged["month"].max()),
        "paths": {
            "ff5_zip": str(paths.ff5_zip),
            "momentum_zip": str(paths.mom_zip),
            "ff5_text": str(paths.ff5_text),
            "momentum_text": str(paths.mom_text),
            "ff5_csv": str(paths.ff5_csv),
            "momentum_csv": str(paths.mom_csv),
            "merged_csv": str(paths.merged_csv),
            "merged_parquet": str(paths.merged_parquet),
        },
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return merged, manifest
