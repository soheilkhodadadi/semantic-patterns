"""Shared lab core primitives with intentionally narrow scope."""

from semantic_ai_washing.labcore.registry import (
    PROJECT_SLUGS,
    ProjectAdapterContract,
    ProjectLanes,
    SharedLanes,
    all_project_adapter_contracts,
    project_lanes,
    project_adapter_contract,
    shared_lanes,
)
from semantic_ai_washing.labcore.audit import (
    append_jsonl,
    default_provenance,
    payload_hash,
    write_audit_record,
)
from semantic_ai_washing.labcore.security import (
    KEY_PATTERNS,
    ensure_api_key_if_enabled,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
    tracked_files,
)
from semantic_ai_washing.labcore.openai_responses import (
    OPENAI_RESPONSES_URL,
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
)
from semantic_ai_washing.labcore.runtime import (
    dump_json,
    ensure_dir,
    git_info,
    load_json,
    now_utc_iso,
    repository_root,
    run_command,
    sha256_file,
    sha256_text,
)

__all__ = [
    "PROJECT_SLUGS",
    "ProjectAdapterContract",
    "ProjectLanes",
    "SharedLanes",
    "KEY_PATTERNS",
    "OPENAI_RESPONSES_URL",
    "OpenAIResponsesError",
    "OpenAIResponsesHTTPError",
    "all_project_adapter_contracts",
    "append_jsonl",
    "call_responses_api",
    "default_provenance",
    "dump_json",
    "ensure_dir",
    "ensure_api_key_if_enabled",
    "git_info",
    "load_json",
    "now_utc_iso",
    "payload_hash",
    "project_lanes",
    "project_adapter_contract",
    "redact_secrets",
    "repository_root",
    "run_command",
    "extract_response_text",
    "scan_repo_for_secrets",
    "scan_text_for_secrets",
    "sha256_file",
    "sha256_text",
    "shared_lanes",
    "tracked_files",
    "write_audit_record",
]
