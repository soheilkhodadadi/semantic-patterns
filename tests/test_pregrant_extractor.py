from __future__ import annotations

import pandas as pd

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

