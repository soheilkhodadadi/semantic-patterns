from ai_washing_member.labeling.dedupe_labeled_sentences import OUTPUT_COLUMNS, run_dedupe


def test_dedupe_labeled_sentences_member_imports() -> None:
    assert callable(run_dedupe)
    assert "sentence_norm" in OUTPUT_COLUMNS
