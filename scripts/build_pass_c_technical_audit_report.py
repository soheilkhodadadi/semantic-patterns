"""Build a technical audit report for the current Pass C paper draft."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
DEFAULT_MONTH = "2026-03"
DEFAULT_STEM = "pass_c_technical_audit_2026-03-25_v1"
OUTPUT_MARKDOWN = REPO_ROOT / "output" / "paper" / "reports" / DEFAULT_MONTH / f"{DEFAULT_STEM}.md"
OUTPUT_DOCX = REPO_ROOT / "output" / "doc" / "reports" / DEFAULT_MONTH / f"{DEFAULT_STEM}.docx"
TRACKED_MARKDOWN = REPO_ROOT / "reports" / "analysis" / f"{DEFAULT_STEM}.md"

LABELS_MASTER = REPO_ROOT / "data" / "labels" / "v1" / "labels_master.parquet"
IRR_MASTER = REPO_ROOT / "data" / "labels" / "v1" / "irr_subset_master.csv"
IRR_REPORT = REPO_ROOT / "reports" / "labels" / "irr_report.json"
IRR_DIAGNOSTIC = REPO_ROOT / "reports" / "labels" / "irr_disagreement_diagnostic_v1.json"
READINESS_REPORT = REPO_ROOT / "reports" / "models" / "preliminary_results_readiness_v1.json"
HELDOUT_SUMMARY = REPO_ROOT / "reports" / "evaluation" / "heldout_eval_prelim_v2.json"
BENCHMARK_MATRIX = REPO_ROOT / "reports" / "evaluation" / "model_benchmark_matrix_prelim_v1.json"
PANEL = (
    REPO_ROOT / "data" / "processed" / "panel" / "panel_reg_ready_ever_speaker_2016_2024_v1.csv"
)

TABLE_PATHS = {
    "Table 2": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_2_ai_focus_timing_prelim_v1.md",
    "Table 3": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_3_disclosure_composition_timing_prelim_v1.md",
    "Table 4": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_4_actionable_patent_timing_prelim_v1.md",
    "Table 4B": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_4b_speculative_patent_timing_prelim_v1.md",
    "Table 6": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_6_as_patent_mismatch_tplus1_prelim_v1.md",
    "Table 6B": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_6b_as_patent_mismatch_tplus2_prelim_v1.md",
    "Table 7": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_7_mismatch_determinants_prelim_v1.md",
    "Table 7C": REPO_ROOT
    / "paper"
    / "generated"
    / "tables"
    / "table_7c_mismatch_determinants_reduced_prelim_v1.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-markdown", type=Path, default=OUTPUT_MARKDOWN)
    parser.add_argument("--output-docx", type=Path, default=OUTPUT_DOCX)
    parser.add_argument("--tracked-markdown", type=Path, default=TRACKED_MARKDOWN)
    parser.add_argument("--skip-docx", action="store_true")
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_float(value: float, places: int = 4) -> str:
    return f"{float(value):.{places}f}"


def _extract_observations_row(path: Path) -> list[str]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Observations |"):
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            return parts[1:]
    return []


def _build_measurement_tables() -> tuple[str, dict[str, object]]:
    labels = pd.read_parquet(LABELS_MASTER)
    labels = labels[labels["label"].notna()].copy()
    label_counts = labels["label"].value_counts().sort_index()

    irr_master = pd.read_csv(IRR_MASTER)
    irr_counts = irr_master["label"].value_counts().sort_index()

    irr_report = _load_json(IRR_REPORT)
    irr_diag = _load_json(IRR_DIAGNOSTIC)
    heldout = _load_json(HELDOUT_SUMMARY)
    matrix = _load_json(BENCHMARK_MATRIX)

    selected_model = heldout["model_id"]
    model_row = next(row for row in matrix["models"] if row["model_id"] == selected_model)
    primary = model_row["benchmarks"]["held_out_v2"]
    per_class = primary["per_class"]

    macro_precision = sum(stats["precision"] for stats in per_class.values()) / len(per_class)
    macro_recall = sum(stats["recall"] for stats in per_class.values()) / len(per_class)
    weighted_precision = sum(
        stats["precision"] * stats["support"] for stats in per_class.values()
    ) / sum(stats["support"] for stats in per_class.values())
    weighted_recall = sum(
        stats["recall"] * stats["support"] for stats in per_class.values()
    ) / sum(stats["support"] for stats in per_class.values())
    weighted_f1 = sum(stats["f1"] * stats["support"] for stats in per_class.values()) / sum(
        stats["support"] for stats in per_class.values()
    )
    agreement_rate = (
        irr_report["summary"]["reviewed_items"] - irr_report["summary"]["rows_disagreement"]
    ) / irr_report["summary"]["reviewed_items"]

    summary_table = "\n".join(
        [
            "| Audit component | Current source of truth | N | Key current numbers |",
            "| --- | --- | ---: | --- |",
            (
                f"| Adjudicated labeled sentence set | `data/labels/v1/labels_master.parquet` "
                f"| {len(labels):,} | Actionable {label_counts.get('Actionable', 0):,}; "
                f"Speculative {label_counts.get('Speculative', 0):,}; "
                f"Irrelevant {label_counts.get('Irrelevant', 0):,} |"
            ),
            (
                f"| Human-human IRR subset | `reports/labels/irr_report.json` and "
                f"`data/labels/v1/irr_subset_master.csv` | {len(irr_master):,} | "
                f"Balanced subset: Actionable {irr_counts.get('Actionable', 0):,}; "
                f"Speculative {irr_counts.get('Speculative', 0):,}; "
                f"Irrelevant {irr_counts.get('Irrelevant', 0):,}; "
                f"Cohen's kappa = {_fmt_float(irr_report['summary']['kappa'])}; "
                f"agreement = {_fmt_float(agreement_rate)} |"
            ),
            (
                f"| Selected classifier held-out benchmark | `reports/evaluation/heldout_eval_prelim_v2.json` "
                f"and `reports/evaluation/model_benchmark_matrix_prelim_v1.json` | "
                f"{heldout['summary']['reviewed_items']:,} | Accuracy = {_fmt_float(heldout['summary']['accuracy'])}; "
                f"macro-F1 = {_fmt_float(heldout['summary']['macro_f1'])}; "
                f"weighted-F1 = {_fmt_float(weighted_f1)} |"
            ),
        ]
    )

    class_table_lines = [
        "| Class | Support | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label in ["Actionable", "Speculative", "Irrelevant"]:
        stats = per_class[label]
        class_table_lines.append(
            f"| {label} | {stats['support']} | {_fmt_float(stats['precision'])} | "
            f"{_fmt_float(stats['recall'])} | {_fmt_float(stats['f1'])} |"
        )
    class_table_lines.extend(
        [
            f"| Macro average | {heldout['summary']['reviewed_items']} | {_fmt_float(macro_precision)} | {_fmt_float(macro_recall)} | {_fmt_float(heldout['summary']['macro_f1'])} |",
            f"| Weighted average | {heldout['summary']['reviewed_items']} | {_fmt_float(weighted_precision)} | {_fmt_float(weighted_recall)} | {_fmt_float(weighted_f1)} |",
        ]
    )

    tables = "\n".join([summary_table, "", "\n".join(class_table_lines)])
    payload = {
        "labels_count": len(labels),
        "label_counts": {k: int(v) for k, v in label_counts.items()},
        "irr_count": len(irr_master),
        "irr_counts": {k: int(v) for k, v in irr_counts.items()},
        "irr_kappa": irr_report["summary"]["kappa"],
        "agreement_rate": agreement_rate,
        "binary_relevance_kappa": irr_diag["summary"]["binary_relevance_kappa"],
        "as_conditional_kappa": irr_diag["summary"]["actionable_speculative_conditional_kappa"],
        "heldout_count": heldout["summary"]["reviewed_items"],
        "accuracy": heldout["summary"]["accuracy"],
        "macro_f1": heldout["summary"]["macro_f1"],
        "weighted_f1": weighted_f1,
        "binary_relevance_accuracy": heldout["summary"]["binary_relevance_accuracy"],
        "as_conditional_accuracy": heldout["summary"][
            "actionable_speculative_conditional_accuracy"
        ],
    }
    return tables, payload


def _build_attrition_table() -> tuple[str, dict[str, object]]:
    df = pd.read_csv(PANEL, low_memory=False)
    base_2016 = df[df["year"] == 2016].sort_values("cik").drop_duplicates("cik")
    table2_obs = _extract_observations_row(TABLE_PATHS["Table 2"])
    table4_obs = _extract_observations_row(TABLE_PATHS["Table 4"])
    table6_obs = _extract_observations_row(TABLE_PATHS["Table 6"])
    table6b_obs = _extract_observations_row(TABLE_PATHS["Table 6B"])
    table7_obs = _extract_observations_row(TABLE_PATHS["Table 7"])
    table7c_obs = _extract_observations_row(TABLE_PATHS["Table 7C"])

    horizon_counts = {
        "t-2": int(df["log_patents_ai_lag2"].notna().sum()),
        "t-1": int(df["log_patents_ai_lag1"].notna().sum()),
        "t": int(df["log_patents_ai_lead0"].notna().sum()),
        "t+1": int(df["log_patents_ai_lead1"].notna().sum()),
        "t+2": int(df["log_patents_ai_lead2"].notna().sum()),
    }
    control_counts = {
        c: int(df[c].notna().sum())
        for c in [
            "ln_assets",
            "leverage",
            "cash",
            "rd_intensity",
            "capx_at",
            "roa",
            "sales_growth",
            "emp",
        ]
    }
    baseline_counts = {
        c: int(base_2016[c].notna().sum())
        for c in ["ln_assets", "cash", "leverage", "capx_at", "roa", "rd_intensity", "emp"]
    }

    rows = [
        (
            "Regression-ready ever-speaker panel",
            f"{len(df):,}",
            "All ever-speaker firm-years, 2016-2024, with baseline control backbone.",
        ),
        (
            "AI-talking firm-years inside ever-speaker panel",
            f"{int(df['any_ai_talk'].fillna(0).sum()):,}",
            "Composition and mismatch constructs are only economically meaningful when AI disclosure is observed.",
        ),
        (
            "Table 2 / 3, t-2 horizon",
            table2_obs[0],
            "Outcome requires lag-2 patent availability plus complete controls.",
        ),
        (
            "Table 2 / 3, t+1 horizon",
            table2_obs[3],
            "Outcome requires lead-1 patent availability plus complete controls.",
        ),
        (
            "Table 2 / 3, t+2 horizon",
            table2_obs[4],
            "Outcome requires lead-2 patent availability plus complete controls.",
        ),
        (
            "Table 4 / 4B timing matrices",
            table4_obs[0],
            "Strongest drop because each regression includes patent timing terms from t-2 through t+2 simultaneously.",
        ),
        (
            "Table 6, mismatch at t+1",
            table6_obs[0],
            "One-horizon ever-speaker regression; PatentMismatch is coded as zero outside AI-talking years rather than inducing a talk-only sample.",
        ),
        (
            "Table 6B, mismatch at t+2",
            table6b_obs[0],
            "Longer-horizon counterpart; later years drop out mechanically.",
        ),
        (
            "Table 7 full multivariate",
            table7_obs[-1],
            "2016 baseline firm cross-section plus missingness in R&D/assets and employees.",
        ),
        (
            "Table 7C reduced multivariate",
            table7c_obs[-1],
            "Reduced baseline set recovers most of the firm sample by omitting sparse R&D/assets and employees.",
        ),
    ]

    md_lines = [
        "| Empirical block | Observations | Main reason for shrinkage |",
        "| --- | ---: | --- |",
    ]
    for label, n, reason in rows:
        md_lines.append(f"| {label} | {n} | {reason} |")

    payload = {
        "panel_rows": len(df),
        "unique_firms": int(df["cik"].nunique()),
        "talk_rows": int(df["any_ai_talk"].fillna(0).sum()),
        "horizon_counts": horizon_counts,
        "control_counts": control_counts,
        "baseline_firms": len(base_2016),
        "baseline_counts": baseline_counts,
    }
    return "\n".join(md_lines), payload


def _build_markdown() -> str:
    measurement_tables, measurement = _build_measurement_tables()
    attrition_table, attrition = _build_attrition_table()

    exact_rule = (
        "`PatentMismatch_{i,t} = 1` if firm-year `i,t` is an AI-talking year, "
        "`A_S_{i,t}` lies in the bottom quartile of the year-`t` AI-talking distribution "
        "or `SpecShare_{i,t}` lies in the top quartile of that same distribution, and "
        "contemporaneous `log(1 + AI patents_{i,t})` is below the year-`t` industry-year mean "
        "of `log(1 + AI patents)`; otherwise `PatentMismatch_{i,t} = 0`."
    )

    return f"""# Pass C Technical Audit Report V1

