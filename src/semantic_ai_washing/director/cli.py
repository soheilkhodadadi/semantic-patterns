"""CLI entrypoint for the autonomous director package."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.config import (
    ensure_default_configs,
    ensure_director_dirs,
    get_director_paths,
    load_configs,
    required_file_paths,
)
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.decision import DecisionEngine
from semantic_ai_washing.director.core.executor import RunbookExecutor
from semantic_ai_washing.director.core.planner import PlannerEngine, write_plan_manifest
from semantic_ai_washing.director.core.security import (
    ensure_openai_key_if_enabled,
    scan_repo_for_secrets,
)
from semantic_ai_washing.director.core.snapshot import SnapshotIngestor
from semantic_ai_washing.director.core.state import StateCompiler
from semantic_ai_washing.director.core.utils import (
    dump_json,
    git_info,
    now_utc_iso,
    repository_root,
)


def _init_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    ensure_director_dirs(paths)
    ensure_default_configs(paths)

    placeholders = {
        paths.snapshots_dir / "protocol_summary.json": {
            "source_path": "",
            "key_points": [],
            "gates": [],
            "risks": [],
            "ingested_at": now_utc_iso(),
        },
        paths.snapshots_dir / "roadmap_summary.json": {
            "source_path": "",
            "key_points": [],
            "gates": [],
            "risks": [],
            "ingested_at": now_utc_iso(),
        },
        paths.snapshots_dir / "iteration_state.json": {
            "source_path": "",
            "iterations": [],
            "phases": [],
            "last_successful_gate": "unknown",
            "ingested_at": now_utc_iso(),
        },
    }
    for path, payload in placeholders.items():
        if not path.exists():
            dump_json(path, payload)

    print(f"[director] initialized under {paths.director_root}")
    return 0


def _ingest_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    ensure_director_dirs(paths)
    ensure_default_configs(paths)

    ingestor = SnapshotIngestor(paths.snapshots_dir)
    manifest = ingestor.ingest(
        protocol_path=args.protocol,
        roadmap_path=args.roadmap,
        iteration_log_path=args.iteration_log,
        atlas_search=args.atlas_search or "",
        atlas_limit=args.atlas_limit,
        enable_atlas=args.enable_atlas,
    )

    # Compile state graph from the freshly ingested iteration snapshot.
    compiler = StateCompiler(repo_root=repo_root)
    compiled = compiler.compile(
        iteration_state_path=str(paths.snapshots_dir / "iteration_state.json"),
        output_path=str(paths.snapshots_dir / "iteration_state_compiled.json"),
    )

    print("[director] ingestion complete")
    print(
        json.dumps(
            {"manifest": manifest, "compiled_state": compiled["last_gate_status"]}, indent=2
        )
    )
    return 0


def _plan_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)

    planner = PlannerEngine(
        repo_root=repo_root,
        config=config,
        snapshots_dir=str(paths.snapshots_dir),
        plans_dir=str(paths.plans_dir),
        decisions_dir=str(paths.decisions_dir),
        runs_dir=str(paths.runs_dir),
        cache_dir=str(paths.cache_dir),
    )
    result = planner.generate(iteration_id=args.iteration, phase_name=args.phase)

    manifest_path = paths.plans_dir / f"manifest_{result['runbook_id']}.json"
    write_plan_manifest(result, str(manifest_path))

    print(f"[director] plan generated: {result['runbook_id']}")
    print(f"[director] runbook: {result['runbook_file']}")
    print(f"[director] plan: {result['plan_file']}")
    print(f"[director] decision scaffold: {result['decision_file']}")
    print(f"[director] manifest: {manifest_path}")
    return 0


def _decide_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    engine = DecisionEngine(decisions_dir=paths.decisions_dir)

    if args.blocker_file and args.execution_state:
        raise ValueError("Provide only one of --blocker-file or --execution-state.")
    if not args.blocker_file and not args.execution_state:
        raise ValueError("Provide either --blocker-file or --execution-state.")

    blocker_payload = args.blocker_file or args.execution_state
    try:
        decision, out_path = engine.from_blocker_file(
            blocker_file=blocker_payload,
            selected_option_id=args.select_option,
            require_manual_selection=not args.auto_select,
        )
    except ValueError as exc:
        print(f"[director] invalid blocker payload: {exc}")
        print(
            "[director] expected blocker event JSON or execution_state JSON with `blocker`. "
            "For execution state use: --execution-state <path>"
        )
        return 2

    print(f"[director] decision file: {out_path}")
    print(json.dumps(decision.as_deterministic_dict(), indent=2))
    return 0


def _defer_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    engine = DecisionEngine(decisions_dir=paths.decisions_dir)

    deferred, out_path = engine.defer(
        decision_file=args.decision_file,
        until_iteration=args.until_iteration,
        until_phase=args.until_phase,
        criteria=args.criteria,
        runs_dir=paths.runs_dir,
    )
    print(f"[director] deferred blocker record: {out_path}")
    print(json.dumps(deferred.as_deterministic_dict(), indent=2))
    return 0


def _run_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    executor = RunbookExecutor(
        repo_root=repo_root,
        runs_dir=paths.runs_dir,
        decisions_dir=paths.decisions_dir,
        autonomy_policy=config.get("autonomy_policy", {}),
    )

    result = executor.run(runbook_path=args.runbook, mode=args.mode, resume=args.resume)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "passed" else 2


def _status_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    ensure_director_dirs(paths)

    runbooks = sorted(paths.plans_dir.glob("runbook_*.yaml"), key=lambda p: p.stat().st_mtime)
    states = sorted(paths.runs_dir.glob("execution_state_*.json"), key=lambda p: p.stat().st_mtime)
    deferred_records = sorted(
        paths.decisions_dir.glob("deferred_*.json"), key=lambda p: p.stat().st_mtime
    )
    active_deferred: list[dict[str, Any]] = []
    for record in deferred_records:
        payload = json.loads(record.read_text(encoding="utf-8"))
        if payload.get("status") == "active":
            active_deferred.append(
                {
                    "record": str(record),
                    "decision_id": payload.get("decision_id", ""),
                    "blocker_id": payload.get("blocker_id", ""),
                    "until_iteration": payload.get("until_iteration", ""),
                    "until_phase": payload.get("until_phase", ""),
                }
            )

    payload = {
        "repo_root": str(paths.repo_root),
        "git": git_info(repo_root),
        "snapshots": {
            "protocol": str(paths.snapshots_dir / "protocol_summary.json"),
            "roadmap": str(paths.snapshots_dir / "roadmap_summary.json"),
            "iteration": str(paths.snapshots_dir / "iteration_state.json"),
        },
        "latest_runbook": str(runbooks[-1]) if runbooks else "",
        "latest_execution_state": str(states[-1]) if states else "",
        "active_deferred_blockers": active_deferred,
    }
    print(json.dumps(payload, indent=2))
    return 0


def _cost_report_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)

    controller = CostController(
        policy=config.get("cost_policy", {}),
        usage_file=paths.runs_dir / "cost_usage.jsonl",
        cache_dir=paths.cache_dir / "llm",
    )
    totals = controller.totals()
    payload = {
        "totals": totals,
        "usage_file": str(paths.runs_dir / "cost_usage.jsonl"),
        "cache_dir": str(paths.cache_dir / "llm"),
    }
    print(json.dumps(payload, indent=2))
    return 0


def _doctor_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    ensure_director_dirs(paths)
    ensure_default_configs(paths)
    config = load_configs(paths)

    checks: list[dict[str, Any]] = []

    # 1) Required files.
    missing = [str(path) for path in required_file_paths(paths) if not path.exists()]
    checks.append(
        {
            "name": "required_files",
            "ok": len(missing) == 0,
            "detail": "all required files exist" if not missing else f"missing: {missing}",
        }
    )

    # 2) venv pip health.
    venv_python = Path(repo_root) / ".venv" / "bin" / "python"
    if venv_python.exists():
        proc = subprocess.run(
            [str(venv_python), "-m", "pip", "--version"],
            text=True,
            capture_output=True,
            check=False,
        )
        checks.append(
            {
                "name": "venv_pip",
                "ok": proc.returncode == 0,
                "detail": proc.stdout.strip() if proc.returncode == 0 else proc.stderr.strip(),
            }
        )
    else:
        checks.append({"name": "venv_pip", "ok": False, "detail": ".venv/bin/python not found"})

    # 3) make doctor (optional).
    if not args.skip_make_doctor:
        proc = subprocess.run(
            ["make", "doctor"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        checks.append(
            {
                "name": "make_doctor",
                "ok": proc.returncode == 0,
                "detail": (proc.stdout + "\n" + proc.stderr).strip()[-1200:],
            }
        )

    # 4) Git cleanliness (optional strict failure).
    git_status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    dirty = bool(git_status.stdout.strip())
    checks.append(
        {
            "name": "git_clean",
            "ok": (not dirty) or (not args.require_clean),
            "detail": "clean" if not dirty else "worktree has pending changes",
        }
    )

    # 5) Secret scan over tracked files.
    findings = scan_repo_for_secrets(repo_root)
    secret_ok = len(findings) == 0 or (not args.strict_secrets)
    checks.append(
        {
            "name": "secret_scan",
            "ok": secret_ok,
            "detail": "no tracked secrets found"
            if len(findings) == 0
            else f"findings={len(findings)}",
            "findings": findings[:20],
        }
    )

    # 6) API key guardrail when llm enabled.
    llm_enabled = bool(config.get("cost_policy", {}).get("llm_enabled", False))
    key_ok, key_detail = ensure_openai_key_if_enabled(llm_enabled)
    checks.append({"name": "openai_key", "ok": key_ok, "detail": key_detail})

    ok = all(item["ok"] for item in checks)
    payload = {
        "checked_at": now_utc_iso(),
        "ok": ok,
        "checks": checks,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for item in checks:
            status = "OK" if item["ok"] else "FAIL"
            print(f"[{status}] {item['name']}: {item['detail']}")

    return 0 if ok else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Autonomous project director CLI")
    parser.add_argument("--repo-root", default=".")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="Initialize director workspace")
    init_cmd.set_defaults(func=_init_command)

    ingest_cmd = subparsers.add_parser("ingest", help="Ingest snapshots from canonical docs")
    ingest_cmd.add_argument("--protocol", required=True)
    ingest_cmd.add_argument("--roadmap", required=True)
    ingest_cmd.add_argument("--iteration-log", required=True)
    ingest_cmd.add_argument("--atlas-search", default="")
    ingest_cmd.add_argument("--atlas-limit", type=int, default=20)
    ingest_cmd.add_argument("--enable-atlas", action="store_true")
    ingest_cmd.set_defaults(func=_ingest_command)

    plan_cmd = subparsers.add_parser("plan", help="Generate runbook + plan markdown")
    plan_cmd.add_argument("--iteration", required=True)
    plan_cmd.add_argument("--phase", required=True)
    plan_cmd.set_defaults(func=_plan_command)

    decide_cmd = subparsers.add_parser("decide", help="Rank recovery options for a blocker")
    decide_cmd.add_argument("--blocker-file")
    decide_cmd.add_argument("--execution-state")
    decide_cmd.add_argument("--select-option", default=None)
    decide_cmd.add_argument("--auto-select", action="store_true")
    decide_cmd.set_defaults(func=_decide_command)

    defer_cmd = subparsers.add_parser("defer", help="Defer a blocker with expiry metadata")
    defer_cmd.add_argument("--decision-file", required=True)
    defer_cmd.add_argument("--until-iteration", required=True)
    defer_cmd.add_argument("--until-phase", required=True)
    defer_cmd.add_argument("--criteria", required=True)
    defer_cmd.set_defaults(func=_defer_command)

    run_cmd = subparsers.add_parser("run", help="Execute runbook")
    run_cmd.add_argument("--runbook", required=True)
    run_cmd.add_argument("--mode", default="autonomous", choices=["autonomous", "advisory"])
    run_cmd.add_argument("--resume", action="store_true")
    run_cmd.set_defaults(func=_run_command)

    status_cmd = subparsers.add_parser("status", help="Show director status")
    status_cmd.set_defaults(func=_status_command)

    cost_cmd = subparsers.add_parser(
        "cost-report", help="Show cumulative LLM usage and budget totals"
    )
    cost_cmd.set_defaults(func=_cost_report_command)

    doctor_cmd = subparsers.add_parser("doctor", help="Run director environment and policy checks")
    doctor_cmd.add_argument("--strict-secrets", action="store_true")
    doctor_cmd.add_argument("--skip-make-doctor", action="store_true")
    doctor_cmd.add_argument("--require-clean", action="store_true")
    doctor_cmd.add_argument("--json", action="store_true")
    doctor_cmd.set_defaults(func=_doctor_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
