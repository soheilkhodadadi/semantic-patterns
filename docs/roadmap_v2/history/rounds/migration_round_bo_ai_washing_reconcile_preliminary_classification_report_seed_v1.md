# Migration Round BO: AI-Washing Reconcile Preliminary Classification Report Seed V1

## Purpose

Seed the canonical member-owned preliminary classification reconciliation authority for Queue V16.

## What moved

Canonical member-owned authority:
- `projects/ai_washing/src/ai_washing_member/classification/reconcile_preliminary_classification_report.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/classification/reconcile_preliminary_classification_report.py`

New member-local test:
- `projects/ai_washing/tests/test_reconcile_preliminary_classification_report_member.py`

Grouped migration sheet:
- `projects/ai_washing/migration_sheets/reconcile_preliminary_classification_report_grouped_migration_sheet_v1.md`

## Validation

Passed:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_reconcile_preliminary_classification_report_member.py`

Result:
- `1 passed`
