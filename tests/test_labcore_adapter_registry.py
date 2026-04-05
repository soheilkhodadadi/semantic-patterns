from pathlib import Path

import pytest

from semantic_ai_washing.labcore.registry import (
    PROJECT_SLUGS,
    all_project_adapter_contracts,
    project_adapter_contract,
)


def test_project_adapter_contract_resolves_ai_washing_contract(tmp_path: Path) -> None:
    contract = project_adapter_contract(tmp_path, project="ai_washing")

    assert contract.project == "ai_washing"
    assert contract.mode == "flagship_publication"
    assert contract.framing_note == (
        tmp_path / "docs" / "projects" / "ai_washing" / "adapter_framing_v1.md"
    )
    assert contract.local_private_root == tmp_path / "local_private" / "projects" / "ai_washing"
    assert "semantic_ai_washing.labcore.runtime" in contract.shared_dependencies


def test_all_project_adapter_contracts_cover_all_supported_projects(tmp_path: Path) -> None:
    contracts = all_project_adapter_contracts(tmp_path)

    assert set(contracts) == set(PROJECT_SLUGS)
    assert contracts["eri"].mode == "incubation_reuse_test"
    assert contracts["allocationlab"].mode == "architecture_first"


def test_project_adapter_contract_rejects_unknown_project(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported project"):
        project_adapter_contract(tmp_path, project="unknown")
