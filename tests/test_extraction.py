from semantic_ai_washing.core.sentence_filter import merge_page_fragments


def test_merge_page_split_sentence():
    lines = [
        (
            "The Company continues to invest in artificial intelligence and machine "
            "learning to enhance its products — 4 —"
        ),
        " and services in the coming year.",
    ]

    merged = merge_page_fragments(lines)

    assert len(merged) == 1
    result = merged[0]
    assert "—" not in result
    assert result.startswith("The Company")
    assert result.endswith(".")


def test_no_fragment_no_change():
    lines = ["This sentence is complete and has no fragment."]
    merged = merge_page_fragments(lines)
    assert merged == lines


def test_merge_removes_page_marker_and_normalizes_sentence_end():
    lines = [
        "Our AI platform supports forecasting and recommendations — 12 —",
        " across the retail business",
    ]
    merged = merge_page_fragments(lines)

    assert len(merged) == 1
    result = merged[0]
    assert "12" not in result
    assert "—" not in result
    assert result[0].isupper()
    assert result.endswith(".")
