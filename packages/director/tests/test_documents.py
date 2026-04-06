from __future__ import annotations

from pathlib import Path

from semantic_director.documents import read_text_document, summarize_document


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_summarize_document_extracts_iterations_gates_and_risks(tmp_path):
    path = tmp_path / "roadmap.md"
    _write(
        path,
        """
# Program Notes

Iteration 1 - Label Expansion
Goal: Freeze a clean review sheet.
- review-sheet generation
- diagnostic export
Outcome: readiness gate passed
- R1: monitor disagreement drift
- Acceptance criteria: gate must pass before promotion
""".strip(),
    )

    summary = summarize_document(str(path))

    assert summary["source_path"] == str(path)
    assert summary["paragraph_count"] >= 6
    assert summary["iterations"][0]["iteration_id"] == "1"
    assert summary["iterations"][0]["goal"] == "Freeze a clean review sheet."
    assert "readiness gate passed" in summary["iterations"][0]["outcomes"][0]
    assert any("Acceptance criteria" in line for line in summary["gates"])
    assert any("R1" in line for line in summary["risks"])


def test_read_text_document_reads_markdown_plaintext(tmp_path):
    path = tmp_path / "protocol.md"
    _write(path, "# Protocol\n\nLine one.\nLine two.\n")

    assert "Line one." in read_text_document(str(path))
