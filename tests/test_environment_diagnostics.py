from __future__ import annotations

import argparse
import os
import platform
import sys
from pathlib import Path

from semantic_ai_washing.diagnostics.environment_audit import run_audit
from semantic_ai_washing.diagnostics.wrds_smoke import run_wrds_smoke


def _link_python(env_dir: Path, python_path: str) -> None:
    bin_dir = env_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    os.symlink(python_path, bin_dir / "python")
    (env_dir / "pyvenv.cfg").write_text("home = /tmp/python\nversion = 3.11.0\n", encoding="utf-8")


def test_environment_audit_reports_canonical_env(tmp_path: Path):
    import semantic_ai_washing.diagnostics.environment_audit as environment_audit

    environment_audit.PACKAGES[:] = []
    canonical = tmp_path / ".venv"
    _link_python(canonical, sys.executable)

    report = run_audit(
        argparse.Namespace(
            repo_root=str(tmp_path),
            canonical_env_dir=".venv",
            legacy_env_dir="venv_missing",
            target_python=".".join(platform.python_version_tuple()[:2]),
            target_arch=platform.machine(),
            output="reports/environment/audit.json",
        )
    )

    assert report["canonical_env"]["exists"] is True
    assert report["canonical_env"]["probe_status"] == "ok"
    assert report["repo_target"]["canonical_env_dir"] == ".venv"
    assert report["status"] in {"passed", "passed_with_warnings"}
    assert Path(tmp_path / "reports" / "environment" / "audit.json").exists()


def test_wrds_smoke_fails_without_credentials(tmp_path: Path, monkeypatch):
    import semantic_ai_washing.diagnostics.wrds_smoke as wrds_smoke

    monkeypatch.setattr(wrds_smoke, "_import_check", lambda name: {"ok": True, "version": "x"})
    for name in ["WRDS_USER", "WRDS_PASS", "WRDS_DB_HOST", "WRDS_DB_PORT"]:
        monkeypatch.delenv(name, raising=False)

    report = run_wrds_smoke(
        argparse.Namespace(
            repo_root=str(tmp_path),
            dotenv="missing.env",
            query="select 1 as ok",
            timeout_seconds=5,
            output="reports/environment/wrds_smoke.json",
        )
    )

    assert report["status"] == "failed"
    assert "missing_wrds_credentials" in report["summary"]["failure_reasons"]


def test_wrds_smoke_passes_with_mocked_queries(tmp_path: Path, monkeypatch):
    import semantic_ai_washing.diagnostics.wrds_smoke as wrds_smoke

    monkeypatch.setattr(wrds_smoke, "_import_check", lambda name: {"ok": True, "version": "x"})
    monkeypatch.setattr(
        wrds_smoke,
        "_run_wrds_query",
        lambda user, password, query: {"ok": True, "row_count": 1, "records": [{"ok": 1}]},
    )
    monkeypatch.setattr(
        wrds_smoke,
        "_run_psycopg2_query",
        lambda user, password, host, port, query, timeout_seconds: {
            "ok": True,
            "row_count": 1,
            "records": [{"ok": 1}],
        },
    )
    monkeypatch.setenv("WRDS_USER", "user")
    monkeypatch.setenv("WRDS_PASS", "pass")
    monkeypatch.setenv("WRDS_DB_HOST", "host")
    monkeypatch.setenv("WRDS_DB_PORT", "9737")

    report = run_wrds_smoke(
        argparse.Namespace(
            repo_root=str(tmp_path),
            dotenv="missing.env",
            query="select 1 as ok",
            timeout_seconds=5,
            output="reports/environment/wrds_smoke.json",
        )
    )

    assert report["status"] == "passed"
    assert report["attempts"]["wrds_connection"]["ok"] is True
    assert report["attempts"]["psycopg2_connection"]["ok"] is True
