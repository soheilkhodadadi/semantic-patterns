"""Build filing-level AI measures from yearly classified-sentence parquet outputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import pandas as pd

DEFAULT_INPUT_ROOT = "data/processed/classifications_shadow_hybrid_api_a_conf49_v1"
DEFAULT_MODEL_ID = "layered_binary_relevance_logreg_as_shadow_api_a_conf49_v1"
DEFAULT_IDENTITY_PANEL = (
    "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_SPINE_OUTPUT = "data/interim/market/filing_event_spine_hybrid_api_a_conf49_v1.csv"
DEFAULT_MEASURES_OUTPUT = "data/interim/market/filing_ai_measures_hybrid_api_a_conf49_v1.csv"
DEFAULT_REPORT = "reports/analysis/filing_ai_measures_hybrid_api_a_conf49_v1.json"
DEFAULT_FORMS = ("10-K", "10-K-A")
CHATGPT_RELEASE_DATE = "20221130"

SOURCE_FILE_PATTERN = re.compile(
    r"(?P<filing_date>\d{8})_"
    r"(?P<form>[^_]+)_"
    r"edgar_data_"
    r"(?P<cik>\d+)_"
    r"(?P<accession>[^.]+)\.txt$"
)

SPINE_COLUMNS = [
    "filing_id",
    "source_filename",
    "source_path",
    "filing_date",
    "filing_year",
    "form_type",
    "cik",
    "accession_number",
    "gvkey",
    "ticker_comp",
    "issuer_name",
    "sic",
]

MEASURE_COLUMNS = [
    "filing_id",
    "source_filename",
    "source_path",
    "filing_date",
    "filing_year",
    "form_type",
    "cik",
    "gvkey",
    "sentence_count",
    "n_actionable",
    "n_speculative",
    "n_irrelevant",
    "n_other",
    "n_ai_total",
    "share_actionable",
    "share_speculative",
    "share_irrelevant",
    "any_actionable",
    "any_speculative",
    "any_irrelevant",
    "post_chatgpt",
    "api_a_sentence_count",
]

LABEL_TO_COUNT = {
    "Actionable": "n_actionable",
    "Speculative": "n_speculative",
    "Irrelevant": "n_irrelevant",
}


def normalize_cik(value: Any) -> str:
    digits = "".join(character for character in str(value or "") if character.isdigit())
    return digits.zfill(10) if digits else ""


def compute_filing_id(source_file: str) -> str:
    return hashlib.sha1(source_file.encode("utf-8")).hexdigest()[:16]


def parse_source_file(source_file: str) -> dict[str, str] | None:
    match = SOURCE_FILE_PATTERN.search(Path(source_file).name)
    if not match:
        return None
    return {
        "source_filename": Path(source_file).name,
        "source_path": source_file,
        "filing_date": match.group("filing_date"),
        "filing_year": match.group("filing_date")[:4],
        "form_type": match.group("form"),
        "cik": normalize_cik(match.group("cik")),
        "accession_number": match.group("accession"),
    }


def parse_forms(forms: str) -> set[str]:
    return {part.strip().upper() for part in forms.split(",") if part.strip()}


def load_identity_lookup(path: str | Path) -> dict[tuple[str, int], dict[str, str]]:
    resolved = Path(path)
    if not resolved.exists():
        return {}

    panel = pd.read_parquet(resolved)
    required = {"cik", "year"}
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"Identity panel missing required columns: {sorted(missing)}")

    panel = panel.copy()
    panel["cik_norm"] = panel["cik"].map(normalize_cik)
    panel["year_int"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")

    lookup: dict[tuple[str, int], dict[str, str]] = {}
    for row in panel.dropna(subset=["year_int"]).itertuples(index=False):
        cik = str(getattr(row, "cik_norm", "") or "")
        year = int(getattr(row, "year_int"))
        if not cik or (cik, year) in lookup:
            continue
        lookup[(cik, year)] = {
            "gvkey": str(getattr(row, "gvkey", "") or "").strip(),
            "ticker_comp": str(getattr(row, "ticker", "") or "").strip(),
            "issuer_name": str(getattr(row, "name", "") or "").strip(),
            "sic": str(getattr(row, "sic", "") or "").strip(),
        }
    return lookup


def iter_year_paths(input_root: str | Path, years: list[int], model_id: str) -> list[Path]:
    root = Path(input_root)
    paths = []
    for year in years:
        path = root / f"year={year}" / f"model={model_id}" / "classified_sentences.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Missing classified sentences for year={year}: {path}")
        paths.append(path)
    return paths


def _safe_share(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator.where(denominator.ne(0))).fillna(0.0)


def build_outputs(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    years = [int(year) for year in args.years]
    allowed_forms = parse_forms(args.forms)
    identity = load_identity_lookup(args.identity_panel)

    frames: list[pd.DataFrame] = []
    for path in iter_year_paths(args.input_root, years, args.model_id):
        frame = pd.read_parquet(
            path,
            columns=[
                "source_file",
                "source_form",
                "source_cik",
                "source_year",
                "predicted_label",
                "prediction_source",
            ],
        )
        frames.append(frame)
    sentences = pd.concat(frames, ignore_index=True)
    sentences["source_file"] = sentences["source_file"].fillna("").astype(str)
    sentences["source_form_norm"] = sentences["source_form"].fillna("").astype(str).str.upper()
    if allowed_forms:
        sentences = sentences[sentences["source_form_norm"].isin(allowed_forms)].copy()

    parsed = sentences["source_file"].drop_duplicates().map(parse_source_file)
    metadata = pd.DataFrame([record for record in parsed if record is not None])
    if metadata.empty:
        raise ValueError("No filing metadata could be parsed from source_file values.")

    metadata["filing_id"] = metadata["source_path"].map(compute_filing_id)
    metadata["filing_year_int"] = pd.to_numeric(metadata["filing_year"], errors="coerce").astype(
        "Int64"
    )

    identity_rows = []
    identity_hits = 0
    for row in metadata.itertuples(index=False):
        lookup = identity.get((row.cik, int(row.filing_year_int)), {})
        if lookup:
            identity_hits += 1
        identity_rows.append(lookup)
    identity_df = pd.DataFrame(identity_rows).fillna("")
    metadata = pd.concat(
        [metadata.reset_index(drop=True), identity_df.reset_index(drop=True)], axis=1
    )

    counts = (
        sentences.groupby(["source_file", "predicted_label"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    counts["sentence_count"] = counts.drop(columns=["source_file"]).sum(axis=1)
    for label, column in LABEL_TO_COUNT.items():
        counts[column] = counts[label] if label in counts.columns else 0
    counts["n_ai_total"] = counts[list(LABEL_TO_COUNT.values())].sum(axis=1)
    counts["n_other"] = counts["sentence_count"] - counts["n_ai_total"]

    api_counts = (
        sentences[sentences["prediction_source"].fillna("").astype(str).eq("api_a")]
        .groupby("source_file")
        .size()
        .rename("api_a_sentence_count")
        .reset_index()
    )
    counts = counts.merge(api_counts, on="source_file", how="left")
    counts["api_a_sentence_count"] = counts["api_a_sentence_count"].fillna(0).astype(int)

    filing = metadata.merge(counts, left_on="source_path", right_on="source_file", how="left")
    for column in [
        "n_actionable",
        "n_speculative",
        "n_irrelevant",
        "n_other",
        "n_ai_total",
        "sentence_count",
    ]:
        filing[column] = pd.to_numeric(filing[column], errors="coerce").fillna(0).astype(int)

    filing["share_actionable"] = _safe_share(filing["n_actionable"], filing["n_ai_total"]).round(6)
    filing["share_speculative"] = _safe_share(filing["n_speculative"], filing["n_ai_total"]).round(
        6
    )
    filing["share_irrelevant"] = _safe_share(filing["n_irrelevant"], filing["n_ai_total"]).round(6)
    filing["any_actionable"] = filing["n_actionable"].gt(0).astype(int)
    filing["any_speculative"] = filing["n_speculative"].gt(0).astype(int)
    filing["any_irrelevant"] = filing["n_irrelevant"].gt(0).astype(int)
    filing["post_chatgpt"] = filing["filing_date"].ge(CHATGPT_RELEASE_DATE).astype(int)

    spine = (
        filing[SPINE_COLUMNS]
        .sort_values(["filing_date", "source_filename"])
        .reset_index(drop=True)
    )
    measures = (
        filing[MEASURE_COLUMNS]
        .sort_values(["filing_date", "source_filename"])
        .reset_index(drop=True)
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_root": str(Path(args.input_root).resolve()),
        "model_id": args.model_id,
        "identity_panel": str(Path(args.identity_panel).resolve()),
        "years": years,
        "forms": sorted(allowed_forms) if allowed_forms else "all",
        "row_count": int(len(measures)),
        "sentence_count": int(measures["sentence_count"].sum()),
        "n_actionable": int(measures["n_actionable"].sum()),
        "n_speculative": int(measures["n_speculative"].sum()),
        "n_irrelevant": int(measures["n_irrelevant"].sum()),
        "api_a_sentence_count": int(measures["api_a_sentence_count"].sum()),
        "filings_with_api_a_count": int(measures["api_a_sentence_count"].gt(0).sum()),
        "date_min": str(measures["filing_date"].min()) if not measures.empty else "",
        "date_max": str(measures["filing_date"].max()) if not measures.empty else "",
        "year_counts": {
            str(key): int(value)
            for key, value in measures["filing_year"].value_counts().sort_index().items()
        },
        "form_counts": {
            str(key): int(value)
            for key, value in measures["form_type"].value_counts().sort_index().items()
        },
        "unique_cik_count": int(measures["cik"].nunique()),
        "unique_gvkey_count": int(measures["gvkey"].replace("", pd.NA).dropna().nunique()),
        "identity_match_count": identity_hits,
        "identity_match_rate": round(identity_hits / len(metadata), 4) if len(metadata) else 0.0,
    }
    return spine, measures, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--identity-panel", default=DEFAULT_IDENTITY_PANEL)
    parser.add_argument("--years", nargs="+", default=[str(year) for year in range(2016, 2026)])
    parser.add_argument("--forms", default=",".join(DEFAULT_FORMS))
    parser.add_argument("--spine-output", default=DEFAULT_SPINE_OUTPUT)
    parser.add_argument("--measures-output", default=DEFAULT_MEASURES_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spine, measures, report = build_outputs(args)
    spine_path = Path(args.spine_output)
    measures_path = Path(args.measures_output)
    report_path = Path(args.report)
    spine_path.parent.mkdir(parents=True, exist_ok=True)
    measures_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    spine.to_csv(spine_path, index=False)
    measures.to_csv(measures_path, index=False)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
