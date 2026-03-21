"""Build monthly report Markdown files into DOCX outputs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
DEFAULT_MONTH = "2026-03"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--month",
        default=DEFAULT_MONTH,
        help="Month folder under output/paper/reports and output/doc/reports, e.g. 2026-03.",
    )
    return parser.parse_args()


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
    src_dir = REPO_ROOT / "output" / "paper" / "reports" / args.month
    dst_dir = REPO_ROOT / "output" / "doc" / "reports" / args.month

    if not src_dir.exists():
        raise FileNotFoundError(f"Monthly report source folder does not exist: {src_dir}")

    markdown_files = sorted(src_dir.glob("*.md"))
    if not markdown_files:
        raise FileNotFoundError(f"No markdown report files found in: {src_dir}")

    built = []
    for markdown_path in markdown_files:
        output_docx = dst_dir / f"{markdown_path.stem}.docx"
        build_docx(markdown_path, output_docx)
        built.append(output_docx)

    for path in built:
        print(f"[OK] built monthly report docx: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
