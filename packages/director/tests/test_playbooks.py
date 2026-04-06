from __future__ import annotations

from pathlib import Path

from semantic_director.playbooks import list_playbooks, recommend_playbooks, show_playbook
from semantic_director.schemas import ReviewFinding

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_playbook_loader_and_show_from_package_surface() -> None:
    playbooks = list_playbooks(REPO_ROOT)
    ids = [item["playbook_id"] for item in playbooks]
    assert ids == ["extraction_micro_cleanup", "prompt_boundary_benchmark"]

    details = show_playbook(REPO_ROOT, "prompt_boundary_benchmark")
    assert details["spec"]["playbook_id"] == "prompt_boundary_benchmark"
    assert "reviewed slice" in details["procedure_markdown"]


def test_recommend_playbooks_from_package_surface_is_deterministic() -> None:
    findings = [
        ReviewFinding(
            scope="iteration",
            finding_id="boundary",
            category="gate_weakness",
            summary="Overall accuracy is acceptable but actionable speculative boundary accuracy is weak on a fixed slice.",
            recommended_action="Run a prompt benchmark on the subgroup boundary before scaling.",
            evidence_refs=["reports/labels/tranche1_prompt_benchmark_v2_4.md"],
        ),
        ReviewFinding(
            scope="phase",
            finding_id="noise",
            category="data_quality",
            summary="Table of Contents header fragment and unmatched noisy extraction rows remain in the slice.",
            recommended_action="Run a micro cleanup on 5-10 noisy extraction rows.",
            evidence_refs=["reports/labels/tranche1_reextraction_v2_2_summary.json"],
        ),
    ]
    recommendations = recommend_playbooks(findings, REPO_ROOT)
    assert [item.playbook_id for item in recommendations] == [
        "prompt_boundary_benchmark",
        "extraction_micro_cleanup",
    ]
    assert recommendations[0].match_score >= recommendations[1].match_score
