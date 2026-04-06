from ai_washing_member.labeling.qa_labeled_dataset import REQUIRED_COLUMNS, run_qa


def test_qa_labeled_dataset_member_imports() -> None:
    assert callable(run_qa)
    assert "sentence_id" in REQUIRED_COLUMNS
