from __future__ import annotations

from pathlib import Path

from semantic_director.roadmap_model import (
    find_phase,
    load_remediation_library,
    load_roadmap_model,
    resolve_model_path,
)


def test_roadmap_model_loads_repo_fixture() -> None:
    model_path = Path("director/model/roadmap_model.yaml")

    model = load_roadmap_model(model_path)

    assert model.project["name"] == "semantic-patterns"
    assert find_phase(model, iteration_id="1", phase_name="label-ops-bootstrap") is not None


def test_remediation_library_loads_repo_fixture() -> None:
    library = load_remediation_library("director/model/remediation_library.yaml")

    assert "common.audit_sentence_integrity" in library


def test_resolve_model_path_supports_relative_and_absolute_inputs(tmp_path: Path) -> None:
    relative = resolve_model_path(str(tmp_path), "director/model/roadmap_model.yaml")
    absolute = resolve_model_path(
        str(tmp_path), str(tmp_path / "director/model/roadmap_model.yaml")
    )

    assert relative == (tmp_path / "director/model/roadmap_model.yaml").resolve()
    assert absolute == (tmp_path / "director/model/roadmap_model.yaml").resolve()
