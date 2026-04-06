from ai_washing_member.labeling.build_labeling_sample import OUTPUT_COLUMNS, run_build


def test_build_labeling_sample_member_imports() -> None:
    assert callable(run_build)
    assert "sample_id" in OUTPUT_COLUMNS
