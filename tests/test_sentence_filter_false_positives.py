from __future__ import annotations

from semantic_ai_washing.core.sentence_filter import (
    filter_ai_sentences_with_sections,
    is_artifact_only_ai_false_positive,
)


def test_is_artifact_only_ai_false_positive_flags_clause_markers() -> None:
    assert is_artifact_only_ai_false_positive(
        "(ai) Purchase Price has the meaning ascribed to that term in Clause 2.3(a)."
    )
    assert is_artifact_only_ai_false_positive(
        "Executive shall be reimbursed by Telkonet for all ordinary, reasonable, customary ai.1d necessary expenses incurred by him."
    )
    assert not is_artifact_only_ai_false_positive(
        "We use AI technologies to improve our underwriting workflow."
    )
    assert not is_artifact_only_ai_false_positive(
        "Our artificial intelligence platform supports customer service automation."
    )


def test_filter_ai_sentences_with_sections_skips_artifact_only_ai_false_positives() -> None:
    sentences = [
        "(ai) Option Agreement means a written agreement between the Company and a holder.",
        "We use AI technologies across our logistics platform.",
        "Our artificial intelligence platform supports customer service automation.",
        "Executive shall be reimbursed by Telkonet for all ordinary, reasonable, customary ai.1d necessary expenses incurred by him.",
    ]

    tagged = filter_ai_sentences_with_sections(sentences, ["AI", "artificial intelligence"])

    assert [sentence for sentence, _ in tagged] == [
        "We use AI technologies across our logistics platform.",
        "Our artificial intelligence platform supports customer service automation.",
    ]
