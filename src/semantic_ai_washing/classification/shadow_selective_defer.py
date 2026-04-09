"""Helpers for scalable shadow selective-defer classification workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ShadowDeferPolicy:
    name: str
    description: str
    low_confidence_threshold: float | None = None
    low_as_margin_threshold: float | None = None
    require_component_disagreement: bool = False


POLICIES: dict[str, ShadowDeferPolicy] = {
    "conf49": ShadowDeferPolicy(
        name="conf49",
        description="Defer rows with local top-score confidence below 0.49.",
        low_confidence_threshold=0.49,
    ),
    "conf54": ShadowDeferPolicy(
        name="conf54",
        description="Defer rows with local top-score confidence below 0.54.",
        low_confidence_threshold=0.54,
    ),
    "conf_or_margin": ShadowDeferPolicy(
        name="conf_or_margin",
        description="Defer rows with low confidence or narrow A/S margin.",
        low_confidence_threshold=0.60,
        low_as_margin_threshold=0.15,
    ),
    "conf_or_margin_or_disagreement": ShadowDeferPolicy(
        name="conf_or_margin_or_disagreement",
        description="Defer rows with low confidence, narrow A/S margin, or local component disagreement.",
        low_confidence_threshold=0.60,
        low_as_margin_threshold=0.15,
        require_component_disagreement=True,
    ),
}


def resolve_policy(policy_name: str) -> ShadowDeferPolicy:
    try:
        return POLICIES[str(policy_name).strip()]
    except KeyError as exc:
        available = ", ".join(sorted(POLICIES))
        raise ValueError(f"Unknown shadow selective-defer policy {policy_name!r}. Available: {available}.") from exc


def should_defer_row(row: pd.Series, policy: ShadowDeferPolicy) -> bool:
    triggers: list[bool] = []
    if policy.low_confidence_threshold is not None:
        triggers.append(float(row["local_confidence"]) < policy.low_confidence_threshold)
    if policy.low_as_margin_threshold is not None:
        if str(row.get("local_label", row.get("predicted_label", ""))) == "Irrelevant":
            triggers.append(False)
        else:
            triggers.append(float(row["conditional_as_margin"]) < policy.low_as_margin_threshold)
    if policy.require_component_disagreement:
        triggers.append(bool(row.get("binary_logreg_relevance_disagreement", False)))
    return any(triggers)


def load_classified_rows(
    *,
    input_root: str | Path,
    years: list[int],
    model_id: str,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in years:
        path = (
            Path(input_root)
            / f"year={int(year)}"
            / f"model={model_id}"
            / "classified_sentences.parquet"
        )
        if not path.exists():
            raise FileNotFoundError(f"Missing classified sentences for year={year}: {path}")
        frame = pd.read_parquet(path)
        frame["source_year"] = pd.to_numeric(frame["source_year"], errors="coerce").astype(int)
        frames.append(frame)
    if not frames:
        raise ValueError("No classified sentence tables were loaded.")
    return pd.concat(frames, ignore_index=True)


def build_deferred_mask(frame: pd.DataFrame, policy: ShadowDeferPolicy) -> pd.Series:
    required = {"local_confidence", "conditional_as_margin"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Classified frame is missing required defer columns: {missing}")
    return frame.apply(lambda row: should_defer_row(row, policy), axis=1).astype(bool)


def summarize_deferred_rows(frame: pd.DataFrame, deferred_mask: pd.Series) -> dict[str, Any]:
    scoped = frame.copy()
    scoped["deferred"] = deferred_mask.astype(bool)
    by_year = (
        scoped.groupby("source_year", dropna=False)
        .agg(
            rows_total=("sentence_id", "count"),
            deferred_rows=("deferred", "sum"),
        )
        .reset_index()
        .sort_values("source_year")
    )
    by_year["deferred_rate"] = by_year["deferred_rows"] / by_year["rows_total"]
    by_label = (
        scoped.groupby("predicted_label", dropna=False)
        .agg(
            rows_total=("sentence_id", "count"),
            deferred_rows=("deferred", "sum"),
        )
        .reset_index()
        .sort_values("predicted_label")
    )
    by_label["deferred_rate"] = by_label["deferred_rows"] / by_label["rows_total"]
    return {
        "rows_total": int(len(scoped)),
        "deferred_rows": int(deferred_mask.sum()),
        "deferred_rate": float(deferred_mask.mean()) if len(scoped) else 0.0,
        "by_year": by_year,
        "by_label": by_label,
    }
