"""Branch policy helpers for iteration kickoff and closeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.schemas import BranchingPolicySpec, RoadmapModel

BOUNDARY_PHASE_SUFFIXES = {
    "kickoff": "kickoff-and-preflight",
    "review": "review-and-replan",
}


def format_branch_name(template: str, iteration_id: str, slug: str = "work") -> str:
    return template.format(iteration_id=iteration_id, slug=slug)


def boundary_phase_id(iteration_id: str, kind: str) -> str:
    return f"iteration{iteration_id}/{BOUNDARY_PHASE_SUFFIXES[kind]}"


def validate_iteration_boundaries(model: RoadmapModel) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for iteration in model.iterations:
        phase_ids = {phase.phase_id for phase in iteration.phases}
        has_review = boundary_phase_id(iteration.iteration_id, "review") in phase_ids
        checks.append(
            {
                "name": f"iteration_{iteration.iteration_id}_review_phase",
                "ok": has_review,
                "detail": "review-and-replan phase exists"
                if has_review
                else "missing review-and-replan phase",
            }
        )
        if str(iteration.iteration_id) != "1":
            has_kickoff = boundary_phase_id(iteration.iteration_id, "kickoff") in phase_ids
            checks.append(
                {
                    "name": f"iteration_{iteration.iteration_id}_kickoff_phase",
                    "ok": has_kickoff,
                    "detail": "kickoff-and-preflight phase exists"
                    if has_kickoff
                    else "missing kickoff-and-preflight phase",
                }
            )
    return checks


def current_branch(repo_root: str) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def is_worktree_clean(repo_root: str) -> bool:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0 and not proc.stdout.strip()


def is_based_on(repo_root: str, base_branch: str) -> tuple[bool, str]:
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_branch, "HEAD"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    detail = proc.stderr.strip() or f"merge-base return code={proc.returncode}"
    if proc.returncode == 0:
        detail = f"HEAD contains {base_branch}"
    return proc.returncode == 0, detail


def closeout_branch_plan(
    policy: BranchingPolicySpec, iteration_id: str, current_branch_name: str
) -> dict[str, Any]:
    integration_branch = format_branch_name(policy.integration_branch_template, iteration_id)
    next_iteration_id = str(int(iteration_id) + 1)
    next_integration = format_branch_name(policy.integration_branch_template, next_iteration_id)
    return {
        "current_branch": current_branch_name,
        "integration_branch": integration_branch,
        "merge_target": policy.merge_target,
        "tag": policy.tag_template.format(iteration_id=iteration_id),
        "closeout_validation_commands": list(policy.closeout_validation_commands),
        "steps": [
            f"git push origin {current_branch_name}",
            f"git switch {integration_branch}",
            f"git merge --ff-only {current_branch_name}",
            f"git switch {policy.merge_target}",
            "git pull --ff-only",
            f"git switch {integration_branch}",
            f"git merge --ff-only {policy.merge_target}",
        ],
        "merge_strategy_note": (
            "Prefer ff-only. If ff-only is not possible, use a non-interactive PR/merge-commit "
            "workflow after rerunning closeout validation."
        ),
        "next_iteration_steps": [
            f"git switch {policy.merge_target}",
            "git pull --ff-only",
            f"git switch -c {next_integration}",
        ],
    }


def kickoff_checks(
    repo_root: str,
    policy: BranchingPolicySpec,
    iteration_id: str,
) -> list[dict[str, Any]]:
    expected_branch = format_branch_name(policy.integration_branch_template, iteration_id)
    current = current_branch(repo_root)
    base_ok, base_detail = is_based_on(repo_root, policy.merge_target)
    clean = is_worktree_clean(repo_root)
    return [
        {
            "name": "branch_name",
            "ok": current == expected_branch,
            "detail": f"expected={expected_branch} current={current}",
        },
        {
            "name": "merge_base",
            "ok": base_ok,
            "detail": base_detail,
        },
        {
            "name": "worktree_clean",
            "ok": clean,
            "detail": "clean" if clean else "tracked changes present",
        },
    ]


def normalize_branching_policy(model: RoadmapModel) -> BranchingPolicySpec:
    return model.branching_policy


def review_artifact_paths(
    reviews_dir: Path, iteration_id: str, phase_id: str = ""
) -> dict[str, Path]:
    if phase_id:
        safe_phase = phase_id.replace("/", "_")
        stem = f"phase_{safe_phase}"
    else:
        stem = f"iteration_{iteration_id}"
    return {
        "review_json": reviews_dir / f"{stem}_review.json",
        "review_md": reviews_dir / f"{stem}_review.md",
        "patch_yaml": reviews_dir / f"{stem}_patch_proposal.yaml",
        "branch_plan": reviews_dir / f"{stem}_branch_plan.md",
        "starter_prompt": reviews_dir / f"{stem}_starter_prompt.md",
        "approval_json": reviews_dir / f"{stem}_approval.json",
        "kickoff_json": reviews_dir / f"iteration_{iteration_id}_kickoff.json",
        "patch_apply_json": reviews_dir / f"{stem}_patch_apply.json",
    }
