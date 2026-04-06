"""Playbook registry loading and deterministic recommendation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from semantic_director.schemas import (
    PlaybookRecommendation,
    PlaybookSpec,
    ReviewFinding,
)


def _playbooks_root(repo_root: str | Path) -> Path:
    return Path(repo_root).resolve() / "director" / "playbooks"


def _blast_radius_rank(value: str) -> int:
    return {"low": 0, "medium": 1, "high": 2}.get(str(value), 3)


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return payload


def load_playbook_index(repo_root: str | Path) -> dict[str, Any]:
    index_path = _playbooks_root(repo_root) / "index.yaml"
    if not index_path.exists():
        return {}
    payload = _load_yaml(index_path)
    payload["index_path"] = str(index_path)
    return payload


def load_playbook_specs(repo_root: str | Path) -> list[PlaybookSpec]:
    root = _playbooks_root(repo_root)
    index = load_playbook_index(repo_root)
    specs: list[PlaybookSpec] = []
    for item in index.get("playbooks", []) or []:
        if not isinstance(item, dict):
            continue
        metadata_rel = str(item.get("metadata_path", "")).strip()
        procedure_rel = str(item.get("procedure_path", "")).strip()
        if not metadata_rel:
            continue
        metadata_path = root / metadata_rel
        if not metadata_path.exists():
            raise FileNotFoundError(f"Playbook metadata file missing: {metadata_path}")
        payload = _load_yaml(metadata_path)
        payload.setdefault("metadata_path", str(metadata_path))
        payload.setdefault("procedure_path", str(root / procedure_rel) if procedure_rel else "")
        specs.append(PlaybookSpec.model_validate(payload))
    return sorted(specs, key=lambda spec: spec.playbook_id)


def get_playbook_spec(repo_root: str | Path, playbook_id: str) -> PlaybookSpec:
    for spec in load_playbook_specs(repo_root):
        if spec.playbook_id == playbook_id:
            return spec
    raise KeyError(f"Unknown playbook_id={playbook_id}")


def list_playbooks(repo_root: str | Path) -> list[dict[str, Any]]:
    return [spec.as_deterministic_dict() for spec in load_playbook_specs(repo_root)]


def show_playbook(repo_root: str | Path, playbook_id: str) -> dict[str, Any]:
    spec = get_playbook_spec(repo_root, playbook_id)
    procedure_markdown = ""
    if spec.procedure_path:
        procedure_path = Path(spec.procedure_path)
        if procedure_path.exists():
            procedure_markdown = procedure_path.read_text(encoding="utf-8")
    return {
        "spec": spec.as_deterministic_dict(),
        "procedure_markdown": procedure_markdown,
    }


def recommend_playbooks(
    findings: list[ReviewFinding], repo_root: str | Path
) -> list[PlaybookRecommendation]:
    specs = load_playbook_specs(repo_root)
    if not specs or not findings:
        return []

    recommendations: list[PlaybookRecommendation] = []
    for spec in specs:
        match_score = 0
        matched_categories: set[str] = set()
        matched_keywords: set[str] = set()
        for finding in findings:
            if finding.category in spec.finding_categories:
                match_score += 2
                matched_categories.add(finding.category)
            text = " ".join(
                [
                    finding.summary,
                    finding.recommended_action,
                    " ".join(str(ref) for ref in finding.evidence_refs),
                ]
            ).lower()
            for keyword in spec.keywords:
                normalized = str(keyword).strip().lower()
                if normalized and normalized in text:
                    match_score += 1
                    matched_keywords.add(normalized)
        if match_score <= 0:
            continue
        reason_parts = []
        if matched_categories:
            reason_parts.append("categories=" + ", ".join(sorted(matched_categories)))
        if matched_keywords:
            reason_parts.append("keywords=" + ", ".join(sorted(matched_keywords)))
        recommendations.append(
            PlaybookRecommendation(
                playbook_id=spec.playbook_id,
                title=spec.title,
                category=spec.category,
                reason="; ".join(reason_parts) or "matched review findings",
                match_score=match_score,
                blast_radius=spec.blast_radius,
                automation_level=spec.automation_level,
                procedure_path=spec.procedure_path,
            )
        )

    recommendations.sort(
        key=lambda item: (
            _blast_radius_rank(item.blast_radius),
            -item.match_score,
            item.title.lower(),
            item.playbook_id,
        )
    )
    return recommendations
