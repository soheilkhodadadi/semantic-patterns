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
        ]
    )

    for iteration in model.iterations:
        lines.extend(
            [
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
                    f"- Depends on: {', '.join(phase.depends_on) if phase.depends_on else 'none'}",
                    f"- Required artifacts: {', '.join(phase.required_artifacts) if phase.required_artifacts else 'none'}",
                    "",
                    "#### Tasks",
                ]
            )
            for task in phase.tasks:
                input_paths = [item.path for item in task.inputs]
                output_paths = [item.path for item in task.outputs]
                lines.extend(
                    [
                        f"- `{task.task_id}` {task.title}",
                        f"  - kind: `{task.kind}`",
                        f"  - depends_on: {', '.join(task.depends_on) if task.depends_on else 'none'}",
                        f"  - inputs: {', '.join(input_paths) if input_paths else 'none'}",
                        f"  - outputs: {', '.join(output_paths) if output_paths else 'none'}",
                        f"  - risks: {', '.join(task.risks) if task.risks else 'none'}",
                    ]
                )
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
) -> str:
    lines = [
        f"# Optimization Recommendation: {recommendation.recommendation_id}",
        "",
        f"- Focus iteration: `{recommendation.focus_iteration or 'all'}`",
        f"- Focus phase: `{recommendation.focus_phase or 'all'}`",
        f"- Proposal only: `{str(recommendation.proposal_only).lower()}`",
        f"- Patch file: `{recommendation.patch_file or 'none'}`",
        "",
        "## Recommended Tasks",
    ]
    if recommendation.recommended_task_ids:
        for task_id in recommendation.recommended_task_ids:
            lines.append(f"- `{task_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Blocked Tasks"])
    if recommendation.blocked_task_ids:
        for task_id in recommendation.blocked_task_ids:
            lines.append(f"- `{task_id}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Rationale"])
    if recommendation.rationale:
        for item in recommendation.rationale:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    lines.extend(["", "## Task States"])
    for row in task_state_rows:
        lines.append(
            f"- `{row['task_id']}` `{row['status']}` score={row.get('score', 0.0)} phase=`{row['phase_id']}`"
        )
    return "\n".join(lines).strip() + "\n"
