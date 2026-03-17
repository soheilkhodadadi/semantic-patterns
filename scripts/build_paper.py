"""Build a repo-native paper draft into Markdown and DOCX."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUTPUT_MARKDOWN = REPO_ROOT / "output" / "paper" / "manuscript_compiled.md"
OUTPUT_DOCX = REPO_ROOT / "output" / "doc" / "ai_washing_preliminary_draft.docx"

SECTION_ORDER = [
    "paper/sections/00_abstract.md",
    "paper/sections/01_introduction.md",
    "paper/sections/02_methodology.md",
    "paper/sections/03_data_and_measures.md",
    "paper/sections/04_results.md",
    "paper/sections/05_discussion.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-markdown",
        type=Path,
        default=OUTPUT_MARKDOWN,
        help="Path for the assembled Markdown manuscript.",
    )
    parser.add_argument(
        "--output-docx",
        type=Path,
        default=OUTPUT_DOCX,
        help="Path for the generated DOCX draft.",
    )
    parser.add_argument(
        "--skip-docx",
        action="store_true",
        help="Only assemble Markdown; do not run Pandoc.",
    )
    return parser.parse_args()


def section_paths() -> list[Path]:
    return [REPO_ROOT / rel_path for rel_path in SECTION_ORDER]


def validate_inputs(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing paper sections:\n{formatted}")


def assemble_markdown(output_path: Path, paths: list[Path]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    for path in paths:
        relative = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8").rstrip()
        chunks.append(f"<!-- begin: {relative} -->\n\n{text}\n\n<!-- end: {relative} -->")
    output_path.write_text("\n\n".join(chunks) + "\n", encoding="utf-8")


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
    sections = section_paths()
    validate_inputs(sections)
    assemble_markdown(args.output_markdown, sections)

    if args.skip_docx:
        print(f"[OK] assembled markdown: {args.output_markdown}")
        return 0

    build_docx(args.output_markdown, args.output_docx)
    print(f"[OK] assembled markdown: {args.output_markdown}")
    print(f"[OK] built docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
