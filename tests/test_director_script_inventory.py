from __future__ import annotations

import json
from pathlib import Path

from semantic_ai_washing.director.tasks.script_inventory import (
    build_script_inventory,
    render_script_registry,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_script_inventory_classifies_modules_and_hygiene(tmp_path):
    repo_root = tmp_path

    _write(
        repo_root
        / "src"
        / "semantic_ai_washing"
        / "classification"
        / "classify_all_ai_sentences.py",
        '''"""Canonical classifier entrypoint."""

def main() -> None:
    return

if __name__ == "__main__":
    main()
''',
    )
    _write(
        repo_root / "src" / "semantic_ai_washing" / "data" / "extract_ai_sentences.py",
        '''"""Transitional extractor."""

def main() -> None:
    return

if __name__ == "__main__":
    main()
''',
    )
    _write(
        repo_root / "src" / "scripts" / "extract_ai_sentences.py",
        '''"""Legacy compatibility shim.

TODO: remove after Iteration 1 deprecation window.
"""

from semantic_ai_washing.data.extract_ai_sentences import *  # noqa: F401,F403

if __name__ == "__main__":
    main()
''',
    )
    _write(
        repo_root / "src" / "semantic_ai_washing" / "tmp" / "clean_ai_sentences.py",
        '''"""Scratch helper."""

def main() -> None:
    return
''',
    )
    (repo_root / "src" / "__pycache__").mkdir(parents=True, exist_ok=True)
    _write(repo_root / "src" / ".DS_Store", "metadata")

    output = repo_root / "director" / "snapshots" / "script_inventory.json"
    payload = build_script_inventory(repo_root=str(repo_root), output_path=str(output))

    assert output.exists()
    assert payload["summary"]["canonical_count"] == 1
    assert payload["summary"]["transitional_count"] == 2
    assert payload["summary"]["legacy_count"] == 1
    assert payload["summary"]["hygiene_finding_count"] == 2

    modules = {item["module"]: item for item in payload["modules"]}
    assert (
        modules["semantic_ai_washing.classification.classify_all_ai_sentences"]["classification"]
        == "canonical"
    )
    assert (
        modules["semantic_ai_washing.data.extract_ai_sentences"]["classification"]
        == "transitional"
    )
    assert modules["scripts.extract_ai_sentences"]["classification"] == "transitional"
    assert modules["semantic_ai_washing.tmp.clean_ai_sentences"]["classification"] == "legacy"
    assert (
        modules["semantic_ai_washing.data.extract_ai_sentences"]["replacement_phase"]
        == "iteration1/sentence-table-pilot-2024"
    )


def test_render_script_registry_uses_inventory_snapshot(tmp_path):
    inventory_path = tmp_path / "director" / "snapshots" / "script_inventory.json"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps(
            {
                "summary": {
                    "python_module_count": 3,
                    "canonical_count": 1,
                    "transitional_count": 1,
                    "legacy_count": 1,
                    "entrypoint_count": 2,
                    "hygiene_finding_count": 1,
                },
                "canonical_entrypoints": [
                    {
                        "module": "semantic_ai_washing.classification.classify_all_ai_sentences",
                        "canonical_invocation": (
                            "python -m semantic_ai_washing.classification.classify_all_ai_sentences"
                        ),
                        "doc_summary": "Canonical classifier entrypoint.",
                        "rationale": "primary implementation namespace",
                    }
                ],
                "transitional_surfaces": [
                    {
                        "path": "src/semantic_ai_washing/data/extract_ai_sentences.py",
                        "module": "semantic_ai_washing.data.extract_ai_sentences",
                        "canonical_target": "",
                        "replacement_path": "sentence-table writer",
                        "replacement_phase": "iteration1/sentence-table-pilot-2024",
                        "removal_target": "",
                        "notes": "writes per-filing review files",
                    }
                ],
                "legacy_surfaces": [
                    {
                        "path": "src/semantic_ai_washing/tmp/clean_ai_sentences.py",
                        "rationale": "scratch namespace",
                        "replacement_path": "archive or remove during release packaging",
                        "replacement_phase": "iteration5/release-packaging",
                    }
                ],
                "hygiene_findings": [{"kind": "macos_metadata", "path": "src/.DS_Store"}],
                "decisions": {
                    "planned_replacements": {
                        "src/semantic_ai_washing/data/extract_sample_filings.py": (
                            "Replace raw filing copying with source index + bounded filing manifests."
                        ),
                        "src/semantic_ai_washing/data/extract_ai_sentences.py": (
                            "Replace per-filing *_ai_sentences.txt outputs with year-partitioned sentence tables."
                        ),
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    output_path = tmp_path / "docs" / "director" / "script_registry.md"
    rendered = render_script_registry(
        inventory_path=str(inventory_path),
        output_path=str(output_path),
    )

    assert output_path.exists()
    assert "Script Registry" in rendered
    assert "Canonical Entrypoints" in rendered
    assert "sentence-table writer" in rendered
    assert "src/.DS_Store" in rendered
