from __future__ import annotations

from semantic_ai_washing.patents.patentsview_sources import resolve_patentsview_layout


def test_resolve_patentsview_layout_modern_family_with_application(tmp_path) -> None:
    for name in [
        "g_patent.tsv",
        "g_patent_abstract.tsv",
        "g_assignee_disambiguated.tsv",
        "g_application.tsv",
    ]:
        (tmp_path / name).write_text("stub\n", encoding="utf-8")

    layout = resolve_patentsview_layout(tmp_path, require_application=True)

    assert layout.family == "modern"
    assert layout.patent_path.name == "g_patent.tsv"
    assert layout.abstract_path.name == "g_patent_abstract.tsv"
    assert layout.assignee_path.name == "g_assignee_disambiguated.tsv"
    assert layout.application_path is not None
    assert layout.application_path.name == "g_application.tsv"


def test_resolve_patentsview_layout_legacy_family_without_application(tmp_path) -> None:
    for name in [
        "patent.tsv",
        "patent_abstract.tsv",
        "patent_assignee.tsv",
    ]:
        (tmp_path / name).write_text("stub\n", encoding="utf-8")

    layout = resolve_patentsview_layout(tmp_path)

    assert layout.family == "legacy"
    assert layout.patent_path.name == "patent.tsv"
    assert layout.abstract_path.name == "patent_abstract.tsv"
    assert layout.assignee_path.name == "patent_assignee.tsv"
    assert layout.application_path is None
