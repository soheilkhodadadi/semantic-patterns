"""Document ingestion adapters for markdown/txt/docx strategic files."""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

import xml.etree.ElementTree as ET

from semantic_ai_washing.director.core.roadmap_model import (
    load_roadmap_model,
    roadmap_summary_dict,
)
from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_file

_WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
_ITERATION_HEADER_RE = re.compile(
    r"^\s*(?:#+\s*)?Iteration\s+(?P<id>\d+)\s*[–-]\s*(?P<title>.+?)\s*$",
    re.I,
)
_GOAL_RE = re.compile(r"^\s*(?:\*\*)?Goal(?:\*\*)?:\s*(?P<goal>.+)$", re.I)


def read_text_document(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".docx":
        return _read_docx_text(path)
    return p.read_text(encoding="utf-8", errors="ignore")


def _read_docx_text(path: str) -> str:
    with ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)

    paragraphs: list[str] = []
    for para in root.findall(".//w:p", _WORD_NAMESPACE):
        text_parts = [node.text or "" for node in para.findall(".//w:t", _WORD_NAMESPACE)]
        paragraph = "".join(text_parts).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return "\n".join(paragraphs)


def _extract_iterations(lines: list[str]) -> list[dict]:
    iterations: list[dict] = []
    current: dict | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        header = _ITERATION_HEADER_RE.match(line)
        if header:
            current = {
                "iteration_id": header.group("id"),
                "title": header.group("title").strip(),
                "goal": "",
                "areas": [],
                "outcomes": [],
            }
            iterations.append(current)
            continue
        if current is None:
            continue
        goal_match = _GOAL_RE.match(line)
        if goal_match and not current["goal"]:
            current["goal"] = goal_match.group("goal").strip()
            continue
        if "|" in line and "Area" not in line and "Actions in Iteration" not in line:
            # Skip markdown table rows from the prose summary parser.
            continue
        lowered = line.lower()
        if lowered.startswith("outcome:"):
            current["outcomes"].append(line.split(":", 1)[1].strip())
            continue
        if line.startswith("* ") or line.startswith("- "):
            bullet = line.lstrip("*- ").strip()
            if re.search(r"\b(outcome|deliverable|result)\b", lowered):
                current["outcomes"].append(bullet)
            else:
                current["areas"].append(bullet)

    return iterations


def summarize_document(path: str, max_points: int = 200) -> dict:
    text = read_text_document(path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Keep unique informative lines while preserving order.
    seen = set()
    unique_lines: list[str] = []
    for line in lines:
        normalized = re.sub(r"\s+", " ", line.lower()).strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_lines.append(line)

    gates = [
        line
        for line in unique_lines
        if re.search(r"\bgate\b|\bacceptance\s+criteria\b|\bmust\s+pass\b", line, re.I)
    ]
    risks = [
        line for line in unique_lines if re.search(r"\bR\d\b|\brisk\b|\bmitigation\b", line, re.I)
    ]

    key_points = unique_lines[:max_points]
    iterations = _extract_iterations(unique_lines)
    return {
        "source_path": path,
        "source_sha256": sha256_file(path),
        "ingested_at": now_utc_iso(),
        "paragraph_count": len(lines),
        "key_points": key_points,
        "gates": gates[:max_points],
        "risks": risks[:max_points],
        "iterations": iterations,
    }


def summarize_roadmap_model(path: str) -> dict:
    model = load_roadmap_model(path)
    return roadmap_summary_dict(model=model, source_path=path, source_sha256=sha256_file(path))
