"""Build a deterministic filing manifest for the bounded 2024 sentence-table pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.data.index_sec_filings import ACTIVE_SOURCE_WINDOW_ID
from semantic_ai_washing.labeling.ff12_mapping import FF12Bucket, map_sic_to_ff12

DEFAULT_INDEX = "data/metadata/available_filings_index.csv"
DEFAULT_CONTROLS = "data/interim/controls/controls_by_firm_year.csv"
DEFAULT_CROSSWALK = "data/externals/crosswalks/cik_gvkey.csv"
DEFAULT_OUTPUT = "data/manifests/filings/pilot_2024_10k_v1.csv"
DEFAULT_REPORT = "reports/data/pilot_2024_manifest_summary.json"
DEFAULT_MANIFEST_ID = "pilot_2024_10k_v1"
REQUIRED_QUARTERS = (1, 2, 3, 4)

OUTPUT_COLUMNS = [
    "manifest_id",
    "manifest_row_id",
    "sampling_seed",
    "selection_reason",
    "source_window_id",
    "cik",
    "year",
    "quarter",
    "form",
    "filename",
    "path",
    "sic",
    "ff12_code",
    "ff12_name",
    "industry_metadata_source",
]


def normalize_cik(value: Any) -> str:
    """Normalize a CIK for deterministic joins."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    text = text.lstrip("0")
    return text or "0"


def compute_manifest_row_id(manifest_id: str, path: str) -> str:
    payload = f"{manifest_id}|{path}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _load_controls(path: str, year: int) -> dict[tuple[str, int], str]:
    frame = pd.read_csv(
        path,
        usecols=lambda column: column.lower() in {"cik", "year", "fyear", "sic", "siccd"},
    )
    if frame.empty:
        return {}
    year_column = "year" if "year" in frame.columns else "fyear"
    sic_column = "sic" if "sic" in frame.columns else "siccd"
    frame["cik_norm"] = frame["cik"].map(normalize_cik)
    frame[year_column] = frame[year_column].astype("Int64")
    frame = frame[frame[year_column] == year].copy()
    frame[sic_column] = frame[sic_column].fillna("").astype(str)
    return {
        (row.cik_norm, int(getattr(row, year_column))): str(getattr(row, sic_column)).strip()
        for row in frame.itertuples(index=False)
        if row.cik_norm
    }


def _load_crosswalk(path: str) -> dict[str, str]:
    frame = pd.read_csv(path, usecols=lambda column: column.lower() in {"cik", "sic", "siccd"})
    if frame.empty:
        return {}
    sic_column = "sic" if "sic" in frame.columns else "siccd"
    frame["cik_norm"] = frame["cik"].map(normalize_cik)
    frame[sic_column] = frame[sic_column].fillna("").astype(str)
    return {
        row.cik_norm: str(getattr(row, sic_column)).strip()
        for row in frame.itertuples(index=False)
        if row.cik_norm
    }


def _industry_fields(
    cik: str,
    year: int,
    controls_map: dict[tuple[str, int], str],
    crosswalk_map: dict[str, str],
) -> tuple[str, FF12Bucket, str]:
    cik_norm = normalize_cik(cik)
    sic = controls_map.get((cik_norm, year), "")
    source = "controls_by_firm_year"
    if not sic:
        sic = crosswalk_map.get(cik_norm, "")
        source = "cik_gvkey" if sic else "unknown"
    bucket = map_sic_to_ff12(sic)
    return str(sic).strip(), bucket, source


