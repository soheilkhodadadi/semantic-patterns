"""Pregrant PatentsView source resolution helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PregrantPatentsViewLayout:
    """Resolved source file layout for one pregrant PatentsView drop."""

    root: Path
    published_application_path: Path
    abstract_path: Path
    assignee_path: Path
    crosswalk_path: Path
    applicant_path: Path | None

    @property
    def published_application(self) -> Path:
        return self.published_application_path

    @property
    def abstract(self) -> Path:
        return self.abstract_path

    @property
    def assignee(self) -> Path:
        return self.assignee_path

    @property
    def crosswalk(self) -> Path:
        return self.crosswalk_path

    @property
    def applicant(self) -> Path | None:
        return self.applicant_path


def resolve_pregrant_patentsview_layout(data_root: str | Path) -> PregrantPatentsViewLayout:
    """Resolve the expected pregrant PatentsView table layout under ``data_root``."""

    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"Pregrant PatentsView root does not exist: {root}")

    published_application = root / "pg_published_application.tsv"
    abstract = root / "pg_published_application_abstract.tsv"
    assignee = root / "pg_assignee_disambiguated.tsv"
    crosswalk = root / "pg_granted_pgpubs_crosswalk.tsv"
    applicant = root / "pg_applicant_not_disambiguated.tsv"

    missing = [
        str(path.name)
        for path in (published_application, abstract, assignee, crosswalk)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(
            f"Pregrant PatentsView family is incomplete under {root}: missing {missing}"
        )

    return PregrantPatentsViewLayout(
        root=root,
        published_application_path=published_application,
        abstract_path=abstract,
        assignee_path=assignee,
        crosswalk_path=crosswalk,
        applicant_path=applicant if applicant.exists() else None,
    )
