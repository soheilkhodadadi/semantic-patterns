from __future__ import annotations

from pathlib import Path

from semantic_director.readiness import ReadinessEvaluator
from semantic_director.roadmap_model import load_roadmap_model
from semantic_director.task_graph import build_task_graph


def test_readiness_evaluator_runs_on_repo_fixture(tmp_path: Path) -> None:
    model = load_roadmap_model(Path("director/model/roadmap_model.yaml"))
    graph = build_task_graph(model)

    evaluator = ReadinessEvaluator(
        repo_root=str(tmp_path),
        graph=graph,
        model=model,
        deferred_records=[],
    )
    task_states, phase_states = evaluator.evaluate_all()

    assert task_states
    assert phase_states
