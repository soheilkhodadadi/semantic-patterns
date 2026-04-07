from __future__ import annotations

from pathlib import Path

from ai_washing_member.data.stage_sec_year_root import stage_sec_year_root


def _touch_file(path: Path, text: str = "sample") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_stage_sec_year_root_accepts_direct_qtr_source_and_reuses_links(tmp_path: Path) -> None:
    source_root = tmp_path / "2025"
    for quarter in ("QTR1", "QTR2", "QTR3", "QTR4"):
        _touch_file(source_root / quarter / f"{quarter.lower()}.txt")

    staged_root = tmp_path / "staged"
    first = stage_sec_year_root(source_root=source_root, output_root=staged_root, year=2025)
    second = stage_sec_year_root(source_root=source_root, output_root=staged_root, year=2025)

    assert first["status"] == "staged"
    assert first["created_quarters"] == ["QTR1", "QTR2", "QTR3", "QTR4"]
    assert first["reused_quarters"] == []

    assert second["created_quarters"] == []
    assert second["reused_quarters"] == ["QTR1", "QTR2", "QTR3", "QTR4"]

    for quarter in ("QTR1", "QTR2", "QTR3", "QTR4"):
        target = staged_root / "2025" / quarter
        assert target.is_symlink()
        assert target.resolve() == (source_root / quarter).resolve()
