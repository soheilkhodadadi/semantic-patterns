from __future__ import annotations

from pathlib import Path

from semantic_director.roadmap_model import load_roadmap_model
from semantic_director.task_graph import build_task_graph


def test_task_graph_builds_from_repo_fixture() -> None:
    model = load_roadmap_model(Path("director/model/roadmap_model.yaml"))

    graph = build_task_graph(model)

    assert "iteration1/label-ops-bootstrap" in graph.phases_by_id
    assert graph.topological_order()
    assert graph.phase_topological_order()