def _prepare_candidates(
    index_path: str,
    year: int,
    form: str,
    controls_path: str,
    crosswalk_path: str,
) -> pd.DataFrame:
    index_frame = pd.read_csv(
        index_path, dtype={"cik": str, "filename": str, "path": str, "form": str}
    )
    if index_frame.empty:
        raise ValueError(f"No rows found in filings index: {index_path}")

    filtered = index_frame[
        (index_frame["source_window_id"] == ACTIVE_SOURCE_WINDOW_ID)
        & (index_frame["year"].astype(int) == int(year))
        & (index_frame["form"].astype(str).str.upper() == form.upper())
    ].copy()
    if filtered.empty:
        raise ValueError(
            f"No eligible filings found for source_window={ACTIVE_SOURCE_WINDOW_ID}, year={year}, form={form}."
        )

    filtered["quarter"] = filtered["quarter"].astype(int)
    present_quarters = sorted(filtered["quarter"].unique().tolist())
    if present_quarters != list(REQUIRED_QUARTERS):
        raise ValueError(
            f"Expected quarter coverage {list(REQUIRED_QUARTERS)} but found {present_quarters}."
        )

    controls_map = _load_controls(controls_path, year=year)
    crosswalk_map = _load_crosswalk(crosswalk_path)

    sics: list[str] = []
    ff12_codes: list[int] = []
    ff12_names: list[str] = []
    metadata_sources: list[str] = []

    for row in filtered.itertuples(index=False):
        sic, bucket, source = _industry_fields(
            cik=str(row.cik),
            year=int(row.year),
            controls_map=controls_map,
            crosswalk_map=crosswalk_map,
        )
        sics.append(sic)
        ff12_codes.append(bucket.code)
        ff12_names.append(bucket.name)
        metadata_sources.append(source)

    filtered["cik"] = filtered["cik"].map(normalize_cik)
    filtered["sic"] = sics
    filtered["ff12_code"] = ff12_codes
    filtered["ff12_name"] = ff12_names
    filtered["industry_metadata_source"] = metadata_sources
    filtered["industry_known"] = filtered["industry_metadata_source"] != "unknown"
    filtered["ff12_sort"] = filtered["ff12_code"].astype(int)
    filtered.sort_values(
        by=["quarter", "ff12_sort", "cik", "filename"],
        ascending=[True, True, True, True],
        inplace=True,
    )
    filtered.reset_index(drop=True, inplace=True)
    return filtered


def _quarter_selection(frame: pd.DataFrame, quota: int) -> pd.DataFrame:
    if len(frame) < quota:
        quarter = int(frame["quarter"].iloc[0]) if not frame.empty else -1
        raise ValueError(
            f"Quarter {quarter} has {len(frame)} eligible filings; required quota is {quota}."
        )

    working = frame.copy()
    selected_indices: list[int] = []
    grouped = {
        int(bucket): group.index.tolist()
        for bucket, group in working[working["industry_known"]].groupby("ff12_code", sort=True)
    }

    while len(selected_indices) < quota:
        picked_in_round = False
        for bucket in sorted(grouped):
            indices = grouped[bucket]
            while indices and indices[0] in selected_indices:
                indices.pop(0)
            if not indices:
                continue
            selected_indices.append(indices.pop(0))
            picked_in_round = True
            if len(selected_indices) >= quota:
                break
        if not picked_in_round:
            break

    round_robin = working.loc[selected_indices].copy()
    if not round_robin.empty:
        round_robin["selection_reason"] = "quarter_ff12_round_robin"

    remaining = working.drop(index=selected_indices).copy()
    remaining.sort_values(
        by=["industry_known", "cik", "filename"],
        ascending=[False, True, True],
        inplace=True,
    )
    fill_needed = quota - len(round_robin)
    fill = remaining.head(fill_needed).copy()
    if not fill.empty:
        fill["selection_reason"] = "quarter_fill"

    selected = pd.concat([round_robin, fill], ignore_index=True)
    if len(selected) != quota:
        quarter = int(frame["quarter"].iloc[0])
        raise ValueError(f"Quarter {quarter} produced {len(selected)} rows; expected {quota}.")
    return selected


