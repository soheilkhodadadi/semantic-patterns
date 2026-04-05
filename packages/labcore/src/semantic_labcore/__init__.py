"""Shared low-level infrastructure helpers for the semantic-patterns lab."""

from semantic_labcore.audit import (
    append_jsonl,
    default_provenance,
    payload_hash,
    write_audit_record,
)
from semantic_labcore.openai_responses import (
    OPENAI_RESPONSES_URL,
    OpenAIResponsesError,
    OpenAIResponsesHTTPError,
    call_responses_api,
    extract_response_text,
)
from semantic_labcore.registry import (
    PROJECT_SLUGS,
    ProjectAdapterContract,
    ProjectLanes,
    SharedLanes,
    all_project_adapter_contracts,
    project_adapter_contract,
    project_lanes,
    shared_lanes,
)
from semantic_labcore.runtime import (
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
from semantic_labcore.security import (
    KEY_PATTERNS,
    ensure_api_key_if_enabled,
    redact_secrets,
    scan_repo_for_secrets,
    scan_text_for_secrets,
    tracked_files,
)

__all__ = [
    "__version__",
    "KEY_PATTERNS",
    "OPENAI_RESPONSES_URL",
    "PROJECT_SLUGS",
    "OpenAIResponsesError",
    "OpenAIResponsesHTTPError",
    "ProjectAdapterContract",
    "ProjectLanes",
    "SharedLanes",
    "all_project_adapter_contracts",
    "append_jsonl",
    "call_responses_api",
    "default_provenance",
    "dump_json",
    "ensure_api_key_if_enabled",
    "ensure_dir",
    "extract_response_text",
    "git_info",
    "load_json",
    "now_utc_iso",
    "payload_hash",
    "project_adapter_contract",
    "project_lanes",
    "redact_secrets",
    "repository_root",
    "run_command",
    "scan_repo_for_secrets",
    "scan_text_for_secrets",
    "sha256_file",
    "sha256_text",
    "shared_lanes",
    "tracked_files",
    "write_audit_record",
]
__version__ = "0.1.0"
