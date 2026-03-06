"""Pydantic schemas for the autonomous project director."""

from __future__ import annotations

import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "1.0.0"
ROADMAP_SCHEMA_VERSION = "1.2.0"


class DeterministicModel(BaseModel):
    """Base model with deterministic JSON serialization helpers."""

    schema_version: str = Field(default=SCHEMA_VERSION)

    def as_deterministic_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)

    def as_deterministic_json(self) -> str:
        return json.dumps(self.as_deterministic_dict(), sort_keys=True, separators=(",", ":"))


class ArtifactSpec(DeterministicModel):
    artifact_id: str
    path: str
    kind: Literal[
        "file",
        "directory",
        "json",
        "csv",
        "markdown",
        "report",
        "dataset",
        "model",
        "parquet",
    ]
    required: bool = True
    fingerprint_required: bool = False
    produced_by: list[str] = Field(default_factory=list)
    consumed_by: list[str] = Field(default_factory=list)


class ConditionSpec(DeterministicModel):
    condition_id: str
    kind: Literal[
        "artifact_exists",
        "csv_row_count_gte",
        "json_field_compare",
        "file_hash_present",
        "manual_artifact_present",
        "sentence_fragment_rate_lte",
        "indexed_years_include",
    ]
    target: str
    operator: Literal["==", "!=", ">=", "<=", ">", "<", "in", "not_in"] = "=="
    expected: Any
    on_fail: Literal["block", "warn", "reroute"] = "block"
    message: str = ""
    reroute_to: list[str] = Field(default_factory=list)


class PolicySpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    policy_id: str
    kind: Literal[
        "dataset_freeze",
        "methodology",
        "model_governance",
        "analysis_governance",
        "tooling",
        "data_governance",
    ]
    description: str
    enforcement: Literal["hard", "soft"] = "hard"
    targets: list[str] = Field(default_factory=list)
    value: Any = None


class DataLayerSpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    layer_id: str
    canonical_path: str
    format: Literal["csv", "json", "markdown", "parquet", "mixed", "directory"]
    required_fields: list[str] = Field(default_factory=list)
    review_export_path: str = ""
    description: str = ""


class SourceWindowSpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    source_window_id: str
    years: list[str] = Field(default_factory=list)
    source_root_ref: str
    status: Literal["active", "planned", "deferred", "historical"] = "planned"
    availability_condition: Optional[ConditionSpec] = None


class ToolingPolicySpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    policy_id: str
    tool: str
    mode: str
    repo_root_uv_run_forbidden: bool = True
    required_runner: str = ""
    wrapper_path: str = ""
    expected_repo_venv_python: str = ""
    expected_repo_venv_home: str = ""


class BranchingPolicySpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    integration_branch_template: str
    work_branch_template: str
    merge_target: str
    preferred_merge_strategy: str
    require_review_approval_before_next_iteration: bool = True
    require_review_approval_before_main_merge: bool = True
    suggest_new_chat_at_iteration_boundary: bool = True
    starter_prompt_required: bool = True
    tag_template: str
    closeout_validation_commands: list[str] = Field(default_factory=list)


class ApiAssistivePromptSpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    label_set: list[str] = Field(default_factory=list)
    confidence_bands: list[str] = Field(default_factory=list)
    system_prompt: str
    user_prompt_template: str
    reference_rubric_path: str


