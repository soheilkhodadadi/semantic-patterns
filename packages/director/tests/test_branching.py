from __future__ import annotations

from pathlib import Path

from semantic_director.branching import (
    boundary_phase_id,
    format_branch_name,
    review_artifact_paths,
    validate_iteration_boundaries,
)
from semantic_director.roadmap_model import load_roadmap_model


def test_branching_helpers_format_expected_values() -> None:
    assert format_branch_name("codex/iteration{iteration_id}/{slug}", "3", "work") == (
        "codex/iteration3/work"
    )
    assert boundary_phase_id("2", "kickoff") == "iteration2/kickoff-and-preflight"


def test_validate_iteration_boundaries_runs_on_repo_model() -> None:
    model = load_roadmap_model(Path("director/model/roadmap_model.yaml"))
    checks = validate_iteration_boundaries(model)
    assert checks
    assert all("ok" in check for check in checks)


def test_review_artifact_paths_generates_expected_names(tmp_path: Path) -> None:
    paths = review_artifact_paths(tmp_path, "4", phase_id="iteration4/review-and-replan")
    assert paths["review_json"].name == "phase_iteration4_review-and-replan_review.json"
    assert paths["starter_prompt"].name == "phase_iteration4_review-and-replan_starter_prompt.md"
