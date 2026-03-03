"""Pydantic schemas for the autonomous project director."""

from __future__ import annotations

import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "1.0.0"


class DeterministicModel(BaseModel):
    """Base model with deterministic JSON serialization helpers."""

    schema_version: str = Field(default=SCHEMA_VERSION)

    def as_deterministic_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)

    def as_deterministic_json(self) -> str:
        return json.dumps(self.as_deterministic_dict(), sort_keys=True, separators=(",", ":"))


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
    gate_ids: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    status: Literal["pending", "running", "passed", "failed", "blocked", "skipped"] = "pending"


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