class ApiAssistiveSmokeSpec(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    sample_input: str
    report_path: str = ""
    timeout_seconds: int = Field(default=60, ge=1)
    store: bool = False
    max_output_tokens: int = Field(default=200, ge=1)
    min_tokens: int = Field(default=12, ge=1)
    max_tokens: int = Field(default=120, ge=1)
    require_fragment_score_max: float = Field(default=0.0, ge=0.0)


class ApiAssistivePolicy(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    mode: str
    provider: str
    transport: str
    env_var: str
    model: str
    request: dict[str, Any] = Field(default_factory=dict)
    budget: dict[str, Any] = Field(default_factory=dict)
    prompt_spec: ApiAssistivePromptSpec
    selection: ApiAssistiveSmokeSpec
    telemetry: dict[str, Any] = Field(default_factory=dict)
    usage_policy: dict[str, Any] = Field(default_factory=dict)
    smoke_output: dict[str, Any] = Field(default_factory=dict)

    @field_validator("mode")
    @classmethod
    def _validate_mode(cls, value: str) -> str:
        if value != "assistive_only":
            raise ValueError("ApiAssistivePolicy.mode must equal `assistive_only`")
        return value

    @field_validator("env_var")
    @classmethod
    def _validate_env_var(cls, value: str) -> str:
        if value != "OPENAI_API_KEY":
            raise ValueError("ApiAssistivePolicy.env_var must equal `OPENAI_API_KEY`")
        return value

    @field_validator("budget")
    @classmethod
    def _validate_budget(cls, value: dict[str, Any]) -> dict[str, Any]:
        if int(value.get("max_live_requests_per_run", 0) or 0) != 1:
            raise ValueError("ApiAssistivePolicy budget must cap live requests at exactly 1")
        return value

    @field_validator("telemetry")
    @classmethod
    def _validate_telemetry(cls, value: dict[str, Any]) -> dict[str, Any]:
        if bool(value.get("cache_allowed", True)):
            raise ValueError("ApiAssistivePolicy telemetry.cache_allowed must be false")
        return value

    @field_validator("request")
    @classmethod
    def _validate_request(cls, value: dict[str, Any]) -> dict[str, Any]:
        if "max_output_tokens" not in value:
            raise ValueError("ApiAssistivePolicy request.max_output_tokens is required")
        if "timeout_seconds" not in value:
            raise ValueError("ApiAssistivePolicy request.timeout_seconds is required")
        if "store" not in value:
            raise ValueError("ApiAssistivePolicy request.store is required")
        return value

    @field_validator("prompt_spec")
    @classmethod
    def _validate_prompt_spec(cls, value: ApiAssistivePromptSpec) -> ApiAssistivePromptSpec:
        if value.label_set != ["Actionable", "Speculative", "Irrelevant"]:
            raise ValueError(
                "ApiAssistivePolicy prompt_spec.label_set must equal "
                "[Actionable, Speculative, Irrelevant]"
            )
        if value.confidence_bands != ["high", "medium", "low"]:
            raise ValueError(
                "ApiAssistivePolicy prompt_spec.confidence_bands must equal [high, medium, low]"
            )
        return value

    @field_validator("smoke_output")
    @classmethod
    def _validate_smoke_output(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not str(value.get("report_path", "")).strip():
            raise ValueError("ApiAssistivePolicy smoke_output.report_path is required")
        return value


class TaskSpec(DeterministicModel):
    task_id: str
    title: str
    description: str
    iteration_id: str
    phase_id: str
    kind: Literal[
        "diagnostic",
        "build",
        "validation",
        "manual",
        "decision",
        "analysis",
        "reporting",
        "remediation",
    ]
    depends_on: list[str] = Field(default_factory=list)
    inputs: list[ArtifactSpec] = Field(default_factory=list)
    outputs: list[ArtifactSpec] = Field(default_factory=list)
    preconditions: list[ConditionSpec] = Field(default_factory=list)
    quality_checks: list[ConditionSpec] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    manual_handoff: bool = False
    risks: list[str] = Field(default_factory=list)
    estimated_effort: int = Field(default=3, ge=1, le=10)
    risk_reduction: int = Field(default=3, ge=1, le=10)
    automation_level: Literal["full", "partial", "manual"] = "partial"
    on_fail: Literal["block", "warn", "reroute"] = "block"
    reroute_to: list[str] = Field(default_factory=list)
    evidence_required: bool = True
    tags: list[str] = Field(default_factory=list)
    gate_class: Literal["science", "data", "ops", "manual", "release"] = "ops"


class PhaseSpec(DeterministicModel):
    phase_id: str
    title: str
    goal: str
    depends_on: list[str] = Field(default_factory=list)
    canonical: bool = True
    required_artifacts: list[str] = Field(default_factory=list)
    tasks: list[TaskSpec] = Field(default_factory=list)
    lifecycle_state: Literal[
        "planned",
        "active",
        "completed",
        "historical",
        "superseded",
        "deferred",
    ] = "planned"
    source_window_id: str = ""
    tags: list[str] = Field(default_factory=list)


class IterationSpec(DeterministicModel):
    iteration_id: str
    title: str
    goal: str
    entry_criteria: list[str] = Field(default_factory=list)
    exit_criteria: list[str] = Field(default_factory=list)
    phases: list[PhaseSpec] = Field(default_factory=list)


class OptimizationWeights(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    unblock_value: int = Field(default=5, ge=0)
    critical_path_depth: int = Field(default=4, ge=0)
    risk_reduction: int = Field(default=3, ge=0)
    automation_bonus: int = Field(default=2, ge=0)
    manual_effort_penalty: int = Field(default=2, ge=0)
    precondition_gap_penalty: int = Field(default=4, ge=0)
    quality_failure_penalty: int = Field(default=5, ge=0)


class RoadmapModel(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    project: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    branching_policy: BranchingPolicySpec
    policies: list[PolicySpec] = Field(default_factory=list)
    data_layers: list[DataLayerSpec] = Field(default_factory=list)
    source_windows: list[SourceWindowSpec] = Field(default_factory=list)
    tooling_policies: list[ToolingPolicySpec] = Field(default_factory=list)
    iterations: list[IterationSpec] = Field(default_factory=list)


class TaskStateSnapshot(DeterministicModel):
    task_id: str
    phase_id: str
    iteration_id: str
    status: Literal[
        "satisfied",
        "ready",
        "waiting_on_deps",
        "blocked_precondition",
        "blocked_quality",
        "blocked_manual",
        "deferred",
    ]
    dependency_ids: list[str] = Field(default_factory=list)
    missing_dependencies: list[str] = Field(default_factory=list)
    failed_preconditions: list[str] = Field(default_factory=list)
    failed_quality_checks: list[str] = Field(default_factory=list)
    missing_outputs: list[str] = Field(default_factory=list)
    blocked_policy_ids: list[str] = Field(default_factory=list)
    score: float = 0.0
    context: dict[str, Any] = Field(default_factory=dict)


class PhaseStateSnapshot(DeterministicModel):
    phase_id: str
    iteration_id: str
    status: Literal[
        "satisfied",
        "ready",
        "waiting_on_deps",
        "blocked_precondition",
        "blocked_quality",
        "blocked_manual",
        "deferred",
        "historical",
        "superseded",
        "completed",
    ]
    lifecycle_state: str = "planned"
    dependency_ids: list[str] = Field(default_factory=list)
    missing_dependencies: list[str] = Field(default_factory=list)
    required_artifacts: list[str] = Field(default_factory=list)
    missing_outputs: list[str] = Field(default_factory=list)
    blocked_policy_ids: list[str] = Field(default_factory=list)
    source_window_notes: list[str] = Field(default_factory=list)
    score: float = 0.0
    context: dict[str, Any] = Field(default_factory=dict)


class OptimizationRecommendation(DeterministicModel):
    recommendation_id: str
    focus_iteration: str = ""
    focus_phase: str = ""
    recommended_task_ids: list[str] = Field(default_factory=list)
    recommended_phase_ids: list[str] = Field(default_factory=list)
    blocked_task_ids: list[str] = Field(default_factory=list)
    blocked_phase_ids: list[str] = Field(default_factory=list)
    policy_block_ids: list[str] = Field(default_factory=list)
    reorder_operations: list[dict[str, Any]] = Field(default_factory=list)
    source_window_notes: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)
    proposal_only: bool = True
    patch_file: str = ""


class RoadmapPatchProposal(DeterministicModel):
    proposal_id: str
    source_roadmap_sha256: str
    focus_iteration: str = ""
    focus_phase: str = ""
    operations: list[dict[str, Any]] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)


class OptimizationReport(DeterministicModel):
    report_id: str
    source_roadmap_sha256: str
    graph_file: str
    readiness_file: str
    recommendation_file: str
    recommendation_markdown: str
    patch_file: str = ""
    task_states: list[TaskStateSnapshot] = Field(default_factory=list)
    recommendation: OptimizationRecommendation


class ReviewFinding(DeterministicModel):
    scope: Literal["iteration", "phase"]
    finding_id: str
    category: Literal[
        "planning_error",
        "dependency_order",
        "gate_weakness",
        "gate_overconstraint",
        "tooling_env",
        "runtime_contract",
        "manual_workflow",
        "policy_gap",
        "artifact_schema",
        "data_quality",
    ]
    severity: Literal["low", "medium", "high"] = "medium"
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_action: str


class ReviewChangeProposal(DeterministicModel):
    change_id: str
    source: Literal["optimizer_patch", "review_inference", "manual_carryover"]
    operation: dict[str, Any] = Field(default_factory=dict)
    target: str
    rationale: str
    status: Literal["proposed", "accepted", "deferred"] = "proposed"


class StarterPromptArtifact(DeterministicModel):
    iteration_id: str
    generated_at: str
    recommended_new_chat: bool = True
    prompt_markdown_path: str
    stable_checkpoint_commits: list[str] = Field(default_factory=list)
    key_artifacts: list[str] = Field(default_factory=list)
    next_phase: str = ""
    constraints: list[str] = Field(default_factory=list)


class IterationReview(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    review_id: str
    review_type: Literal["iteration"] = "iteration"
    iteration_id: str
    generated_at: str
    git: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    phase_summary: dict[str, Any] = Field(default_factory=dict)
    blocker_summary: dict[str, Any] = Field(default_factory=dict)
    timing_summary: dict[str, Any] = Field(default_factory=dict)
    manual_summary: dict[str, Any] = Field(default_factory=dict)
    quality_summary: dict[str, Any] = Field(default_factory=dict)
    findings: list[ReviewFinding] = Field(default_factory=list)
    roadmap_changes: list[ReviewChangeProposal] = Field(default_factory=list)
    carryover_blockers: list[dict[str, Any]] = Field(default_factory=list)
    branch_closeout: dict[str, Any] = Field(default_factory=dict)
    next_iteration: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    status: Literal["draft", "approved", "deferred"] = "draft"


class PhaseReview(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    review_id: str
    review_type: Literal["phase"] = "phase"
    iteration_id: str
    phase_id: str
    generated_at: str
    git: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    phase_summary: dict[str, Any] = Field(default_factory=dict)
    blocker_summary: dict[str, Any] = Field(default_factory=dict)
    timing_summary: dict[str, Any] = Field(default_factory=dict)
    manual_summary: dict[str, Any] = Field(default_factory=dict)
    quality_summary: dict[str, Any] = Field(default_factory=dict)
    findings: list[ReviewFinding] = Field(default_factory=list)
    roadmap_changes: list[ReviewChangeProposal] = Field(default_factory=list)
    carryover_blockers: list[dict[str, Any]] = Field(default_factory=list)
    branch_closeout: dict[str, Any] = Field(default_factory=dict)
    next_iteration: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    status: Literal["draft", "approved", "deferred"] = "draft"


class ReviewApproval(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    approval_id: str
    review_id: str
    iteration_id: str
    decision: Literal["approved", "deferred"]
    accepted_change_ids: list[str] = Field(default_factory=list)
    deferred_change_ids: list[str] = Field(default_factory=list)
    branch_closeout_approved: bool = False
    next_iteration_authorized: bool = False
    created_at: str
    notes: str = ""


class KickoffReport(DeterministicModel):
    schema_version: str = Field(default=ROADMAP_SCHEMA_VERSION)
    kickoff_id: str
    iteration_id: str
    generated_at: str
    git: dict[str, Any] = Field(default_factory=dict)
    expected_branch: str
    base_branch: str
    review_approval_file: str = ""
    checks: list[dict[str, Any]] = Field(default_factory=list)
    status: Literal["ready", "blocked"] = "blocked"
    starter_prompt_path: str = ""
    branch_plan_path: str = ""
    rationale: list[str] = Field(default_factory=list)


class ProjectIntent(DeterministicModel):
    project_name: str
    objective: str
    scope_in: list[str] = Field(default_factory=list)
    scope_out: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    audience: str = "engineering"


class RoadmapItem(DeterministicModel):
    item_id: str
    title: str
    description: str
    iteration_id: Optional[str] = None
    phase_name: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class PhaseGate(DeterministicModel):
    gate_id: str
    name: str
    description: str
    pass_condition: str
    on_fail: Literal["block", "warn"] = "block"
    check_command: Optional[str] = None
    required_outputs: list[str] = Field(default_factory=list)


class RiskRegisterEntry(DeterministicModel):
    code: str
    title: str
    signal: str
    mitigation: str
    backout: str
    severity: int = Field(default=3, ge=1, le=5)
    phase_scope: list[str] = Field(default_factory=list)


class ExecutionStep(DeterministicModel):
    step_id: str
    title: str
    description: str
    command: Optional[str] = None
    cwd: str = "."
    timeout_seconds: int = Field(default=1800, ge=1)
    retry_limit: int = Field(default=0, ge=0)
    required_outputs: list[str] = Field(default_factory=list)
    conditions: list[ConditionSpec] = Field(default_factory=list)
    gate_ids: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    manual_handoff: bool = False
    task_id: Optional[str] = None
    status: Literal[
        "pending",
        "running",
        "passed",
        "failed",
        "blocked",
        "skipped",
        "waiting_manual",
    ] = "pending"


class Runbook(DeterministicModel):
    runbook_id: str
    title: str
    summary: str
    iteration_id: str
    phase_name: str
    autonomy_mode: Literal["autonomous", "advisory"] = "autonomous"
    dependencies: list[str] = Field(default_factory=list)
    gates: list[PhaseGate] = Field(default_factory=list)
    risks: list[RiskRegisterEntry] = Field(default_factory=list)
    steps: list[ExecutionStep] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    llm_refined: bool = False


class BlockerEvent(DeterministicModel):
    blocker_id: str
    blocker_type: Literal[
        "env",
        "data",
        "gate",
        "dependency",
        "policy",
        "runtime",
        "security",
        "cost",
        "manual",
    ]
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    message: str
    step_id: Optional[str] = None
    gate_id: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)


class RecoveryOption(DeterministicModel):
    option_id: str
    title: str
    description: str
    commands: list[str] = Field(default_factory=list)
    estimated_effort: int = Field(default=3, ge=1, le=10)
    risk_reduction: int = Field(default=5, ge=1, le=10)
    success_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    side_effects: list[str] = Field(default_factory=list)
    score: float = 0.0


class DecisionRecord(DeterministicModel):
    decision_id: str
    blocker_event_id: str
    status: Literal["needs_selection", "selected", "auto_selected", "resolved"]
    recommended_option_id: Optional[str] = None
    selected_option_id: Optional[str] = None
    rationale: str
    options: list[RecoveryOption] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class DeferredBlockerRecord(DeterministicModel):
    deferred_id: str
    decision_id: str
    blocker_id: str
    until_iteration: str
    until_phase: str
    criteria: str
    created_at: str
    status: Literal["active", "expired", "cleared"] = "active"
    context: dict[str, Any] = Field(default_factory=dict)


class CostUsageRecord(DeterministicModel):
    usage_id: str
    component: str
    model_name: str = ""
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    cache_hit: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("total_tokens", mode="before")
    @classmethod
    def _derive_total_tokens(cls, value: Any, info):
        if value not in (None, "", 0):
            return int(value)
        data = info.data
        prompt = int(data.get("prompt_tokens", 0) or 0)
        completion = int(data.get("completion_tokens", 0) or 0)
        return prompt + completion