def build_manifest(
    index_path: str = DEFAULT_INDEX,
    year: int = 2024,
    form: str = "10-K",
    target_size: int = 240,
    quarter_quota: int = 60,
    controls_path: str = DEFAULT_CONTROLS,
    crosswalk_path: str = DEFAULT_CROSSWALK,
    manifest_id: str = DEFAULT_MANIFEST_ID,
    seed: int = 20260305,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if target_size != quarter_quota * len(REQUIRED_QUARTERS):
        raise ValueError(
            f"target_size ({target_size}) must equal quarter_quota * 4 ({quarter_quota * len(REQUIRED_QUARTERS)})."
        )

    candidates = _prepare_candidates(
        index_path=index_path,
        year=year,
        form=form,
        controls_path=controls_path,
        crosswalk_path=crosswalk_path,
    )

    selected_frames = [
        _quarter_selection(
            candidates[candidates["quarter"] == quarter].copy(), quota=quarter_quota
        )
        for quarter in REQUIRED_QUARTERS
    ]
    manifest = pd.concat(selected_frames, ignore_index=True)
    manifest["manifest_id"] = manifest_id
    manifest["sampling_seed"] = int(seed)
    manifest["manifest_row_id"] = manifest["path"].map(
        lambda value: compute_manifest_row_id(manifest_id, value)
    )

    manifest.sort_values(
        by=["quarter", "selection_reason", "cik", "filename"],
        ascending=[True, True, True, True],
        inplace=True,
    )
    manifest = manifest[OUTPUT_COLUMNS].reset_index(drop=True)

    summary = {
        "manifest_id": manifest_id,
        "seed": int(seed),
        "target_size": int(target_size),
        "quarter_quota": int(quarter_quota),
        "total_eligible_candidate_count": int(len(candidates)),
        "quarter_candidate_counts": {
            str(int(quarter)): int(count)
            for quarter, count in candidates["quarter"].value_counts().sort_index().items()
        },
        "selected_quarter_counts": {
            str(int(quarter)): int(count)
            for quarter, count in manifest["quarter"].value_counts().sort_index().items()
        },
        "selected_ff12_counts": {
            str(bucket): int(count)
            for bucket, count in manifest["ff12_code"].value_counts().sort_index().items()
        },
        "industry_metadata_coverage_counts": {
            "eligible": {
                source: int(count)
                for source, count in candidates["industry_metadata_source"]
                .value_counts()
                .sort_index()
                .items()
            },
            "selected": {
                source: int(count)
                for source, count in manifest["industry_metadata_source"]
                .value_counts()
                .sort_index()
                .items()
            },
        },
        "quota_satisfied": bool(
            len(manifest) == target_size
            and all(
                int(manifest[manifest["quarter"] == quarter].shape[0]) == quarter_quota
                for quarter in REQUIRED_QUARTERS
            )
        ),
    }
    return manifest, summary


def write_manifest(manifest: pd.DataFrame, output_path: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output, index=False)


def write_report(payload: dict[str, Any], output_path: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default=DEFAULT_INDEX)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--form", default="10-K")
    parser.add_argument("--target-size", type=int, default=240)
    parser.add_argument("--quarter-quota", type=int, default=60)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    parser.add_argument("--manifest-id", default=DEFAULT_MANIFEST_ID)
    parser.add_argument("--seed", type=int, default=20260305)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest, summary = build_manifest(
        index_path=args.index,
        year=args.year,
        form=args.form,
        target_size=args.target_size,
        quarter_quota=args.quarter_quota,
        controls_path=args.controls,
        crosswalk_path=args.crosswalk,
        manifest_id=args.manifest_id,
        seed=args.seed,
    )
    write_manifest(manifest, args.output)
    write_report(summary, args.report)
    print(f"[i] Wrote filing manifest: {args.output}")
    print(f"[i] Wrote manifest summary: {args.report}")
    print(f"[i] Manifest rows: {len(manifest):,}")


if __name__ == "__main__":
    main()
