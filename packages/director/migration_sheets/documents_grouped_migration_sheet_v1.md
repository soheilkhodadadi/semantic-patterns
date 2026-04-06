# Documents Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.documents`

Legacy compatibility shim:
- `semantic_ai_washing.director.adapters.documents`

## Group 1: Direct snapshot document-ingestion callers

Files:
- `packages/director/src/semantic_director/snapshot.py`

Gate:
- `packages/director/tests/test_documents.py`
- `packages/director/tests/test_snapshot.py`
- package build smoke

Status:
- complete
