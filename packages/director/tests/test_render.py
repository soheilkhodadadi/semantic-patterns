from __future__ import annotations

from pathlib import Path

from semantic_director.render import is_rendered_roadmap_fresh, render_roadmap_markdown
from semantic_director.roadmap_model import load_roadmap_model
from semantic_labcore.runtime import sha256_file


def test_render_roadmap_markdown_uses_repo_fixture(tmp_path: Path) -> None:
    model_path = Path("director/model/roadmap_model.yaml")
    model = load_roadmap_model(model_path)
    markdown_path = tmp_path / "roadmap_master.md"

    rendered = render_roadmap_markdown(
        model=model,
        source_model=str(model_path),
        source_sha256=sha256_file(model_path),
        approved_reviews=[],
    )
    markdown_path.write_text(rendered, encoding="utf-8")

    assert "# Roadmap Master" in rendered
    assert is_rendered_roadmap_fresh(model_path, markdown_path)
