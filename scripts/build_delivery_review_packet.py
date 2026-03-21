"""Build a modular preliminary-delivery review packet in Markdown and DOCX."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUTPUT_MARKDOWN = REPO_ROOT / "output" / "paper" / "preliminary_delivery_review_packet_v1.md"
OUTPUT_DOCX = REPO_ROOT / "output" / "doc" / "preliminary_delivery_review_packet_v1.docx"

SECTION_ORDER = [
    ("Overview", "docs/preliminary_delivery_status_2026-03-20.md"),
    ("Blueprint", "reports/analysis/preliminary_delivery_blueprint_v1.md"),
    ("Story Arc", "reports/analysis/literature_story_arc_ai_washing_mar2026_v1.md"),
    ("Table Plan", "reports/analysis/preliminary_results_table_plan_v1.md"),
    ("Boundary", "reports/analysis/main_text_appendix_boundary_v1.md"),
    ("Table 1 Spec", "reports/analysis/table_1_summary_statistics_spec_v1.md"),
    ("Table 1 Artifact", "paper/generated/tables/table_1_summary_statistics_prelim_v1.md"),
    ("Table 2 Spec", "reports/analysis/table_2_core_patent_validation_spec_v1.md"),
    ("Table 2 Artifact", "paper/generated/tables/table_2_core_patent_validation_prelim_v1.md"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=OUTPUT_MARKDOWN,
        help="Path for the assembled Markdown packet.",
    )
    parser.add_argument(
        "--output-docx",
        type=Path,
        default=OUTPUT_DOCX,
        help="Path for the generated DOCX packet.",
    )
    parser.add_argument(
        "--skip-docx",
        action="store_true",
        help="Only assemble Markdown; do not run Pandoc.",
    )
    return parser.parse_args()


def validate_inputs() -> None:
    missing = [REPO_ROOT / rel for _, rel in SECTION_ORDER if not (REPO_ROOT / rel).exists()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing packet sections:\n{formatted}")


def assemble_markdown(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = [
        "# Preliminary Delivery Review Packet\n",
        "This packet is intended for modular review of the preliminary delivery package.\n",
        "It is not the manuscript itself. It is a working review document that keeps the current story, table plan, and first built tables in one editable place.\n",
    ]
    for title, rel_path in SECTION_ORDER:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8").rstrip()
        chunks.append(f"\n\n## {title}\n\n<!-- begin: {rel_path} -->\n\n{text}\n\n<!-- end: {rel_path} -->\n")
    output_path.write_text("".join(chunks).rstrip() + "\n", encoding="utf-8")


def build_docx(markdown_path: Path, output_docx: Path) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("pandoc is not installed or not on PATH")

    output_docx.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = PAPER_DIR / "metadata.yaml"
    reference_doc = PAPER_DIR / "reference.docx"

    command = [
        pandoc,
        "--standalone",
        "--metadata-file",
        str(metadata_path),
        str(markdown_path),
        "-o",
        str(output_docx),
    ]
    if reference_doc.exists():
        command.extend(["--reference-doc", str(reference_doc)])
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    validate_inputs()
    assemble_markdown(args.output_markdown)
    if args.skip_docx:
        print(f"[OK] assembled markdown review packet: {args.output_markdown}")
        return 0
    build_docx(args.output_markdown, args.output_docx)
    print(f"[OK] assembled markdown review packet: {args.output_markdown}")
    print(f"[OK] built review packet docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
