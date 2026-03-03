"""Document ingestion adapters for markdown/txt/docx strategic files."""

from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

import xml.etree.ElementTree as ET

from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_file

_WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


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


def summarize_document(path: str, max_points: int = 40) -> dict:
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
    return {
        "source_path": path,
        "source_sha256": sha256_file(path),
        "ingested_at": now_utc_iso(),
        "paragraph_count": len(lines),
        "key_points": key_points,
        "gates": gates[:max_points],
        "risks": risks[:max_points],
    }