This report consolidates the current technical evidence behind the March 25 Pass C draft and responds directly to the three live review issues: measurement credibility, PatentMismatch reproducibility, and sample attrition. It is intended to be a paper-support artifact that can be shared with a supervisor, used to answer an external agent, or mined for direct manuscript revisions.

Reviewed draft:

- `paper/source/AI Washing - SK - 2026.03.25.3 - Pass C.docx`

Primary current source-of-truth artifacts:

- `reports/models/preliminary_results_readiness_v1.json`
- `reports/labels/irr_report.json`
- `reports/labels/irr_disagreement_diagnostic_v1.json`
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- `data/labels/v1/labels_master.parquet`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## 1. Executive Read

The manuscript now explains the measurement pipeline and the mismatch design much more clearly than earlier proposal versions. The remaining hard-gate problem is not conceptual confusion; it is missing audit evidence and missing reproducibility detail in the paper itself. The current repo already contains enough information to answer those issues, but the relevant numbers are spread across several artifacts and are not yet consolidated into a referee-facing object.

The measurement evidence is usable for a preliminary paper, but it is still preliminary rather than publication-grade. The adjudicated sentence set contains `{measurement["labels_count"]}` labels, the human-human IRR subset contains `{measurement["irr_count"]}` balanced items, and the current selected model reaches held-out accuracy `{_fmt_float(measurement["accuracy"])}` with macro-F1 `{_fmt_float(measurement["macro_f1"])}`. Those are enough to report transparently, but they do not justify stronger publication-grade validation claims.

