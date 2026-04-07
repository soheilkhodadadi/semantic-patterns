"""Stage a single SEC filing year into a canonical YEAR/QTR directory shape."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

REQUIRED_QUARTERS = ("QTR1", "QTR2", "QTR3", "QTR4")


def _resolve_source_year_root(source_root: str | Path, year: int) -> Path:
    resolved = Path(source_root).expanduser().resolve()
    direct_quarters = all((resolved / quarter).is_dir() for quarter in REQUIRED_QUARTERS)
    if direct_quarters:
        return resolved

    nested = resolved / str(int(year))
    nested_quarters = all((nested / quarter).is_dir() for quarter in REQUIRED_QUARTERS)
    if nested_quarters:
        return nested

    raise FileNotFoundError(
        "Source root does not expose the expected quarter layout. "
        f"Checked {resolved} and {nested}."
    )


def _remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    raise FileNotFoundError(f"Cannot remove missing path: {path}")


def stage_sec_year_root(
    *,
    source_root: str | Path,
    output_root: str | Path,
    year: int,
    overwrite: bool = False,
) -> dict[str, Any]:
    source_year_root = _resolve_source_year_root(source_root, year)
    staged_root = Path(output_root).expanduser().resolve()
    staged_year_root = staged_root / str(int(year))
    staged_year_root.mkdir(parents=True, exist_ok=True)

    quarter_targets: dict[str, str] = {}
    created_quarters: list[str] = []
    reused_quarters: list[str] = []

    for quarter in REQUIRED_QUARTERS:
        source_quarter = source_year_root / quarter
        if not source_quarter.is_dir():
            raise FileNotFoundError(f"Missing source quarter directory: {source_quarter}")

        target_quarter = staged_year_root / quarter
        expected_target = str(source_quarter.resolve())
        quarter_targets[quarter] = expected_target

        if os.path.lexists(target_quarter):
            if target_quarter.is_symlink() and str(target_quarter.resolve()) == expected_target:
                reused_quarters.append(quarter)
                continue
            if not overwrite:
                raise FileExistsError(
                    f"Target already exists and overwrite is disabled: {target_quarter}"
                )
            _remove_existing(target_quarter)

        target_quarter.symlink_to(source_quarter, target_is_directory=True)
        created_quarters.append(quarter)

    return {
        "status": "staged",
        "year": int(year),
        "source_root": str(Path(source_root).expanduser().resolve()),
        "source_year_root": str(source_year_root),
        "output_root": str(staged_root),
        "output_year_root": str(staged_year_root),
        "required_quarters": list(REQUIRED_QUARTERS),
        "created_quarters": created_quarters,
        "reused_quarters": reused_quarters,
        "quarter_targets": quarter_targets,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--report-path", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = stage_sec_year_root(
        source_root=args.source_root,
        output_root=args.output_root,
        year=args.year,
        overwrite=bool(args.overwrite),
    )
    if args.report_path:
        report_path = Path(args.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        "[sec-stage] staged "
        f"year={report['year']} created={report['created_quarters']} "
        f"reused={report['reused_quarters']}"
    )
    print(f"[sec-stage] output_root -> {report['output_root']}")


if __name__ == "__main__":
    main()
