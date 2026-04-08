from __future__ import annotations

from semantic_ai_washing.patents.pregrant_sources import resolve_pregrant_patentsview_layout


def test_resolve_pregrant_patentsview_layout(tmp_path) -> None:
    for name in [
        "pg_published_application.tsv",
        "pg_published_application_abstract.tsv",
        "pg_assignee_disambiguated.tsv",
        "pg_granted_pgpubs_crosswalk.tsv",
    ]:
        (tmp_path / name).write_text("stub\n", encoding="utf-8")

    layout = resolve_pregrant_patentsview_layout(tmp_path)

    assert layout.published_application.name == "pg_published_application.tsv"
    assert layout.abstract.name == "pg_published_application_abstract.tsv"
    assert layout.assignee.name == "pg_assignee_disambiguated.tsv"
    assert layout.crosswalk.name == "pg_granted_pgpubs_crosswalk.tsv"
    assert layout.applicant is None