## 2. Stop-the-Line Issue 1: Compact Measurement Audit Object

### 2.1 Recommended appendix object

The paper should add one compact appendix measurement-audit object and one short pointer sentence in the main text. The appendix object can combine the current adjudicated-label counts, the IRR audit, and the selected classifier's held-out performance in one place.

### 2.2 Current measurement audit summary

{measurement_tables}

### 2.3 Main-text pointer sentence

Suggested sentence for Section 3.2:

> Appendix Table A1 reports the measurement audit underlying the disclosure-classification layer: the adjudicated sentence set contains 551 labeled observations, the human-human IRR subset contains 120 balanced items with Cohen's kappa of 0.675, and the selected preliminary classifier achieves held-out accuracy of 0.706 and macro-F1 of 0.673 on a 177-sentence benchmark.

### 2.4 Interpretation

Two points matter here. First, the current evidence is real and reportable: it shows an adjudicated label base, a true human-human IRR audit, and a held-out benchmark for the currently selected model. Second, the same evidence still supports only a preliminary measurement claim. The current held-out metrics remain below the repo's own publication-grade threshold, so the paper should avoid language that implies the sentence classifier is fully validated at publication standard.

## 3. Stop-the-Line Issue 2: Exact PatentMismatch Coding Rule

### 3.1 Current live coding rule

