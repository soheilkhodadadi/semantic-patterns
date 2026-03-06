"""Generate a repo script inventory and a human-readable script registry."""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import dump_json, git_info, now_utc_iso, sha256_file

DEFAULT_INVENTORY_OUTPUT = "director/snapshots/script_inventory.json"
DEFAULT_REGISTRY_OUTPUT = "docs/director/script_registry.md"

GENERATED_NOTICE_TEMPLATE = [
    "<!-- generated_file: true -->",
    "<!-- source_inventory: {source_inventory} -->",
    "<!-- source_sha256: {source_sha256} -->",
    "<!-- rendered_at: {rendered_at} -->",
]

TOP_LEVEL_MIRROR_BUCKETS = {
    "aggregation",
    "analysis",
    "classification",
    "config",
    "core",
    "data",
    "modeling",
    "patents",
    "scripts",
    "tests",
    "tmp",
}

TRANSITIONAL_CANONICAL_MODULES: dict[str, dict[str, str]] = {
    "semantic_ai_washing.data.extract_sample_filings": {
        "replacement_path": "source index + bounded filing manifest against SEC_SOURCE_DIR",
        "replacement_phase": "iteration1/source-index-contract",
        "notes": (
            "Current implementation copies raw filings into data/processed/sec. "
            "Target architecture keeps raw filings external and indexes them instead."
        ),
    },
    "semantic_ai_washing.data.extract_ai_sentences": {
        "replacement_path": (
            "sentence-table writer producing data/processed/sentences/year=YYYY/ai_sentences.parquet"
        ),
        "replacement_phase": "iteration1/sentence-table-pilot-2024",
        "notes": (
            "Current implementation writes per-filing *_ai_sentences.txt review files. "
            "Target architecture promotes year-partitioned sentence tables."
        ),
    },
    "semantic_ai_washing.scripts.run_pipeline": {
        "replacement_path": "director runbooks or a future explicit pipeline CLI",
        "replacement_phase": "iteration5/release-packaging",
        "notes": "Placeholder orchestration entrypoint; not used by the current canonical workflow.",
    },
}


def _module_name(src_root: Path, file_path: Path) -> str:
    return ".".join(file_path.relative_to(src_root).with_suffix("").parts)


def _parse_python(path: Path) -> tuple[str, ast.Module | None]:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, None
    return source, tree


def _doc_summary(tree: ast.Module | None) -> str:
    if tree is None:
        return ""
    return (
        (ast.get_docstring(tree) or "").strip().splitlines()[0:1][0]
        if ast.get_docstring(tree)
        else ""
    )


def _has_main_function(tree: ast.Module | None) -> bool:
    if tree is None:
        return False
    return any(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body)


def _has_main_guard(source: str) -> bool:
    return '__name__ == "__main__"' in source or "__name__ == '__main__'" in source


def _shim_target(tree: ast.Module | None) -> str | None:
    if tree is None:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue
        if not node.module.startswith("semantic_ai_washing."):
            continue
        if any(alias.name == "*" for alias in node.names):
            return node.module
    return None


def _removal_target(source: str) -> str:
    for marker in ("Removal target:", "remove after "):
        idx = source.find(marker)
        if idx == -1:
            continue
        tail = source[idx + len(marker) :].strip()
        stop_chars = [tail.find(char) for char in ".\n" if char in tail]
        stop = min(stop_chars) if stop_chars else len(tail)
        return tail[:stop].strip(" `")
    return ""


def _canonical_invocation(module_name: str, is_entrypoint: bool) -> str:
    if not is_entrypoint:
        return ""
    return f"python -m {module_name}"


def _classify_module(
    module_name: str,
    relative_path: str,
    shim_target: str | None,
) -> tuple[str, str, dict[str, str]]:
    if module_name in TRANSITIONAL_CANONICAL_MODULES:
        meta = TRANSITIONAL_CANONICAL_MODULES[module_name]
        return (
            "transitional",
            "canonical implementation kept operational while target data architecture is built",
            meta,
        )

    if module_name.startswith("semantic_ai_washing.tmp."):
        return (
            "legacy",
            "scratch/temporary namespace retained for traceability, not part of the canonical workflow",
            {
                "replacement_path": "archive or remove during release packaging",
                "replacement_phase": "iteration5/release-packaging",
                "notes": "Temporary scratch namespace; do not extend it for new work.",
            },
        )

    path_parts = Path(relative_path).parts
    if path_parts and path_parts[0] == "semantic_ai_washing":
        return (
            "canonical",
            "primary implementation namespace under semantic_ai_washing",
            {
                "replacement_path": "",
                "replacement_phase": "",
                "notes": "",
            },
        )

    if path_parts and path_parts[0] in TOP_LEVEL_MIRROR_BUCKETS and shim_target:
        return (
            "transitional",
            "compatibility shim that re-exports a semantic_ai_washing module",
            {
                "replacement_path": f"python -m {shim_target}",
                "replacement_phase": "iteration3/release-packaging",
                "notes": "Keep temporarily for external callers; remove after migration to canonical module invocations.",
            },
        )

    return (
        "legacy",
        "non-canonical Python surface outside semantic_ai_washing with no supported shim target",
        {
            "replacement_path": "archive or remove after confirming no active dependency",
            "replacement_phase": "iteration5/release-packaging",
            "notes": "",
        },
    )


