from __future__ import annotations

from semantic_ai_washing.patents.run_patent_fuzzy_sensitivity_sample import (
    TermRecord,
    fuzzy_best_match,
)


def test_fuzzy_best_match_accepts_clear_high_score() -> None:
    catalog = [
        TermRecord(
            term="qualcomm",
            cik="0000804328",
            name="QUALCOMM",
            tokens=frozenset({"qualcomm"}),
        ),
        TermRecord(
            term="snowflake",
            cik="0001640147",
            name="SNOWFLAKE",
            tokens=frozenset({"snowflake"}),
        ),
    ]

    match, score, second = fuzzy_best_match(
        "qualcomm technologies",
        catalog=catalog,
        threshold=0.60,
        min_gap=0.03,
    )

    assert match is not None
    assert match.term == "qualcomm"
    assert score >= 0.60
    assert second is None or score - second >= 0.03


def test_fuzzy_best_match_rejects_tight_ambiguity() -> None:
    catalog = [
        TermRecord(
            term="blue owl capital",
            cik="1",
            name="Blue Owl Capital",
            tokens=frozenset({"blue", "owl", "capital"}),
        ),
        TermRecord(
            term="blue owl",
            cik="2",
            name="Blue Owl",
            tokens=frozenset({"blue", "owl"}),
        ),
    ]

    match, _, _ = fuzzy_best_match(
        "blue owl capitals",
        catalog=catalog,
        threshold=0.70,
        min_gap=0.03,
    )

    assert match is None
