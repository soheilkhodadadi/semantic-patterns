"""Shared helpers for legacy validation timing-table publication runs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from semantic_ai_washing.analysis.build_delivery_table_docs import (
    _build_panel_timing_doc,
    _build_row_matrix_doc,
)
from semantic_ai_washing.analysis.generate_delivery_table_artifacts import (
    _render_row_matrix_payload_markdown,
    _render_timing_payload_markdown,
)


def write_payload_json(payload: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_payload_markdown(payload: dict[str, object], *, kind: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "panel_timing":
        markdown = _render_timing_payload_markdown(payload)
    elif kind == "row_matrix":
        markdown = _render_row_matrix_payload_markdown(payload)
    else:
        raise ValueError(f"Unsupported payload kind: {kind}")
    output_path.write_text(markdown, encoding="utf-8")


def build_payload_docx(payload: dict[str, object], *, kind: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "panel_timing":
        _build_panel_timing_doc(payload, output_path)
    elif kind == "row_matrix":
        _build_row_matrix_doc(payload, output_path)
    else:
        raise ValueError(f"Unsupported payload kind: {kind}")


def flatten_payload_to_csv(payload: dict[str, object], *, kind: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if kind == "panel_timing":
        models: list[dict[str, str]] = payload["models"]  # type: ignore[assignment]
        panels: list[dict[str, object]] = payload["panels"]  # type: ignore[assignment]
        rows: list[dict[str, object]] = []
        for panel in panels:
            heading = panel.get("heading")
            if heading:
                rows.append({"section": str(heading), "row_type": "heading"})
            rows.append(
                {
                    "section": str(heading or ""),
                    "row_type": "coef",
                    "label": str(panel["label"]),
                    **{
                        model["label"]: value
                        for model, value in zip(models, panel["coef_cells"], strict=True)
                    },
                }
            )
            rows.append(
                {
                    "section": str(heading or ""),
                    "row_type": "se",
                    "label": "",
                    **{
                        model["label"]: value
                        for model, value in zip(models, panel["se_cells"], strict=True)
                    },
                }
            )
            for footer in panel["footer_rows"]:  # type: ignore[index]
                rows.append(
                    {
                        "section": str(heading or ""),
                        "row_type": "footer",
                        "label": str(footer["label"]),
                        **{
                            model["label"]: value
                            for model, value in zip(models, footer["cells"], strict=True)
                        },
                    }
                )
        pd.DataFrame(rows).to_csv(output_path, index=False)
        return

    if kind == "row_matrix":
        models = payload["models"]  # type: ignore[assignment]
        body_rows = payload["body_rows"]  # type: ignore[assignment]
        footer_rows = payload["footer_rows"]  # type: ignore[assignment]
        rows = []
        for row in body_rows:
            rows.append(
                {
                    "row_type": row.get("kind", "body"),
                    "label": str(row["label"]),
                    **{
                        model["label"]: value
                        for model, value in zip(models, row["cells"], strict=True)
                    },
                }
            )
        for footer in footer_rows:
            rows.append(
                {
                    "row_type": "footer",
                    "label": str(footer["label"]),
                    **{
                        model["label"]: value
                        for model, value in zip(models, footer["cells"], strict=True)
                    },
                }
            )
        pd.DataFrame(rows).to_csv(output_path, index=False)
        return

    raise ValueError(f"Unsupported payload kind: {kind}")


def copy_table_exports(
    run_dir: Path, paper_root: Path, *, test_id: str, run_id: str
) -> dict[str, str]:
    exports = {
        "table_csv": paper_root / "tables" / f"{test_id}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{test_id}_{run_id}.md",
        "table_docx": paper_root / "docx" / f"{test_id}_{run_id}.docx",
        "table_payload": paper_root / "tables" / f"{test_id}_{run_id}_payload.json",
        "writer_packet": paper_root / "writer_packets" / f"{test_id}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{test_id}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    mapping = {
        "table_main.csv": exports["table_csv"],
        "table_main.md": exports["table_md"],
        "table_main.docx": exports["table_docx"],
        "table_payload.json": exports["table_payload"],
        "writer_packet.md": exports["writer_packet"],
        "result_notes.md": exports["result_notes"],
    }
    for src_name, dst in mapping.items():
        shutil.copy2(run_dir / src_name, dst)
    return {key: str(path) for key, path in exports.items()}
