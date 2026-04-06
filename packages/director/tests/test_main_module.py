from __future__ import annotations

from semantic_director.__main__ import main
from semantic_director.cli import main as cli_main


def test_main_module_reexports_cli_main() -> None:
    assert main is cli_main
