"""PatentsView source resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PatentsViewLayout:
    """Resolved source file layout for one PatentsView drop."""

    root: Path
    family: str
    assignee_path: Path
    patent_path: Path
    abstract_path: Path
    application_path: Path | None

    @property
    def assignee(self) -> Path:
        return self.assignee_path

    @property
    def patent(self) -> Path:
        return self.patent_path

    @property
    def abstract(self) -> Path:
        return self.abstract_path

    @property
    def application(self) -> Path | None:
        return self.application_path


def _choose_existing(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def resolve_patentsview_layout(
    data_root: str | Path,
    *,
    require_application: bool = False,
) -> PatentsViewLayout:
    """Resolve a coherent PatentsView file family under ``data_root``."""

    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"PatentsView root does not exist: {root}")

    has_modern = any(
        (root / name).exists()
        for name in (
            "g_patent.tsv",
            "g_patent_abstract.tsv",
            "g_assignee_disambiguated.tsv",
            "g_application.tsv",
        )
    )
    family = "modern" if has_modern else "legacy"

    if family == "modern":
        assignee = root / "g_assignee_disambiguated.tsv"
        patent = root / "g_patent.tsv"
        abstract = root / "g_patent_abstract.tsv"
        application = _choose_existing(root, ("g_application.tsv", "application.tsv"))
    else:
        assignee = root / "patent_assignee.tsv"
        patent = root / "patent.tsv"
        abstract = root / "patent_abstract.tsv"
        application = _choose_existing(root, ("application.tsv", "g_application.tsv"))

    missing = [str(path.name) for path in (assignee, patent, abstract) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            f"PatentsView {family} family is incomplete under {root}: missing {missing}"
        )
    if require_application and application is None:
        raise FileNotFoundError(
            "Application timing requested but no application table was found under "
            f"{root}. Expected one of: g_application.tsv, application.tsv"
        )

    return PatentsViewLayout(
        root=root,
        family=family,
        assignee_path=assignee,
        patent_path=patent,
        abstract_path=abstract,
        application_path=application,
    )


def resolve_patentsview_paths(
    data_root: str | Path,
    *,
    require_application: bool = False,
) -> PatentsViewLayout:
    """Compatibility wrapper for older call sites."""

    return resolve_patentsview_layout(
        data_root,
        require_application=require_application,
    )


def load_application_filing_date_lookup(
    application_path: str | Path,
    patent_ids: set[str],
    *,
    chunksize: int = 250000,
) -> dict[str, str]:
    """Load ``patent_id -> filing_date`` for the requested patent ids."""

    if not patent_ids:
        return {}

    lookup: dict[str, str] = {}
    for chunk in pd.read_csv(
        application_path,
        sep="\t",
        usecols=["patent_id", "filing_date"],
        dtype={"patent_id": str},
        chunksize=chunksize,
    ):
        chunk = chunk[chunk["patent_id"].isin(patent_ids)]
        if chunk.empty:
            continue
        chunk = chunk.dropna(subset=["filing_date"]).copy()
        chunk["filing_date"] = chunk["filing_date"].astype(str).str.strip()
        chunk = chunk[chunk["filing_date"] != ""]
        for patent_id, filing_date in chunk[["patent_id", "filing_date"]].itertuples(index=False):
            lookup[str(patent_id)] = str(filing_date)
    return lookup


def attach_patent_timing(
    frame,
    *,
    timing_field: str,
    filing_date_lookup: dict[str, str] | None = None,
):
    """Attach filing/grant timing columns to a patent frame."""

    working = frame.copy()
    lookup = filing_date_lookup or {}
    working["filing_date"] = working["patent_id"].map(lookup).fillna("")
    if timing_field == "application":
        working["timing_date"] = working["filing_date"]
    else:
        working["timing_date"] = working["patent_date"]
    working["timing_field"] = timing_field
    return working
