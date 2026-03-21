"""Build a standalone supervisor update in Markdown and DOCX."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
DEFAULT_MARKDOWN = REPO_ROOT / "output" / "paper" / "supervisor_update_prelim_v1.md"
DEFAULT_DOCX = REPO_ROOT / "output" / "doc" / "supervisor_update_prelim_v1.docx"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-markdown",
        type=Path,
        default=DEFAULT_MARKDOWN,
        help="Path to the source Markdown memo.",
    )
    parser.add_argument(
        "--output-docx",
        type=Path,
        default=DEFAULT_DOCX,
        help="Path for the generated DOCX memo.",
    )
    return parser.parse_args()


def build_docx(markdown_path: Path, output_docx: Path) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("pandoc is not installed or not on PATH")

    if not markdown_path.exists():
        raise FileNotFoundError(f"Input markdown does not exist: {markdown_path}")

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
    build_docx(args.input_markdown, args.output_docx)
    print(f"[OK] built supervisor update docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
