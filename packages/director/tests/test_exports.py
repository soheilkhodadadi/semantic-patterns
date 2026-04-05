from semantic_director import (
    BlockerEvent,
    CostUsageRecord,
    DecisionRecord,
    ExecutionStep,
    PhaseGate,
    ProjectIntent,
    RecoveryOption,
    RiskRegisterEntry,
    RoadmapItem,
    Runbook,
)
from semantic_director.schemas import (
    BlockerEvent as SchemaBlockerEvent,
    CostUsageRecord as SchemaCostUsageRecord,
    DecisionRecord as SchemaDecisionRecord,
    ExecutionStep as SchemaExecutionStep,
    PhaseGate as SchemaPhaseGate,
    ProjectIntent as SchemaProjectIntent,
    RecoveryOption as SchemaRecoveryOption,
    RiskRegisterEntry as SchemaRiskRegisterEntry,
    RoadmapItem as SchemaRoadmapItem,
    Runbook as SchemaRunbook,
)


def test_package_exports_match_schema_surface() -> None:
    assert ProjectIntent is SchemaProjectIntent
    assert RoadmapItem is SchemaRoadmapItem
    assert PhaseGate is SchemaPhaseGate
    assert RiskRegisterEntry is SchemaRiskRegisterEntry
    assert ExecutionStep is SchemaExecutionStep
    assert Runbook is SchemaRunbook
    assert BlockerEvent is SchemaBlockerEvent
    assert RecoveryOption is SchemaRecoveryOption
    assert DecisionRecord is SchemaDecisionRecord
    assert CostUsageRecord is SchemaCostUsageRecord
