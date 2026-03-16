"""Audit local Python environments against the repo's canonical runtime target."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

PACKAGES = [
    "numpy",
    "pandas",
    "pyarrow",
    "torch",
    "sentence_transformers",
    "spacy",
    "wrds",
    "psycopg2",
]


def _read_pyvenv_cfg(env_dir: Path) -> dict[str, str]:
    cfg_path = env_dir / "pyvenv.cfg"
    if not cfg_path.exists():
        return {}
    payload: dict[str, str] = {}
    for line in cfg_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def _run_python_json(
    python_path: Path, code: str, timeout_seconds: int
) -> tuple[str, dict[str, Any] | None, str]:
    try:
        completed = subprocess.run(
            [str(python_path), "-c", code],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return (
            "timeout",
            None,
            f"interpreter probe timed out after {timeout_seconds} seconds",
        )

    if completed.returncode != 0:
        return "error", None, completed.stderr.strip()

    try:
        return "ok", json.loads(completed.stdout), completed.stderr.strip()
    except json.JSONDecodeError as exc:
        return "error", None, f"invalid probe json: {exc}"


def _probe_interpreter(python_path: Path, *, include_imports: bool) -> dict[str, Any]:
    if not python_path.exists():
        return {
            "exists": False,
            "path": str(python_path),
            "probe_status": "missing",
            "version": "",
            "architecture": "",
            "imports": {},
            "stderr": "",
        }

    base_probe = """
import json
import platform
import sys
print(json.dumps({
    "exists": True,
    "path": sys.executable,
    "probe_status": "ok",
    "version": sys.version.split()[0],
    "architecture": platform.machine(),
}))
"""
    status, payload, stderr = _run_python_json(python_path, base_probe, timeout_seconds=10)
    if status == "timeout":
        return {
            "exists": True,
            "path": str(python_path),
            "probe_status": "probe_timeout",
            "version": "",
            "architecture": "",
            "imports": {},
            "stderr": stderr,
        }
    if status != "ok" or payload is None:
        return {
            "exists": True,
            "path": str(python_path),
            "probe_status": "probe_failed",
            "version": "",
            "architecture": "",
            "imports": {},
            "stderr": stderr,
        }

    imports: dict[str, Any] = {}
    if include_imports:
        for package in PACKAGES:
            import_probe = f"""
import importlib
import json
module = importlib.import_module({package!r})
print(json.dumps({{"version": str(getattr(module, "__version__", "") or "")}}))
"""
            pkg_status, pkg_payload, pkg_stderr = _run_python_json(
                python_path, import_probe, timeout_seconds=15
            )
            if pkg_status == "ok" and pkg_payload is not None:
                imports[package] = {"ok": True, "version": str(pkg_payload.get("version", ""))}
            elif pkg_status == "timeout":
                imports[package] = {
                    "ok": False,
                    "error_type": "TimeoutExpired",
                    "error": pkg_stderr,
                }
            else:
                imports[package] = {
                    "ok": False,
                    "error_type": "ImportProbeFailed",
                    "error": pkg_stderr,
                }
    else:
        for package in PACKAGES:
            imports[package] = {
                "ok": False,
                "error_type": "NotProbed",
                "error": "Import checks are only run against the canonical repo environment.",
            }

    payload["imports"] = imports
    payload["stderr"] = stderr
    return payload


def _inspect_env_dir(env_dir: Path) -> dict[str, Any]:
    python_path = env_dir / "bin" / "python"
    payload = _probe_interpreter(python_path, include_imports=True)
    payload["env_dir"] = str(env_dir)
    payload["pyvenv_cfg"] = _read_pyvenv_cfg(env_dir)
    return payload


def _inspect_shell_python() -> dict[str, Any]:
    shell_python = shutil.which("python")
    if not shell_python:
        return {
            "exists": False,
            "path": "",
            "probe_status": "missing",
            "version": "",
            "architecture": "",
            "imports": {},
            "pyvenv_cfg": {},
            "stderr": "python not found on PATH",
        }
    payload = _probe_interpreter(Path(shell_python), include_imports=False)
    payload["pyvenv_cfg"] = {}
    return payload


def _canonical_failures(
    canonical: dict[str, Any], target_python: str, target_arch: str
) -> list[str]:
    failures: list[str] = []
    if not canonical.get("exists"):
        failures.append("canonical_env_missing")
        return failures
    if canonical.get("probe_status") != "ok":
        failures.append("canonical_env_probe_failed")
        return failures
    version = str(canonical.get("version", ""))
    if not version.startswith(str(target_python)):
        failures.append(f"canonical_python_not_{target_python}")
    arch = str(canonical.get("architecture", ""))
    if arch != str(target_arch):
        failures.append(f"canonical_arch_not_{target_arch}")
    imports = canonical.get("imports", {})
    for package in PACKAGES:
        if not bool((imports.get(package) or {}).get("ok", False)):
            failures.append(f"canonical_missing_import:{package}")
    return failures


def _warnings(shell: dict[str, Any], legacy: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if shell.get("probe_status") != "ok":
        warnings.append("shell_python_probe_failed")
    elif shell.get("architecture") != "arm64":
        warnings.append("shell_python_not_arm64")
    if legacy.get("exists"):
        warnings.append("legacy_venv_present")
    return warnings


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    canonical_env_dir = repo_root / args.canonical_env_dir
    legacy_env_dir = repo_root / args.legacy_env_dir
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    shell = _inspect_shell_python()
    canonical = _inspect_env_dir(canonical_env_dir)
    legacy = _probe_interpreter(legacy_env_dir / "bin" / "python", include_imports=False)
    legacy["env_dir"] = str(legacy_env_dir)
    legacy["pyvenv_cfg"] = _read_pyvenv_cfg(legacy_env_dir)

    failures = _canonical_failures(canonical, args.target_python, args.target_arch)
    warnings = _warnings(shell, legacy)
    if failures:
        status = "failed"
    elif warnings:
        status = "passed_with_warnings"
    else:
        status = "passed"

    report = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_target": {
            "canonical_env_dir": args.canonical_env_dir,
            "target_python": args.target_python,
            "target_arch": args.target_arch,
        },
        "summary": {
            "status": status,
            "canonical_failures": failures,
            "warnings": warnings,
        },
        "shell_python": shell,
        "canonical_env": canonical,
        "legacy_env": legacy,
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve environment directories and the output path.",
    )
    parser.add_argument(
        "--canonical-env-dir",
        default=".venv",
        help="Canonical repo-local environment directory.",
    )
    parser.add_argument(
        "--legacy-env-dir",
        default="venv",
        help="Legacy environment directory to inspect when present.",
    )
    parser.add_argument(
        "--target-python",
        default="3.11",
        help="Required canonical Python major.minor version.",
    )
    parser.add_argument(
        "--target-arch",
        default="arm64",
        help="Required canonical interpreter architecture.",
    )
    parser.add_argument(
        "--output",
        default="reports/environment/environment_audit_pre_rebuild_v1.json",
        help="Output JSON artifact path relative to the repo root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_audit(args)
    print(
        "[environment-audit] "
        f"status={report['status']} canonical_failures={report['summary']['canonical_failures']}"
    )
    print(f"[environment-audit] report -> {args.output}")


if __name__ == "__main__":
    main()