The current source of truth is the live construction in `src/semantic_ai_washing/analysis/delivery_table_payloads.py`.

Exact rule:

> {exact_rule}

This means:
- low `A_S` means bottom year-specific quartile among AI-talking firm-years
- high `SpecShare` means top year-specific quartile among AI-talking firm-years
- the low-credibility gate uses an OR rule
- the final `PatentMismatch` indicator requires all conditions simultaneously
- the patent weakness benchmark is the industry-year mean of contemporaneous `log(1 + AI patents)`, not a raw-count or median benchmark

### 3.2 Recommended manuscript sentence for Section 3.6

> We define `PatentMismatch_{{i,t}} = 1` when firm-year `i,t` is an AI-talking year, `A_S_{{i,t}}` falls in the bottom quartile of the year-`t` AI-talking distribution or `SpecShare_{{i,t}}` rises into the top quartile of that distribution, and contemporaneous `log(1 + AI patents_{{i,t}})` is below the year-`t` industry-year mean of `log(1 + AI patents)`; otherwise `PatentMismatch_{{i,t}} = 0`.

### 3.3 Naming recommendation

Use `A_S` in equations, tables, and code references. In prose, define it once as the actionable-to-speculative ratio. Avoid switching between `AS`, `A/S`, and verbal labels without a stable first definition. The cleanest policy is:
- equation/table symbol: `A_S`
- prose label: actionable-to-speculative ratio

