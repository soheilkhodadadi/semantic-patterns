"""Rendering helpers for canonical roadmap views and optimization outputs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_file
from semantic_ai_washing.director.schemas import (
    IterationReview,
    OptimizationRecommendation,
    PhaseReview,
    RoadmapModel,
    StarterPromptArtifact,
)

ROADMAP_NOTICE_TEMPLATE = [
    "<!-- generated_file: true -->",
    "<!-- source_model: {source_model} -->",
    "<!-- source_sha256: {source_sha256} -->",
    "<!-- rendered_at: {rendered_at} -->",
]

_SHA_RE = re.compile(r"^<!-- source_sha256: (?P<sha>[a-f0-9]+) -->$", re.M)


def json_like_summary(payload: dict[str, Any]) -> str:
    if not payload:
        return "none"
    parts = []
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, dict):
            inner = ", ".join(f"{inner_key}={value[inner_key]}" for inner_key in sorted(value))
            parts.append(f"{key}{{{inner}}}")
        else:
            parts.append(f"{key}={value}")
    return "; ".join(parts)


def render_roadmap_markdown(
    model: RoadmapModel,
    source_model: str,
    source_sha256: str,
    approved_reviews: list[dict] | None = None,
) -> str:
    lines = [
        notice_line.format(
            source_model=source_model,
            source_sha256=source_sha256,
            rendered_at=now_utc_iso(),
        )
        for notice_line in ROADMAP_NOTICE_TEMPLATE
    ]
    lines.extend(
        [
            "",
            "# Roadmap Master",
            "",
            "This document is generated from the canonical roadmap YAML model.",
            "",
            "Optimization proposals may recommend resequencing tasks or phases beyond the canonical order shown here.",
            "",
            "## Branching Policy",
        ]
    )
    lines.extend(
        [
            f"- integration branch template: `{model.branching_policy.integration_branch_template}`",
            f"- work branch template: `{model.branching_policy.work_branch_template}`",
            f"- merge target: `{model.branching_policy.merge_target}`",
            f"- preferred merge strategy: `{model.branching_policy.preferred_merge_strategy}`",
            f"- review approval required before next iteration: `{str(model.branching_policy.require_review_approval_before_next_iteration).lower()}`",
            f"- review approval required before main merge: `{str(model.branching_policy.require_review_approval_before_main_merge).lower()}`",
            f"- starter prompt required: `{str(model.branching_policy.starter_prompt_required).lower()}`",
            "",
            "## Review Workflow",
            "- Every iteration ends with `review-and-replan`.",
            "- Iterations 2-5 start with `kickoff-and-preflight`.",
            "- Approved reviews authorize the next iteration and main-merge closeout.",
            "",
            "## Stakeholder Alignment",
            f"- source artifact: `{model.stakeholder_alignment.source_artifact}`",
            f"- active development scope: `{model.stakeholder_alignment.active_development_scope}`",
            f"- publication target scope: `{model.stakeholder_alignment.publication_target_scope}`",
            f"- desired horizon: `{model.stakeholder_alignment.desired_horizon}`",
            "",
            "### Methodology Hard Gates",
        ]
    )
    if model.stakeholder_alignment.methodology_hard_gates:
        for gate in model.stakeholder_alignment.methodology_hard_gates:
            lines.append(f"- {gate}")
    else:
        lines.append("- none")
    lines.extend(["", "### Data Hard Gates"])
    if model.stakeholder_alignment.data_hard_gates:
        for gate in model.stakeholder_alignment.data_hard_gates:
            lines.append(f"- {gate}")
    else:
        lines.append("- none")
    lines.extend(["", "### Publication Hard Gates"])
    if model.stakeholder_alignment.publication_hard_gates:
        for gate in model.stakeholder_alignment.publication_hard_gates:
            lines.append(f"- {gate}")
    else:
        lines.append("- none")
    lines.extend(["", "### Stakeholder Requirements"])
    if model.stakeholder_alignment.requirements:
        for requirement in model.stakeholder_alignment.requirements:
            lines.extend(
                [
                    f"- `{requirement.requirement_id}` priority=`{requirement.priority}` stakeholder=`{requirement.stakeholder}`",
                    f"  - summary: {requirement.summary}",
                    f"  - target iteration: `{requirement.target_iteration or 'none'}`",
                    f"  - source refs: {', '.join(requirement.source_refs) or 'none'}",
                    f"  - mapped phases: {', '.join(requirement.mapped_phases) or 'none'}",
                    f"  - mapped gates: {', '.join(requirement.mapped_gates) or 'none'}",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Policies",
        ]
    )
    if model.policies:
        for policy in model.policies:
            lines.append(
                f"- `{policy.policy_id}` `{policy.kind}` enforcement=`{policy.enforcement}` value=`{policy.value}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Data Layers"])
    if model.data_layers:
        for layer in model.data_layers:
            export = f" review=`{layer.review_export_path}`" if layer.review_export_path else ""
            lines.append(
                f"- `{layer.layer_id}` path=`{layer.canonical_path}` format=`{layer.format}`{export}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Source Windows"])
    if model.source_windows:
        for window in model.source_windows:
            lines.append(
                f"- `{window.source_window_id}` status=`{window.status}` years={', '.join(window.years)} root=`{window.source_root_ref}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Tooling Policies"])
    if model.tooling_policies:
        for policy in model.tooling_policies:
            lines.append(
                f"- `{policy.policy_id}` tool=`{policy.tool}` mode=`{policy.mode}` wrapper=`{policy.wrapper_path or 'none'}`"
            )
    else:
        lines.append("- none")

    for iteration in model.iterations:
        lines.extend(
            [
                "",
                f"## Iteration {iteration.iteration_id} - {iteration.title}",
                f"Goal: {iteration.goal}",
                f"Entry criteria: {', '.join(iteration.entry_criteria) if iteration.entry_criteria else 'none'}",
                f"Exit criteria: {', '.join(iteration.exit_criteria) if iteration.exit_criteria else 'none'}",
                "",
            ]
        )
        for phase in iteration.phases:
            lines.extend(
                [
                    f"### {phase.phase_id}",
                    f"- Title: {phase.title}",
                    f"- Goal: {phase.goal}",
                    f"- Lifecycle: `{phase.lifecycle_state}`",
                    f"- Depends on: {', '.join(phase.depends_on) if phase.depends_on else 'none'}",
                    f"- Source window: `{phase.source_window_id or 'none'}`",
                    f"- Required artifacts: {', '.join(phase.required_artifacts) if phase.required_artifacts else 'none'}",
                    f"- Tags: {', '.join(phase.tags) if phase.tags else 'none'}",
                    "",
                ]
            )
            if phase.tasks:
                lines.append("#### Tasks")
                for task in phase.tasks:
                    input_paths = [item.path for item in task.inputs]
                    output_paths = [item.path for item in task.outputs]
                    lines.extend(
                        [
                            f"- `{task.task_id}` {task.title}",
                            f"  - kind: `{task.kind}` gate_class: `{task.gate_class}` automation: `{task.automation_level}`",
                            f"  - depends_on: {', '.join(task.depends_on) if task.depends_on else 'none'}",
                            f"  - inputs: {', '.join(input_paths) if input_paths else 'none'}",
                            f"  - outputs: {', '.join(output_paths) if output_paths else 'none'}",
                            f"  - tags: {', '.join(task.tags) if task.tags else 'none'}",
                            f"  - risks: {', '.join(task.risks) if task.risks else 'none'}",
                        ]
                    )
            else:
                lines.append("#### Tasks")
                lines.append("- phase-level only in this roadmap version")
            lines.append("")
    approved_reviews = approved_reviews or []
    lines.extend(["", "## Approved Review Appendix"])
    if approved_reviews:
        for review in approved_reviews:
            scope = review.get("phase_id") or f"iteration {review.get('iteration_id', '')}"
            lines.extend(
                [
                    f"### {review.get('review_id', '')}",
                    f"- Scope: `{scope}`",
                    f"- Accepted changes: {', '.join(review.get('accepted_change_ids', [])) or 'none'}",
                    f"- Deferred changes: {', '.join(review.get('deferred_change_ids', [])) or 'none'}",
                    f"- Next iteration: `{(review.get('next_iteration') or {}).get('iteration_id', '') or 'none'}`",
                    f"- Entry criteria: {', '.join((review.get('next_iteration') or {}).get('entry_criteria', [])) or 'none'}",
                    f"- Stakeholder summary: {json_like_summary(review.get('stakeholder_alignment_summary', {}))}",
                    f"- Unmet stakeholder requirements: {', '.join(review.get('unmet_stakeholder_requirements', [])) or 'none'}",
                    f"- Publication blockers: {', '.join(review.get('publication_readiness_blockers', [])) or 'none'}",
                    "",
                ]
            )
    else:
        lines.append("- none")
    return "\n".join(lines).strip() + "\n"


def rendered_roadmap_hash(markdown_path: str | Path) -> str:
    payload = Path(markdown_path).read_text(encoding="utf-8")
    match = _SHA_RE.search(payload)
    return match.group("sha") if match else ""


def is_rendered_roadmap_fresh(model_path: str | Path, markdown_path: str | Path) -> bool:
    model_source = Path(model_path)
    markdown_source = Path(markdown_path)
    if not model_source.exists() or not markdown_source.exists():
        return False
    return rendered_roadmap_hash(markdown_source) == sha256_file(model_source)


def render_optimization_markdown(
    recommendation: OptimizationRecommendation,
    task_state_rows: list[dict],
    phase_state_rows: list[dict],
) -> str:
    lines = [
        f"# Optimization Recommendation: {recommendation.recommendation_id}",
        "",
        f"- Focus iteration: `{recommendation.focus_iteration or 'all'}`",
        f"- Focus phase: `{recommendation.focus_phase or 'all'}`",
        f"- Proposal only: `{str(recommendation.proposal_only).lower()}`",
        f"- Patch file: `{recommendation.patch_file or 'none'}`",
        "",
        "## Recommended Phases",
    ]
    if recommendation.recommended_phase_ids:
        for phase_id in recommendation.recommended_phase_ids:
            lines.append(f"- `{phase_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Recommended Tasks"])
    if recommendation.recommended_task_ids:
        for task_id in recommendation.recommended_task_ids:
            lines.append(f"- `{task_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Blocked Phases"])
    if recommendation.blocked_phase_ids:
        for phase_id in recommendation.blocked_phase_ids:
            lines.append(f"- `{phase_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Blocked Tasks"])
    if recommendation.blocked_task_ids:
        for task_id in recommendation.blocked_task_ids:
            lines.append(f"- `{task_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Policy Blocks"])
    if recommendation.policy_block_ids:
        for policy_id in recommendation.policy_block_ids:
            lines.append(f"- `{policy_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Source Window Notes"])
    if recommendation.source_window_notes:
        for note in recommendation.source_window_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- none")

    lines.extend(["", "## Rationale"])
    if recommendation.rationale:
        for item in recommendation.rationale:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    lines.extend(["", "## Phase States"])
    for row in phase_state_rows:
        lines.append(
            f"- `{row['phase_id']}` `{row['status']}` lifecycle=`{row.get('lifecycle_state', 'planned')}` score={row.get('score', 0.0)}"
        )

    lines.extend(["", "## Task States"])
    for row in task_state_rows:
        lines.append(
            f"- `{row['task_id']}` `{row['status']}` score={row.get('score', 0.0)} phase=`{row['phase_id']}`"
        )
    return "\n".join(lines).strip() + "\n"


def render_review_markdown(review: IterationReview | PhaseReview) -> str:
    scope = (
        review.phase_id if isinstance(review, PhaseReview) else f"iteration {review.iteration_id}"
    )
    lines = [
        f"# Review: {review.review_id}",
        "",
        f"- Type: `{review.review_type}`",
        f"- Scope: `{scope}`",
        f"- Generated at: `{review.generated_at}`",
        f"- Status: `{review.status}`",
        "",
        "## Phase Summary",
    ]
    for item in review.phase_summary.get("phases", []):
        lines.append(
            f"- `{item['phase_id']}` status=`{item['status']}` lifecycle=`{item['lifecycle_state']}` runs={item['run_count']}"
        )
    lines.extend(["", "## Blockers"])
    for key, value in review.blocker_summary.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Findings"])
    if review.findings:
        for finding in review.findings:
            lines.append(
                f"- `{finding.finding_id}` `{finding.category}` severity=`{finding.severity}`: {finding.summary}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Stakeholder Alignment"])
    lines.append(f"- Summary: {json_like_summary(review.stakeholder_alignment_summary or {})}")
    lines.append(
        f"- Unmet stakeholder requirements: {', '.join(review.unmet_stakeholder_requirements) or 'none'}"
    )
    lines.append(
        f"- Deferred stakeholder requirements: {', '.join(review.deferred_stakeholder_requirements) or 'none'}"
    )
    lines.append(
        f"- Publication readiness blockers: {', '.join(review.publication_readiness_blockers) or 'none'}"
    )
    lines.extend(["", "## Roadmap Changes"])
    if review.roadmap_changes:
        for change in review.roadmap_changes:
            lines.append(
                f"- `{change.change_id}` source=`{change.source}` status=`{change.status}` target=`{change.target}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Next Iteration"])
    lines.append(
        f"- recommended phase: `{review.next_iteration.get('recommended_phase', '') or 'none'}`"
    )
    lines.append(
        f"- entry criteria: {', '.join(review.next_iteration.get('entry_criteria', [])) or 'none'}"
    )
    return "\n".join(lines).strip() + "\n"


def render_branch_plan_markdown(
    branch_plan: dict[str, Any], next_phase: str, starter_prompt_path: str
) -> str:
    lines = [
        "# Branch Plan",
        "",
        f"- Current branch: `{branch_plan.get('current_branch', '')}`",
        f"- Integration branch: `{branch_plan.get('integration_branch', '')}`",
        f"- Merge target: `{branch_plan.get('merge_target', '')}`",
        f"- Suggested next phase: `{next_phase or 'none'}`",
        f"- Starter prompt: `{starter_prompt_path or 'none'}`",
        "",
        "## Closeout Steps",
    ]
    for step in branch_plan.get("steps", []):
        lines.append(f"- `{step}`")
    merge_note = str(branch_plan.get("merge_strategy_note", "")).strip()
    if merge_note:
        lines.extend(["", "## Merge Strategy", f"- {merge_note}"])
    lines.extend(["", "## Next Iteration Steps"])
    for step in branch_plan.get("next_iteration_steps", []):
        lines.append(f"- `{step}`")
    return "\n".join(lines).strip() + "\n"


def render_starter_prompt_markdown(starter: StarterPromptArtifact) -> str:
    next_iteration_id = ""
    next_phase = starter.next_phase or ""
    if next_phase.startswith("iteration"):
        next_iteration_id = next_phase.split("/", 1)[0].replace("iteration", "")
    lines = [
        f"# Iteration {starter.iteration_id} Starter Prompt",
        "",
        f"- Recommended new chat: `{str(starter.recommended_new_chat).lower()}`",
        f"- Next phase: `{next_phase or 'none'}`",
        "",
        "## Stable Checkpoints",
    ]
    for commit in starter.stable_checkpoint_commits:
        lines.append(f"- `{commit}`")
    lines.extend(["", "## Key Artifacts"])
    for path in starter.key_artifacts:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Constraints"])
    for item in starter.constraints:
        lines.append(f"- {item}")
    lines.extend(["", "## First Commands"])
    if next_iteration_id:
        lines.extend(
            [
                "- `git switch main`",
                "- `git pull --ff-only`",
                f"- `git switch -c iteration{next_iteration_id}/integration`",
                f"- `.venv/bin/python -m semantic_ai_washing.director.cli kickoff --iteration {next_iteration_id}`",
            ]
        )
    else:
        lines.append("- determine the next iteration boundary before kickoff")
    lines.extend(
        [
            "",
            "## Prompt",
            "Use the iteration integration branch as the default base. Start from the next recommended phase, preserve proposal-only roadmap changes until explicitly approved, and prefer a new Codex chat at approved iteration boundaries.",
        ]
    )
    return "\n".join(lines).strip() + "\n"
