from pathlib import Path

import pytest

from semantic_labcore.registry import PROJECT_SLUGS, project_lanes, shared_lanes


def test_shared_lanes_resolve_expected_paths(tmp_path: Path) -> None:
    lanes = shared_lanes(tmp_path)

    assert lanes.lab_docs == tmp_path / "docs" / "lab"
    assert lanes.control_plane_docs == tmp_path / "docs" / "lab" / "control_plane"
    assert lanes.registry_reports == tmp_path / "reports" / "registry"
    assert lanes.manifests == tmp_path / "data" / "manifests"
    assert lanes.doc_output == tmp_path / "output" / "doc" / "shared"
    assert lanes.figure_output == tmp_path / "output" / "figures" / "shared"


@pytest.mark.parametrize("project", PROJECT_SLUGS)
def test_project_lanes_resolve_expected_paths(tmp_path: Path, project: str) -> None:
    lanes = project_lanes(tmp_path, project)

    assert lanes.project == project
    assert lanes.docs == tmp_path / "docs" / "projects" / project
    assert lanes.reports == tmp_path / "reports" / "projects" / project
    assert lanes.processed_data == tmp_path / "data" / "processed" / "projects" / project
    assert lanes.doc_output == tmp_path / "output" / "doc" / "projects" / project
    assert lanes.figure_output == tmp_path / "output" / "figures" / "projects" / project


def test_project_lanes_reject_unknown_project(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported project"):
        project_lanes(tmp_path, "unknown_project")
