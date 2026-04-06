from __future__ import annotations

import sys
from pathlib import Path

from semantic_director.runtime import run_command


def test_director_runtime_preserves_timeout_wording(tmp_path: Path) -> None:
    command = f'{sys.executable} -c "import time; time.sleep(0.2)"'

    result = run_command(command, cwd=tmp_path, timeout_seconds=0.01)

    assert result["timed_out"] is True
    assert "[director] command timed out" in result["stderr"]
