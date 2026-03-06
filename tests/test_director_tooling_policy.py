from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from semantic_ai_washing.director.adapters import atlas as atlas_adapter
from semantic_ai_washing.director.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_atlas_runs_in_isolated_cwd(tmp_path, monkeypatch):
    repo_root = tmp_path
    wrapper = repo_root / "scripts" / "atlas_isolated.sh"
    _write(
        repo_root / "director" / "config" / "tooling_policy.yaml",
        yaml.safe_dump(
            {
                "policies": [
                    {
                        "policy_id": "atlas_isolated_env",
                        "tool": "atlas",
                        "mode": "isolated_skill_env",
                        "repo_root_uv_run_forbidden": True,
                        "required_runner": "~/.codex/skills/atlas/scripts/atlas_cli.py",
                        "wrapper_path": "scripts/atlas_isolated.sh",
                    }
                ]
            },
            sort_keys=False,
        ),
    )
    _write(wrapper, "#!/usr/bin/env bash\nexit 0\n")
    wrapper.chmod(0o755)

    captured: dict[str, str] = {}

    def fake_check_output(cmd, text, stderr, cwd, env):  # noqa: ANN001
        captured["cwd"] = cwd
        captured["cmd0"] = cmd[0]
        captured["atlas_cli"] = cmd[1]
        return "ChatGPT Atlas\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    ok, _ = atlas_adapter._run_atlas_command(["app-name"], repo_root=str(repo_root))
    assert ok
    assert captured["cwd"] != str(repo_root)
    assert captured["cmd0"] == str(wrapper)


def test_doctor_detects_repo_venv_policy_drift(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main_with_args(["init"]) == 0

    pyvenv_cfg = tmp_path / ".venv" / "pyvenv.cfg"
    _write(pyvenv_cfg, "home = /tmp/python3.12\nversion = 3.12.0\n")

    code = main_with_args(["doctor", "--skip-make-doctor", "--json"])
    assert code == 2


def main_with_args(args: list[str]) -> int:
    import sys

    previous = sys.argv
    try:
        sys.argv = ["director"] + args
        return int(main())
    finally:
        sys.argv = previous
