"""Blocker taxonomy and ranked recovery decision engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import dump_json, now_utc_iso, sha256_text
from semantic_ai_washing.director.schemas import (
    BlockerEvent,
    DecisionRecord,
    DeferredBlockerRecord,
    RecoveryOption,
)

_DEFAULT_OPTIONS = {
    "env": [
        {
            "title": "Repair local environment and rerun",
            "description": "Recreate venv/bootstrap and rerun failed step.",
            "commands": ["make bootstrap", "make doctor"],
            "estimated_effort": 3,
            "risk_reduction": 8,
            "success_probability": 0.8,
            "side_effects": ["may change dependency lock state"],
        },
        {
            "title": "Use fallback interpreter path",
            "description": "Use explicit interpreter fallback for validation commands.",
            "commands": ["PYTHONPATH=src python3.9 -m pytest -q"],
            "estimated_effort": 2,
            "risk_reduction": 5,
            "success_probability": 0.5,
            "side_effects": ["deviates from canonical .venv policy"],
        },
    ],
    "data": [
        {
            "title": "Regenerate missing data artifact",
            "description": "Rerun upstream extraction/build steps for missing artifacts.",
            "commands": [],
            "estimated_effort": 4,
            "risk_reduction": 7,
            "success_probability": 0.75,
            "side_effects": ["runtime increase"],
        },
        {
            "title": "Downscope target and document limitation",
            "description": "Adjust phase targets based on current data availability with evidence.",
            "commands": [],
            "estimated_effort": 3,
            "risk_reduction": 4,
            "success_probability": 0.6,
            "side_effects": ["lower phase completeness"],
        },
    ],
    "gate": [
        {
            "title": "Open corrective branch and fix failing gate",
            "description": "Address failing tests/metrics before merge continues.",
            "commands": [],
            "estimated_effort": 5,
            "risk_reduction": 9,
            "success_probability": 0.7,
            "side_effects": ["timeline extension"],
        }
    ],
    "dependency": [
        {
            "title": "Pin and reinstall dependencies",
            "description": "Stabilize dependency versions and rerun validation.",
            "commands": ["make bootstrap"],
            "estimated_effort": 4,
            "risk_reduction": 7,
            "success_probability": 0.7,
            "side_effects": ["possible version drift"],
        }
    ],
    "policy": [
        {
            "title": "Escalate for manual decision",
            "description": "Pause automation and request explicit policy decision.",
            "commands": [],
            "estimated_effort": 1,
            "risk_reduction": 8,
            "success_probability": 0.95,
            "side_effects": ["manual intervention required"],
        }
    ],
    "runtime": [
        {
            "title": "Retry step with bounded timeout",
            "description": "Rerun the failed runtime step once with stricter timeout.",
            "commands": [],
            "estimated_effort": 2,
            "risk_reduction": 4,
            "success_probability": 0.5,
            "side_effects": ["may fail again"],
        },
        {
            "title": "Isolate failing command and continue in debug mode",
            "description": "Pause autonomous flow and run command manually with diagnostics.",
            "commands": [],
            "estimated_effort": 3,
            "risk_reduction": 6,
            "success_probability": 0.7,
            "side_effects": ["slower throughput"],
        },
    ],
    "security": [
        {
            "title": "Rotate secrets and purge exposures",
            "description": "Rotate exposed key material and rerun security scan.",
            "commands": [],
            "estimated_effort": 4,
            "risk_reduction": 10,
            "success_probability": 0.95,
            "side_effects": ["temporary API disruption"],
        }
    ],
    "cost": [
        {
            "title": "Lower model budget and retry deterministically",
            "description": "Disable LLM refinement for this run and continue deterministically.",
            "commands": [],
            "estimated_effort": 1,
            "risk_reduction": 7,
            "success_probability": 0.9,
            "side_effects": ["less nuanced synthesis"],
        }
    ],
}


class DecisionEngine:
    def __init__(self, decisions_dir: str | Path):
        self.decisions_dir = Path(decisions_dir)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _score(option: RecoveryOption) -> float:
        """Higher score means better option."""
        penalty = len(option.side_effects) * 2
        return round(
            (option.risk_reduction * 2.5)
            + (option.success_probability * 30.0)
            - (option.estimated_effort * 3.0)
            - penalty,
            3,
        )

    def options_for(self, blocker: BlockerEvent) -> list[RecoveryOption]:
        templates = _DEFAULT_OPTIONS.get(blocker.blocker_type, _DEFAULT_OPTIONS["runtime"])
        options: list[RecoveryOption] = []
        for idx, tpl in enumerate(templates, start=1):
            option = RecoveryOption(
                option_id=f"{blocker.blocker_id}-opt{idx}",
                title=tpl["title"],
                description=tpl["description"],
                commands=tpl.get("commands", []),
                estimated_effort=tpl.get("estimated_effort", 3),
                risk_reduction=tpl.get("risk_reduction", 5),
                success_probability=tpl.get("success_probability", 0.5),
                side_effects=tpl.get("side_effects", []),
            )
            option.score = self._score(option)
            options.append(option)
        options.sort(key=lambda item: item.score, reverse=True)
        return options

    def decide(
        self,
        blocker: BlockerEvent,
        selected_option_id: str | None = None,
        require_manual_selection: bool = True,
    ) -> DecisionRecord:
        options = self.options_for(blocker)
        recommended = options[0] if options else None

        status = "needs_selection"
        selected = None
        rationale = "Escalation required with ranked recovery options."

        if selected_option_id:
            selected = selected_option_id
            status = "selected"
            rationale = "User/runner selected explicit recovery option."
        elif not require_manual_selection and recommended is not None:
            selected = recommended.option_id
            status = "auto_selected"
            rationale = "Auto-selection enabled by policy."

        decision = DecisionRecord(
            decision_id=sha256_text(f"{blocker.blocker_id}:{now_utc_iso()}")[:16],
            blocker_event_id=blocker.blocker_id,
            status=status,
            recommended_option_id=(recommended.option_id if recommended else None),
            selected_option_id=selected,
            rationale=rationale,
            options=options,
            context={"blocker_type": blocker.blocker_type, "severity": blocker.severity},
        )
        return decision

    def write_decision(self, decision: DecisionRecord) -> Path:
        out = self.decisions_dir / f"decision_{decision.decision_id}.json"
        dump_json(out, decision.as_deterministic_dict())
        return out

    def from_blocker_file(
        self,
        blocker_file: str,
        selected_option_id: str | None = None,
        require_manual_selection: bool = True,
    ) -> tuple[DecisionRecord, Path]:
        blocker = self.blocker_from_payload_file(blocker_file)
        decision = self.decide(
            blocker=blocker,
            selected_option_id=selected_option_id,
            require_manual_selection=require_manual_selection,
        )
        out = self.write_decision(decision)
        return decision, out

    def blocker_from_payload_file(self, payload_file: str) -> BlockerEvent:
        payload = json.loads(Path(payload_file).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Expected JSON object payload for blocker parsing.")
        return self.blocker_from_payload_dict(payload)

    @staticmethod
    def blocker_from_payload_dict(payload: dict[str, Any]) -> BlockerEvent:
        if {"blocker_id", "blocker_type", "message"}.issubset(payload.keys()):
            return BlockerEvent.model_validate(payload)

        if "blocker" in payload and isinstance(payload["blocker"], dict):
            return BlockerEvent.model_validate(payload["blocker"])

        if {"decision_id", "blocker_event_id", "options"}.issubset(payload.keys()):
            raise ValueError(
                "Expected blocker event JSON or execution_state JSON containing `blocker`; "
                "received decision record JSON."
            )

        raise ValueError(
            "Expected blocker event JSON (`blocker_id`, `blocker_type`, `message`) "
            "or execution_state JSON containing `blocker`."
        )

    def defer(
        self,
        decision_file: str,
        until_iteration: str,
        until_phase: str,
        criteria: str,
        runs_dir: str | Path | None = None,
    ) -> tuple[DeferredBlockerRecord, Path]:
        payload = json.loads(Path(decision_file).read_text(encoding="utf-8"))
        decision = DecisionRecord.model_validate(payload)
        if not decision.blocker_event_id:
            raise ValueError("Decision file does not reference a blocker_event_id.")

        deferred = DeferredBlockerRecord(
            deferred_id=sha256_text(
                f"{decision.decision_id}:{decision.blocker_event_id}:{now_utc_iso()}"
            )[:16],
            decision_id=decision.decision_id,
            blocker_id=decision.blocker_event_id,
            until_iteration=str(until_iteration),
            until_phase=str(until_phase),
            criteria=criteria,
            created_at=now_utc_iso(),
            status="active",
            context={"decision_file": str(Path(decision_file).resolve())},
        )
        out = self.decisions_dir / f"deferred_{deferred.deferred_id}.json"
        dump_json(out, deferred.as_deterministic_dict())

        updated = decision.model_copy(
            update={
                "status": "resolved",
                "rationale": (
                    f"{decision.rationale} Deferred to iteration {until_iteration} / "
                    f"{until_phase} with criteria: {criteria}"
                ),
                "context": {
                    **decision.context,
                    "deferred_record": str(out),
                    "deferred_until_iteration": str(until_iteration),
                    "deferred_until_phase": str(until_phase),
                },
            }
        )
        dump_json(decision_file, updated.as_deterministic_dict())

        if runs_dir is not None:
            runs_path = Path(runs_dir)
            for state_file in runs_path.glob("execution_state_*.json"):
                state_payload = json.loads(state_file.read_text(encoding="utf-8"))
                if state_payload.get("decision_file") != str(Path(decision_file).resolve()):
                    continue
                state_payload["status"] = "deferred_blocked"
                state_payload["deferred"] = deferred.as_deterministic_dict()
                dump_json(state_file, state_payload)
                break

        return deferred, out
