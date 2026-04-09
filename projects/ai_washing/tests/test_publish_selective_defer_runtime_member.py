from __future__ import annotations

import argparse
import json

from ai_washing_member.classification.publish_selective_defer_runtime import run_publish


def test_member_publish_selective_defer_runtime_smoke(tmp_path):
    binary_meta = tmp_path / "binary.json"
    logreg_meta = tmp_path / "logreg.json"
    policy = tmp_path / "policy.yaml"
    binary_meta.write_text(
        json.dumps(
            {
                "source_window_id": "active_2021_2024",
                "runtime": {
                    "relevance_model_pickle": "rel.pkl",
                    "relevance_model_pickle_sha256": "abc",
                    "embedding_backend": "hash",
                    "model_name": "hash://bow",
                    "hash_dim": 32,
                    "batch_size": 8,
                },
            }
        ),
        encoding="utf-8",
    )
    logreg_meta.write_text(
        json.dumps(
            {
                "runtime": {
                    "model_pickle": "log.pkl",
                    "model_pickle_sha256": "def",
                    "embedding_backend": "hash",
                    "model_name": "hash://bow",
                    "hash_dim": 32,
                    "batch_size": 8,
                }
            }
        ),
        encoding="utf-8",
    )
    policy.write_text("model: gpt-5-mini\n", encoding="utf-8")
    output_manifest = tmp_path / "selected.json"

    report = run_publish(
        argparse.Namespace(
            binary_metadata=str(binary_meta),
            logreg_metadata=str(logreg_meta),
            api_policy=str(policy),
            low_confidence_threshold=0.49,
            model_id="",
            selection_reason="test",
            output_manifest=str(output_manifest),
            heldout_report="heldout.json",
            heldout_confidence_sweep="heldout.csv",
            irr_boundary_report="irr.json",
            irr_boundary_confidence_sweep="irr.csv",
            decision_note="note.md",
        )
    )

    assert report["status"] == "selected"
    assert report["winner"]["model_type"] == "selective_defer_layered_api_a"
    assert report["operating_point"]["low_confidence_threshold"] == 0.49
    payload = json.loads(output_manifest.read_text(encoding="utf-8"))
    assert payload["winner"]["model_id"] == "selective_defer_layered_api_a_conf49_v1"
