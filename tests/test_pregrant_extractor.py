from __future__ import annotations

import csv

import pandas as pd

from semantic_ai_washing.patents.extract_filtered_pregrant_applications_lightweight import (
    append_pgpub_matches_from_org_file,
)
from semantic_ai_washing.patents.extract_filtered_pregrant_applications_lightweight import (
    _dedupe_application_matches,
)


def test_dedupe_application_matches_prefers_current_pgpub_and_latest_publication() -> None:
    frame = pd.DataFrame(
        [
            {
                "cik": "1",
                "application_id": "app1",
                "pgpub_id": "pg1",
                "published_date": "2020-01-01",
                "application_abstract": "",
                "current_pgpub_id_flag": "FALSE",
                "current_patent_id_flag": "FALSE",
            },
            {
                "cik": "1",
                "application_id": "app1",
                "pgpub_id": "pg2",
                "published_date": "2021-01-01",
                "application_abstract": "abstract",
                "current_pgpub_id_flag": "TRUE",
                "current_patent_id_flag": "TRUE",
            },
            {
                "cik": "1",
                "application_id": "app2",
                "pgpub_id": "pg3",
                "published_date": "2022-01-01",
                "application_abstract": "abstract",
                "current_pgpub_id_flag": "",
                "current_patent_id_flag": "",
            },
        ]
    )

    result = _dedupe_application_matches(frame).sort_values(["application_id"])

    assert list(result["pgpub_id"]) == ["pg2", "pg3"]


def test_append_pgpub_matches_from_org_file_uses_fallback_only(tmp_path) -> None:
    path = tmp_path / "applicant.tsv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["pgpub_id", "raw_applicant_organization"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerow({"pgpub_id": "pg1", "raw_applicant_organization": "Example Corp."})
        writer.writerow({"pgpub_id": "pg2", "raw_applicant_organization": "Example Corp."})

    matched = {"pg1": [("0000000001", "Example Corp")]}
    rows_added, pgpubs_added = append_pgpub_matches_from_org_file(
        matched,
        path=path,
        org_column="raw_applicant_organization",
        term_index={"example": [("0000000001", "Example Corp")]},
        fallback_only=True,
    )

    assert rows_added == 1
    assert pgpubs_added == 1
    assert matched["pg1"] == [("0000000001", "Example Corp")]
    assert matched["pg2"] == [("0000000001", "Example Corp")]
