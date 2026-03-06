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
from semantic_ai_washing.director.core.branching import validate_iteration_boundaries
from semantic_ai_washing.director.core.cost import CostController
from semantic_ai_washing.director.core.decision import DecisionEngine
from semantic_ai_washing.director.core.optimizer import DirectorOptimizer
from semantic_ai_washing.director.core.executor import RunbookExecutor
from semantic_ai_washing.director.core.planner import PlannerEngine, write_plan_manifest
from semantic_ai_washing.director.core.review import ReviewEngine, load_approved_review_summaries
from semantic_ai_washing.director.core.render import (
    is_rendered_roadmap_fresh,
    render_roadmap_markdown,
)
from semantic_ai_washing.director.core.roadmap_model import (
    load_remediation_library,
    load_roadmap_model,
    resolve_model_path,
)
from semantic_ai_washing.director.core.security import (
    ensure_openai_key_if_enabled,
    scan_repo_for_secrets,
)
from semantic_ai_washing.director.core.snapshot import SnapshotIngestor
from semantic_ai_washing.director.core.state import StateCompiler
from semantic_ai_washing.director.core.utils import (
    dump_json,
    git_info,
    load_json,
    now_utc_iso,
    repository_root,
    sha256_file,
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

    if not args.roadmap and not args.roadmap_model:
        raise ValueError("Provide --roadmap-model or --roadmap.")

    ingestor = SnapshotIngestor(paths.snapshots_dir)
    manifest = ingestor.ingest(
        protocol_path=args.protocol,
        roadmap_path=args.roadmap or "",
        roadmap_model_path=args.roadmap_model or "",
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


def _render_roadmap_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    model_path = resolve_model_path(
        repo_root, args.roadmap_model or profile.get("roadmap_model_path", "")
    )
    model = load_roadmap_model(model_path)
    output_path = Path(
        args.output or (Path(repo_root) / "docs" / "director" / "roadmap_master.md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = render_roadmap_markdown(
        model=model,
        source_model=str(model_path),
        source_sha256=sha256_file(model_path),
        approved_reviews=load_approved_review_summaries(paths.reviews_dir),
    )
    output_path.write_text(markdown, encoding="utf-8")
    print(f"[director] roadmap rendered: {output_path}")
    return 0


def _optimize_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    compiler = StateCompiler(repo_root=repo_root)
    compiler.compile(
        iteration_state_path=str(paths.snapshots_dir / "iteration_state.json"),
        output_path=str(paths.snapshots_dir / "iteration_state_compiled.json"),
    )
    optimizer = DirectorOptimizer(
        repo_root=repo_root,
        roadmap_model_path=str(
            resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
        ),
        remediation_library_path=str(
            resolve_model_path(repo_root, profile.get("remediation_library_path", ""))
        ),
        optimization_dir=str(paths.optimization_dir),
        decisions_dir=str(paths.decisions_dir),
        weights=profile.get("optimization_weights", {}),
        emit_patch=bool(profile.get("feature_flags", {}).get("emit_roadmap_patch", True)),
    )
    result = optimizer.optimize(
        focus_iteration=str(args.iteration or ""),
        focus_phase=str(args.phase or ""),
    )
    print(json.dumps(result.as_deterministic_dict(), indent=2))
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


def _review_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    engine = ReviewEngine(
        repo_root=repo_root,
        paths=paths,
        roadmap_model_path=str(
            resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
        ),
        iteration_log_path=str(Path(repo_root) / "docs" / "iteration_log.md"),
    )
    review = engine.generate_review(iteration_id=args.iteration, phase_name=args.phase or "")
    print(json.dumps(review.as_deterministic_dict(), indent=2))
    return 0


def _approve_review_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    engine = ReviewEngine(
        repo_root=repo_root,
        paths=paths,
        roadmap_model_path=str(
            resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
        ),
        iteration_log_path=str(Path(repo_root) / "docs" / "iteration_log.md"),
    )
    approval = engine.approve_review(
        review_file=args.review_file,
        decision=args.decision,
        accept_patch=args.accept_patch,
    )
    print(json.dumps(approval.as_deterministic_dict(), indent=2))
    return 0


def _apply_review_patch_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    model_path = resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
    engine = ReviewEngine(
        repo_root=repo_root,
        paths=paths,
        roadmap_model_path=str(model_path),
        iteration_log_path=str(Path(repo_root) / "docs" / "iteration_log.md"),
    )
    result = engine.apply_review_patch(args.approval_file)

    model = load_roadmap_model(model_path)
    roadmap_doc = Path(repo_root) / "docs" / "director" / "roadmap_master.md"
    roadmap_doc.write_text(
        render_roadmap_markdown(
            model=model,
            source_model=str(model_path),
            source_sha256=sha256_file(model_path),
            approved_reviews=load_approved_review_summaries(paths.reviews_dir),
        ),
        encoding="utf-8",
    )

    protocol_path = Path(repo_root) / "docs" / "director" / "implementation_protocol_master.md"
    iteration_log_path = Path(repo_root) / "docs" / "iteration_log.md"
    ingest_result: dict[str, Any] = {}
    if protocol_path.exists() and iteration_log_path.exists():
        ingestor = SnapshotIngestor(paths.snapshots_dir)
        ingest_result = ingestor.ingest(
            protocol_path=str(protocol_path),
            roadmap_path="",
            roadmap_model_path=str(model_path),
            iteration_log_path=str(iteration_log_path),
            atlas_search="",
            atlas_limit=20,
            enable_atlas=False,
        )
    result["rendered_roadmap"] = str(roadmap_doc)
    result["ingest"] = ingest_result
    print(json.dumps(result, indent=2))
    return 0


def _kickoff_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    config = load_configs(paths)
    profile = config.get("project_profile", {})
    engine = ReviewEngine(
        repo_root=repo_root,
        paths=paths,
        roadmap_model_path=str(
            resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
        ),
        iteration_log_path=str(Path(repo_root) / "docs" / "iteration_log.md"),
    )
    report = engine.kickoff(args.iteration)
    print(json.dumps(report.as_deterministic_dict(), indent=2))
    return 0 if report.status == "ready" else 2


def _status_command(args: argparse.Namespace) -> int:
    repo_root = repository_root(args.repo_root)
    paths = get_director_paths(repo_root)
    ensure_director_dirs(paths)

    runbooks = sorted(paths.plans_dir.glob("runbook_*.yaml"), key=lambda p: p.stat().st_mtime)
    states = sorted(paths.runs_dir.glob("execution_state_*.json"), key=lambda p: p.stat().st_mtime)
    deferred_records = sorted(
        paths.decisions_dir.glob("deferred_*.json"), key=lambda p: p.stat().st_mtime
    )
    recommendations = sorted(
        paths.optimization_dir.glob("recommendation_*.json"), key=lambda p: p.stat().st_mtime
    )
    reviews = sorted(paths.reviews_dir.glob("*_review.json"), key=lambda p: p.stat().st_mtime)
    approvals = sorted(paths.reviews_dir.glob("*_approval.json"), key=lambda p: p.stat().st_mtime)
    kickoffs = sorted(
        paths.reviews_dir.glob("iteration_*_kickoff.json"), key=lambda p: p.stat().st_mtime
    )
    latest_recommendation_id = ""
    if recommendations:
        latest_recommendation_id = recommendations[-1].stem.replace("recommendation_", "")
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

    latest_approval_payload = (load_json(approvals[-1], default={}) if approvals else {}) or {}
    branch_policy_summary = {}
    try:
        config = load_configs(paths)
        profile = config.get("project_profile", {})
        model_path = resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
        model = load_roadmap_model(model_path)
        branch_policy_summary = model.branching_policy.model_dump(mode="json")
    except Exception:
        branch_policy_summary = {}

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
        "latest_recommendation_id": latest_recommendation_id,
        "latest_recommendation": str(recommendations[-1]) if recommendations else "",
        "latest_review": str(reviews[-1]) if reviews else "",
        "latest_review_approval": str(approvals[-1]) if approvals else "",
        "latest_kickoff": str(kickoffs[-1]) if kickoffs else "",
        "next_iteration_authorized": bool(
            latest_approval_payload.get("next_iteration_authorized", False)
        ),
        "branching_policy": branch_policy_summary,
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
    pyvenv_cfg = Path(repo_root) / ".venv" / "pyvenv.cfg"
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

    tooling_policies = config.get("tooling_policy", {}).get("policies", [])
    atlas_policy = next(
        (
            item
            for item in tooling_policies
            if isinstance(item, dict) and item.get("tool") == "atlas"
        ),
        {},
    )
    wrapper_path = atlas_policy.get("wrapper_path", "")
    if wrapper_path:
        wrapper_file = Path(wrapper_path)
        if not wrapper_file.is_absolute():
            wrapper_file = Path(repo_root) / wrapper_file
        checks.append(
            {
                "name": "atlas_wrapper",
                "ok": wrapper_file.exists(),
                "detail": str(wrapper_file),
            }
        )

    expected_version = str(atlas_policy.get("expected_repo_venv_python", "")).strip()
    expected_home = str(atlas_policy.get("expected_repo_venv_home", "")).strip()
    if pyvenv_cfg.exists():
        cfg_text = pyvenv_cfg.read_text(encoding="utf-8")
        version_ok = expected_version in cfg_text if expected_version else True
        home_ok = expected_home in cfg_text if expected_home else True
        checks.append(
            {
                "name": "repo_venv_policy",
                "ok": version_ok and home_ok,
                "detail": cfg_text.strip().replace("\n", "; "),
            }
        )
    else:
        checks.append(
            {
                "name": "repo_venv_policy",
                "ok": False,
                "detail": f"{pyvenv_cfg} not found",
            }
        )

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

    profile = config.get("project_profile", {})
    model_path = resolve_model_path(repo_root, profile.get("roadmap_model_path", ""))
    remediation_path = resolve_model_path(repo_root, profile.get("remediation_library_path", ""))
    roadmap_doc = Path(repo_root) / "docs" / "director" / "roadmap_master.md"

    loaded_model = None
    try:
        loaded_model = load_roadmap_model(model_path)
        checks.append(
            {
                "name": "roadmap_model_schema",
                "ok": True,
                "detail": str(model_path),
            }
        )
    except Exception as exc:
        checks.append(
            {
                "name": "roadmap_model_schema",
                "ok": False,
                "detail": str(exc),
            }
        )
    checks.append(
        {
            "name": "branching_policy_present",
            "ok": loaded_model is not None and loaded_model.branching_policy is not None,
            "detail": str(model_path),
        }
    )
    if loaded_model is not None:
        boundary_checks = validate_iteration_boundaries(loaded_model)
        checks.append(
            {
                "name": "iteration_boundary_phases",
                "ok": all(item["ok"] for item in boundary_checks),
                "detail": boundary_checks,
            }
        )

    try:
        load_remediation_library(remediation_path)
        checks.append(
            {
                "name": "remediation_library_schema",
                "ok": True,
                "detail": str(remediation_path),
            }
        )
    except Exception as exc:
        checks.append(
            {
                "name": "remediation_library_schema",
                "ok": False,
                "detail": str(exc),
            }
        )
    checks.append(
        {
            "name": "roadmap_render_fresh",
            "ok": is_rendered_roadmap_fresh(model_path, roadmap_doc),
            "detail": str(roadmap_doc),
        }
    )

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
    ingest_cmd.add_argument("--roadmap")
    ingest_cmd.add_argument("--roadmap-model")
    ingest_cmd.add_argument("--iteration-log", required=True)
    ingest_cmd.add_argument("--atlas-search", default="")
    ingest_cmd.add_argument("--atlas-limit", type=int, default=20)
    ingest_cmd.add_argument("--enable-atlas", action="store_true")
    ingest_cmd.set_defaults(func=_ingest_command)

    plan_cmd = subparsers.add_parser("plan", help="Generate runbook + plan markdown")
    plan_cmd.add_argument("--iteration", required=True)
    plan_cmd.add_argument("--phase", required=True)
    plan_cmd.set_defaults(func=_plan_command)

    render_cmd = subparsers.add_parser(
        "render-roadmap", help="Render roadmap Markdown from the canonical YAML model"
    )
    render_cmd.add_argument("--roadmap-model")
    render_cmd.add_argument("--output")
    render_cmd.set_defaults(func=_render_roadmap_command)

    optimize_cmd = subparsers.add_parser(
        "optimize", help="Compile task readiness and next-work recommendations"
    )
    optimize_cmd.add_argument("--iteration")
    optimize_cmd.add_argument("--phase")
    optimize_cmd.set_defaults(func=_optimize_command)

    review_cmd = subparsers.add_parser(
        "review", help="Generate iteration or phase review artifacts"
    )
    review_cmd.add_argument("--iteration", required=True)
    review_cmd.add_argument("--phase")
    review_cmd.set_defaults(func=_review_command)

    approve_review_cmd = subparsers.add_parser(
        "approve-review", help="Approve or defer a review and record accepted patch changes"
    )
    approve_review_cmd.add_argument("--review-file", required=True)
    approve_review_cmd.add_argument("--decision", required=True, choices=["approve", "defer"])
    approve_review_cmd.add_argument("--accept-patch", default="none")
    approve_review_cmd.set_defaults(func=_approve_review_command)

    apply_review_patch_cmd = subparsers.add_parser(
        "apply-review-patch",
        help="Apply accepted roadmap changes from a review approval artifact",
    )
    apply_review_patch_cmd.add_argument("--approval-file", required=True)
    apply_review_patch_cmd.set_defaults(func=_apply_review_patch_command)

    kickoff_cmd = subparsers.add_parser(
        "kickoff", help="Validate iteration kickoff branch context and approval state"
    )
    kickoff_cmd.add_argument("--iteration", required=True)
    kickoff_cmd.set_defaults(func=_kickoff_command)

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
