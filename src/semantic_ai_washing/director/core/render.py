"""Rendering helpers for canonical roadmap views and optimization outputs."""

from __future__ import annotations

import re
from pathlib import Path

from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_file
from semantic_ai_washing.director.schemas import OptimizationRecommendation, RoadmapModel

ROADMAP_NOTICE_TEMPLATE = [
    "<!-- generated_file: true -->",
    "<!-- source_model: {source_model} -->",
    "<!-- source_sha256: {source_sha256} -->",
    "<!-- rendered_at: {rendered_at} -->",
]

_SHA_RE = re.compile(r"^<!-- source_sha256: (?P<sha>[a-f0-9]+) -->$", re.M)


def render_roadmap_markdown(model: RoadmapModel, source_model: str, source_sha256: str) -> str:
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
