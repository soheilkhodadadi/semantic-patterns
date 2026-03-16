"""Run a live WRDS connectivity smoke test from the canonical repo environment."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import importlib
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


REQUIRED_ENV_VARS = ["WRDS_USER", "WRDS_PASS", "WRDS_DB_HOST", "WRDS_DB_PORT"]


def _import_check(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "")
        return {"ok": True, "version": str(version or "")}
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}


def _load_credentials(dotenv_path: Path) -> tuple[dict[str, str], list[str]]:
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)
    creds = {name: os.getenv(name, "") for name in REQUIRED_ENV_VARS}
    missing = [name for name, value in creds.items() if not str(value).strip()]
    return creds, missing


def _run_wrds_query(user: str, password: str, query: str) -> dict[str, Any]:
    wrds = importlib.import_module("wrds")
    original_getpass = getpass.getpass
    try:
        getpass.getpass = lambda prompt="": user if "username" in prompt.lower() else password
        db = wrds.Connection(wrds_username=user)
        frame = db.raw_sql(query)
        db.close()
    finally:
        getpass.getpass = original_getpass

    records = frame.to_dict(orient="records")
    ok_value = records[0].get("ok") if records else None
    return {
        "ok": bool(records) and str(ok_value) == "1",
        "row_count": int(len(frame)),
        "records": records,
    }


def _run_psycopg2_query(
    user: str,
    password: str,
    host: str,
    port: int,
    query: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    psycopg2 = importlib.import_module("psycopg2")
    conn = psycopg2.connect(
        dbname="wrds",
        user=user,
        password=password,
        host=host,
        port=port,
        connect_timeout=timeout_seconds,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc.name for desc in cursor.description or []]
    finally:
        conn.close()

    records = [dict(zip(columns, row)) for row in rows]
    ok_value = records[0].get("ok") if records else None
    return {
        "ok": bool(records) and str(ok_value) == "1",
        "row_count": len(records),
        "records": records,
    }


def run_wrds_smoke(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    imports = {
        "wrds": _import_check("wrds"),
        "psycopg2": _import_check("psycopg2"),
    }
    dotenv_path = repo_root / args.dotenv
    creds, missing_env = _load_credentials(dotenv_path)

    attempts: dict[str, Any] = {}
    failure_reasons: list[str] = []
    if not imports["wrds"]["ok"]:
        failure_reasons.append("wrds_import_failed")
    if not imports["psycopg2"]["ok"]:
        failure_reasons.append("psycopg2_import_failed")
    if missing_env:
        failure_reasons.append("missing_wrds_credentials")

    if not failure_reasons:
        try:
            attempts["wrds_connection"] = _run_wrds_query(
                user=creds["WRDS_USER"],
                password=creds["WRDS_PASS"],
                query=args.query,
            )
            if not attempts["wrds_connection"]["ok"]:
                failure_reasons.append("wrds_live_query_failed")
        except Exception as exc:
            attempts["wrds_connection"] = {
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            failure_reasons.append("wrds_live_query_failed")

        try:
            attempts["psycopg2_connection"] = _run_psycopg2_query(
                user=creds["WRDS_USER"],
                password=creds["WRDS_PASS"],
                host=creds["WRDS_DB_HOST"],
                port=int(creds["WRDS_DB_PORT"]),
                query=args.query,
                timeout_seconds=int(args.timeout_seconds),
            )
            if not attempts["psycopg2_connection"]["ok"]:
                failure_reasons.append("psycopg2_live_query_failed")
        except Exception as exc:
            attempts["psycopg2_connection"] = {
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            failure_reasons.append("psycopg2_live_query_failed")

    status = "passed" if not failure_reasons else "failed"
    report = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "status": status,
            "failure_reasons": failure_reasons,
            "dotenv_path": str(dotenv_path),
            "credentials_missing": missing_env,
        },
        "runtime": {
            "python_executable": os.path.realpath(os.sys.executable),
            "query": args.query,
            "timeout_seconds": int(args.timeout_seconds),
        },
        "host_metadata": {
            "wrds_user": creds.get("WRDS_USER", ""),
            "wrds_db_host": creds.get("WRDS_DB_HOST", ""),
            "wrds_db_port": creds.get("WRDS_DB_PORT", ""),
        },
        "imports": imports,
        "attempts": attempts,
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dotenv", default=".env")
    parser.add_argument("--query", default="select 1 as ok")
    parser.add_argument("--timeout-seconds", type=int, default=15)
    parser.add_argument(
        "--output",
        default="reports/environment/wrds_smoke_v1.json",
        help="Output JSON artifact path relative to the repo root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_wrds_smoke(args)
    print(
        f"[wrds-smoke] status={report['status']} failure_reasons={report['summary']['failure_reasons']}"
    )
    print(f"[wrds-smoke] report -> {args.output}")


if __name__ == "__main__":
    main()