def _iter_python_files(src_root: Path) -> list[Path]:
    return sorted(
        path for path in src_root.rglob("*.py") if path.is_file() and path.name != "__init__.py"
    )


def _hygiene_findings(repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    scan_roots = [
        repo_root / "src",
        repo_root / "tests",
        repo_root / "docs",
        repo_root / "director",
    ]
    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for pattern, kind in (
            ("**/__pycache__", "python_cache_dir"),
            ("**/.DS_Store", "macos_metadata"),
        ):
            for path in sorted(scan_root.glob(pattern)):
                findings.append(
                    {
                        "kind": kind,
                        "path": str(path.relative_to(repo_root)),
                    }
                )
    return findings


def build_script_inventory(
    repo_root: str = ".",
    output_path: str = DEFAULT_INVENTORY_OUTPUT,
) -> dict[str, Any]:
    repo_path = Path(repo_root).resolve()
    src_root = repo_path / "src"
    modules: list[dict[str, Any]] = []

    for file_path in _iter_python_files(src_root):
        relative_path = file_path.relative_to(src_root).as_posix()
        module_name = _module_name(src_root, file_path)
        source, tree = _parse_python(file_path)
        shim_target = _shim_target(tree)
        classification, rationale, replacement_meta = _classify_module(
            module_name=module_name,
            relative_path=relative_path,
            shim_target=shim_target,
        )
        doc_summary = _doc_summary(tree)
        has_main_guard = _has_main_guard(source)
        has_main_function = _has_main_function(tree)
        is_entrypoint = has_main_guard or has_main_function
        removal_target = _removal_target(source)
        domain = (
            (shim_target or module_name).split(".")[1]
            if "." in (shim_target or module_name)
            else ""
        )

        modules.append(
            {
                "path": f"src/{relative_path}",
                "module": module_name,
                "domain": domain,
                "classification": classification,
                "rationale": rationale,
                "status_detail": (
                    "compatibility_shim"
                    if shim_target and not module_name.startswith("semantic_ai_washing.")
                    else "replacement_planned"
                    if module_name in TRANSITIONAL_CANONICAL_MODULES
                    else "scratch_namespace"
                    if module_name.startswith("semantic_ai_washing.tmp.")
                    else "current_implementation"
                ),
                "doc_summary": doc_summary,
                "has_main_guard": has_main_guard,
                "has_main_function": has_main_function,
                "is_entrypoint": is_entrypoint,
                "canonical_target": shim_target or "",
                "canonical_invocation": _canonical_invocation(
                    shim_target or module_name,
                    is_entrypoint,
                ),
                "replacement_path": replacement_meta["replacement_path"],
                "replacement_phase": replacement_meta["replacement_phase"],
                "removal_target": removal_target or "",
                "notes": replacement_meta["notes"],
            }
        )

    classification_counts = Counter(item["classification"] for item in modules)
    entrypoint_counts = Counter(
        item["classification"] for item in modules if item["is_entrypoint"]
    )
    hygiene_findings = _hygiene_findings(repo_path)

    canonical_entrypoints = [
        item for item in modules if item["classification"] == "canonical" and item["is_entrypoint"]
    ]
    transitional_surfaces = [item for item in modules if item["classification"] == "transitional"]
    legacy_surfaces = [item for item in modules if item["classification"] == "legacy"]

    payload = {
        "generated_at": now_utc_iso(),
        "git": git_info(str(repo_path)),
        "repo_root": repo_path.name,
        "summary": {
            "python_module_count": len(modules),
            "canonical_count": classification_counts.get("canonical", 0),
            "transitional_count": classification_counts.get("transitional", 0),
            "legacy_count": classification_counts.get("legacy", 0),
            "entrypoint_count": sum(1 for item in modules if item["is_entrypoint"]),
            "entrypoint_counts": dict(entrypoint_counts),
            "hygiene_finding_count": len(hygiene_findings),
        },
        "decisions": {
            "canonical_namespace": "src/semantic_ai_washing",
            "transitional_roots": [
                "src/aggregation",
                "src/analysis",
                "src/classification",
                "src/config",
                "src/core",
                "src/data",
                "src/modeling",
                "src/patents",
                "src/scripts",
                "src/tests",
                "src/tmp",
            ],
            "legacy_namespaces": ["src/semantic_ai_washing/tmp"],
            "planned_replacements": {
                "src/semantic_ai_washing/data/extract_sample_filings.py": (
                    "Replace raw filing copying with source index + bounded filing manifests."
                ),
                "src/semantic_ai_washing/data/extract_ai_sentences.py": (
                    "Replace per-filing *_ai_sentences.txt outputs with year-partitioned sentence tables."
                ),
            },
        },
        "canonical_entrypoints": canonical_entrypoints,
        "transitional_surfaces": transitional_surfaces,
        "legacy_surfaces": legacy_surfaces,
        "hygiene_findings": hygiene_findings,
        "modules": modules,
    }

    dump_json(output_path, payload)
    return payload


def render_script_registry(
    inventory_path: str = DEFAULT_INVENTORY_OUTPUT,
    output_path: str = DEFAULT_REGISTRY_OUTPUT,
) -> str:
    inventory_source = Path(inventory_path)
    inventory = json.loads(inventory_source.read_text(encoding="utf-8"))
    source_sha = sha256_file(inventory_source)
    lines = [
        template.format(
            source_inventory=str(inventory_source),
            source_sha256=source_sha,
            rendered_at=now_utc_iso(),
        )
        for template in GENERATED_NOTICE_TEMPLATE
    ]
    summary = inventory["summary"]
    lines.extend(
        [
            "",
            "# Script Registry",
            "",
            "This document is generated from the repo script inventory snapshot.",
            "",
            "## Summary",
            f"- Python modules inventoried: `{summary['python_module_count']}`",
            f"- Canonical modules: `{summary['canonical_count']}`",
            f"- Transitional modules: `{summary['transitional_count']}`",
            f"- Legacy modules: `{summary['legacy_count']}`",
            f"- Entrypoints: `{summary['entrypoint_count']}`",
            f"- Hygiene findings: `{summary['hygiene_finding_count']}`",
            "",
            "## Canonical Entrypoints",
            "",
            "| Module | Invocation | Notes |",
            "| --- | --- | --- |",
        ]
    )
    for item in inventory["canonical_entrypoints"]:
        note = item["doc_summary"] or item["rationale"]
        lines.append(f"| `{item['module']}` | `{item['canonical_invocation']}` | {note} |")
    if not inventory["canonical_entrypoints"]:
        lines.append("| none | none | none |")

    lines.extend(
        [
            "",
            "## Transitional Surfaces",
            "",
            "| Path | Canonical Target | Replacement Path | Removal Target |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in inventory["transitional_surfaces"]:
        target = item["canonical_target"] or item["module"]
        replacement = item["replacement_path"] or item["notes"] or "keep under review"
        removal = item["removal_target"] or item["replacement_phase"] or "TBD"
        lines.append(f"| `{item['path']}` | `{target}` | {replacement} | {removal} |")
    if not inventory["transitional_surfaces"]:
        lines.append("| none | none | none | none |")

    lines.extend(
        [
            "",
            "## Legacy and Scratch Modules",
            "",
            "| Path | Classification Note | Planned Action |",
            "| --- | --- | --- |",
        ]
    )
    for item in inventory["legacy_surfaces"]:
        action = item["replacement_path"] or item["replacement_phase"] or "archive or remove"
        lines.append(f"| `{item['path']}` | {item['rationale']} | {action} |")
    if not inventory["legacy_surfaces"]:
        lines.append("| none | none | none |")

    planned = inventory["decisions"]["planned_replacements"]
    lines.extend(
        [
            "",
            "## Planned Replacements",
            "",
            "- `src/semantic_ai_washing/data/extract_sample_filings.py`: "
            f"{planned['src/semantic_ai_washing/data/extract_sample_filings.py']}",
            "- `src/semantic_ai_washing/data/extract_ai_sentences.py`: "
            f"{planned['src/semantic_ai_washing/data/extract_ai_sentences.py']}",
            "",
            "Current canonical raw-source contract is `SEC_SOURCE_DIR` plus the source index. "
            "Per-filing copied raw filings and per-filing AI sentence text outputs remain operational but are not the target architecture.",
            "",
            "## Hygiene Findings",
        ]
    )
    if inventory["hygiene_findings"]:
        for finding in inventory["hygiene_findings"]:
            lines.append(f"- `{finding['kind']}`: `{finding['path']}`")
    else:
        lines.append("- none")

    output = "\n".join(lines).strip() + "\n"
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(output, encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--mode",
        choices=("inventory", "publish", "both"),
        default="both",
    )
    parser.add_argument("--input-inventory", default=DEFAULT_INVENTORY_OUTPUT)
    parser.add_argument("--output-inventory", default=DEFAULT_INVENTORY_OUTPUT)
    parser.add_argument("--output-registry", default=DEFAULT_REGISTRY_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode in {"inventory", "both"}:
        build_script_inventory(
            repo_root=args.repo_root,
            output_path=args.output_inventory,
        )
    if args.mode in {"publish", "both"}:
        render_script_registry(
            inventory_path=args.input_inventory
            if args.mode == "publish"
            else args.output_inventory,
            output_path=args.output_registry,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
