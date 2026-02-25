from semantic_ai_washing.aggregation.aggregate_classification_counts import (
    build_aggregated_rows,
    parse_labels_from_file,
)


def test_parse_labels_from_csv_uses_label_pred(tmp_path):
    classified = (
        tmp_path / "2024" / "20240101_10-K_edgar_data_1234567_0000000000-24-000001_classified.csv"
    )
    classified.parent.mkdir(parents=True, exist_ok=True)
    classified.write_text(
        "sentence,label_pred,p_actionable\n"
        "We launched an AI model,Actionable,0.92\n"
        "We may expand AI use,Speculative,0.12\n"
        "Bad row,,0.0\n",
        encoding="utf-8",
    )

    labels = parse_labels_from_file(str(classified))

    assert labels == ["Actionable", "Speculative"]


def test_parse_labels_from_legacy_txt(tmp_path):
    classified = (
        tmp_path / "2024" / "20240102_10-K_edgar_data_1234567_0000000000-24-000002_classified.txt"
    )
    classified.parent.mkdir(parents=True, exist_ok=True)
    classified.write_text(
        "Sentence A | Label: Irrelevant | Score: 0.71\n"
        "Sentence B | Label: Speculative | Score: 0.66\n"
        "Malformed line\n",
        encoding="utf-8",
    )

    labels = parse_labels_from_file(str(classified))

    assert labels == ["Irrelevant", "Speculative"]


def test_parse_labels_from_csv_falls_back_to_label_column(tmp_path):
    classified = (
        tmp_path / "2024" / "20240103_10-K_edgar_data_7777777_0000000000-24-000003_classified.csv"
    )
    classified.parent.mkdir(parents=True, exist_ok=True)
    classified.write_text(
        "sentence,label\nText one,Actionable\nText two,Irrelevant\n",
        encoding="utf-8",
    )

    labels = parse_labels_from_file(str(classified))

    assert labels == ["Actionable", "Irrelevant"]


def test_build_aggregated_rows_handles_mixed_formats_and_empty_inputs(tmp_path):
    root = tmp_path / "sec"
    year_dir = root / "2024"
    year_dir.mkdir(parents=True, exist_ok=True)

    csv_file = year_dir / "20240101_10-K_edgar_data_1234567_0000000000-24-000001_classified.csv"
    csv_file.write_text(
        "sentence,label_pred\nSentence 1,Actionable\nSentence 2,Irrelevant\nSentence 3,ERROR\n",
        encoding="utf-8",
    )

    txt_file = year_dir / "20240102_10-K_edgar_data_1234567_0000000000-24-000002_classified.txt"
    txt_file.write_text(
        "Sentence 4 | Label: Speculative | Score: 0.62\nMalformed\n",
        encoding="utf-8",
    )

    empty_csv = year_dir / "20240103_10-K_edgar_data_7654321_0000000000-24-000003_classified.csv"
    empty_csv.write_text("sentence,label_pred\n", encoding="utf-8")

    rows, classified_files, used_files, firm_year_count = build_aggregated_rows(str(root))

    assert classified_files == 3
    assert used_files == 2
    assert firm_year_count == 2

    row_map = {(row["cik"], row["year"]): row for row in rows}

    first = row_map[("1234567", 2024)]
    assert first["A_count"] == 1
    assert first["S_count"] == 1
    assert first["I_count"] == 1
    assert first["total_count"] == 3

    second = row_map[("7654321", 2024)]
    assert second["A_count"] == 0
    assert second["S_count"] == 0
    assert second["I_count"] == 0
    assert second["total_count"] == 0
