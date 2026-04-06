from __future__ import annotations

from semantic_director.optimizer import DirectorOptimizer


def test_optimizer_patch_proposal_returns_none_when_emit_patch_disabled(tmp_path) -> None:
    optimizer = DirectorOptimizer(
        repo_root=str(tmp_path),
        roadmap_model_path=str(tmp_path / "roadmap.yaml"),
        remediation_library_path=str(tmp_path / "remediation.yaml"),
        optimization_dir=str(tmp_path / "optimization"),
        decisions_dir=str(tmp_path / "decisions"),
        weights={},
        emit_patch=False,
    )

    proposal = optimizer._patch_proposal(
        recommendation_id="rec-1",
        source_sha="abc123",
        blocked_state=None,
        task_lookup={},
        focus_iteration="1",
        focus_phase="phase-a",
    )

    assert proposal is None