## 4. Major Issue: Sample Attrition

### 4.1 What is happening

The current paper no longer has a mysterious hidden sample problem, but it does have several different sample logics that the reader should not be left to infer. The main ever-speaker panel contains `{attrition["panel_rows"]:,}` firm-year observations across `{attrition["unique_firms"]:,}` firms in the regression-ready file, and `{attrition["talk_rows"]:,}` of those observations are AI-talking firm-years. Sample sizes then change for three mechanical reasons:

1. horizon-specific timing outcomes are unavailable at the start or end of the annual panel
2. some controls, especially `R&D/assets`, are materially incomplete
3. the determinants tables collapse the panel to baseline 2016 firm characteristics rather than staying in firm-years

### 4.2 Attrition map by empirical block

{attrition_table}

### 4.3 Current nonmissing counts that drive the shrinkage

- Patent-timing availability:
  - `t-2`: `{attrition["horizon_counts"]["t-2"]:,}`
  - `t-1`: `{attrition["horizon_counts"]["t-1"]:,}`
  - `t`: `{attrition["horizon_counts"]["t"]:,}`
  - `t+1`: `{attrition["horizon_counts"]["t+1"]:,}`
  - `t+2`: `{attrition["horizon_counts"]["t+2"]:,}`
- Key control availability in the regression-ready ever-speaker panel:
  - `ln_assets`: `{attrition["control_counts"]["ln_assets"]:,}`
  - `leverage`: `{attrition["control_counts"]["leverage"]:,}`
  - `cash`: `{attrition["control_counts"]["cash"]:,}`
  - `rd_intensity`: `{attrition["control_counts"]["rd_intensity"]:,}`
  - `capx_at`: `{attrition["control_counts"]["capx_at"]:,}`
  - `roa`: `{attrition["control_counts"]["roa"]:,}`
  - `sales_growth`: `{attrition["control_counts"]["sales_growth"]:,}`
  - `emp`: `{attrition["control_counts"]["emp"]:,}`
- Baseline 2016 determinants sample:
  - baseline firms: `{attrition["baseline_firms"]:,}`
  - 2016 `rd_intensity` available for `{attrition["baseline_counts"]["rd_intensity"]:,}` firms
  - 2016 `emp` available for `{attrition["baseline_counts"]["emp"]:,}` firms

### 4.4 Suggested manuscript sentence

> Sample sizes vary across empirical blocks for mechanical reasons tied to the panel design and the required covariate set. The main ever-speaker panel contains 18,741 firm-year observations, but timing regressions lose observations at the beginning and end of the sample when lagged or lead AI patent outcomes are unavailable, and all regressions additionally use complete cases on the baseline controls. The distributed-lag timing matrices impose the strongest requirement because they include patent outcomes from `t-2` through `t+2` simultaneously, while the determinants tables use a different design that collapses the panel to 2016 baseline firm characteristics, making missing `R&D/assets` and employment the main source of cross-sectional attrition.

## 5. Additional Technical Notes Worth Flagging

1. The current measurement evidence is preliminary rather than publication-grade.
   - Current held-out accuracy is `{_fmt_float(measurement["accuracy"])}` and macro-F1 is `{_fmt_float(measurement["macro_f1"])}`.
   - Current overall IRR kappa is `{_fmt_float(measurement["irr_kappa"])}`.
   - Those are reportable, but the manuscript should not claim fully validated publication-grade measurement.
2. The draft should explicitly point to the measurement-audit appendix object.
   - Right now the methodology section explains the gates well but still makes the reader trust the audit more than inspect it.
3. The mismatch rule is ready to state exactly now.
   - This is a writing fix, not a modeling blocker.
4. The determinants tables should distinguish substantive variation from missing-data variation.
   - The fuller determinants variants remain useful because the negative `R&D/assets` slope is informative.
   - The reduced variants remain useful because they protect against over-interpreting a heavily reduced complete-case sample.

## 6. Recommended Next Manuscript Edits

1. Add a compact appendix measurement-audit table and point to it once in Section 3.2.
2. Replace the current verbal description in Section 3.6 with the exact `PatentMismatch` rule above.
3. Add one explicit sample-attrition paragraph in the data/results section.
4. Keep the fuller determinants appendix tables in the package because the `R&D/assets` result is substantively informative even if it is not the cleanest main-text multivariate object.

## 7. Current Best Supporting Files

- Main paper draft:
  - `paper/source/AI Washing - SK - 2026.03.25.3 - Pass C.docx`
- Current preliminary draft build:
  - `output/doc/ai_washing_preliminary_draft.docx`
- Measurement audit sources:
  - `reports/models/preliminary_results_readiness_v1.json`
  - `reports/labels/irr_report.json`
  - `reports/labels/irr_disagreement_diagnostic_v1.json`
  - `reports/evaluation/heldout_eval_prelim_v2.json`
  - `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- Mismatch construct note:
  - `reports/analysis/patent_mismatch_construct_v1.md`

This report is the current paper-support audit for the March 25 Pass C draft.
"""


def build_docx(markdown_path: Path, output_docx: Path) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("pandoc is not installed or not on PATH")
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = PAPER_DIR / "metadata.yaml"
    reference_doc = PAPER_DIR / "reference.docx"
    command = [
        pandoc,
        "--standalone",
        "--metadata-file",
        str(metadata_path),
        str(markdown_path),
        "-o",
        str(output_docx),
    ]
    if reference_doc.exists():
        command.extend(["--reference-doc", str(reference_doc)])
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown = _build_markdown()
    args.output_markdown.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    args.tracked_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.tracked_markdown.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    if args.skip_docx:
        print(f"[OK] assembled markdown technical audit: {args.output_markdown}")
        print(f"[OK] wrote tracked markdown technical audit: {args.tracked_markdown}")
        return 0
    build_docx(args.output_markdown, args.output_docx)
    print(f"[OK] assembled markdown technical audit: {args.output_markdown}")
    print(f"[OK] wrote tracked markdown technical audit: {args.tracked_markdown}")
    print(f"[OK] built technical audit docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
