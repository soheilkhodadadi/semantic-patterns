"""Build a modular results-draft scaffold in Markdown and DOCX."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUTPUT_MARKDOWN = REPO_ROOT / "output" / "paper" / "results_draft_scaffold_v1.md"
OUTPUT_DOCX = REPO_ROOT / "output" / "doc" / "results_draft_scaffold_v1.docx"

SCAFFOLD_TEXT = """# Results Draft Scaffold V1

This document is a writing scaffold for the results section. It is not the manuscript itself. It is a guide for arranging the validated tables and figures into a clean empirical narrative, using literature-style insert markers rather than embedding the objects directly in the text.

## 4. Results

### 4.1 Sample, Coverage, and Descriptive Patterns

We begin by defining the estimation sample and the scale of the main variables. The main descriptive frame should stay anchored on the ever-speaker annual panel rather than the narrower speaking-only panel, because the ever-speaker design is the first panel that supports meaningful timing comparisons across prior, contemporaneous, and future innovation outcomes. The descriptive objects should show two facts clearly: AI-related disclosure grows sharply over the sample window, and AI patenting remains sparse even within the set of firms that discuss AI at least once.

[Insert Table 1 here]

Table 1 should establish the sample used in the main specifications, document the skewness of the disclosure measures, and make clear that medians and upper-tail percentiles are more informative than raw means for the patent outcomes. The surrounding text can briefly note that the restored zero-disclosure years are important for interpretation and that the resulting panel is broader than a disclosure-conditioned design.

[Insert Figure 1 here]

Figure 1 should visually motivate the growth of AI disclosure and its decomposition into actionable and speculative components. The text here should emphasize that the decomposition is economically meaningful rather than cosmetic.

[Insert Figure 2 here]

Figure 2 should then establish the validation target. The point is not simply that AI patenting exists, but that it is sparse, uneven, and therefore a demanding external benchmark for disclosure-based measures.

### 4.2 Timing Validation: Broad Intensity and Disclosure Composition

The next step is to validate the filing-based measures against AI patent timing outcomes. The broad AI-focus measure provides the first indication that AI disclosure is not merely noise: it is positively related to AI patent outcomes across multiple horizons in the ever-speaker panel. That broad result should be presented first because it establishes that the filing-based AI narrative layer contains economically relevant information before we ask whether composition sharpens the signal.

[Insert Table 2 here]

The text after Table 2 should emphasize that broad AI-related disclosure intensity is positively associated with AI patent outcomes at prior, contemporaneous, and future horizons. This motivates moving from disclosure intensity to disclosure composition.

[Insert Table 3 here]

Table 3 should then show that the composition of AI disclosure matters. The text can note that actionable and speculative-only disclosure follow different timing profiles, which is exactly why a decomposition-based design is useful.

[Insert Table 4 here]

[Insert Table 4B here]

Tables 4 and 4B should be discussed as the literature-style timing matrices. These are the tables that let the reader see whether the relevant relation is primarily backward-looking, contemporaneous, or forward-looking. The narrative here should avoid forcing a single stylized fact that the data do not support. Instead, it should stress that the timing patterns differ meaningfully across disclosure types and fixed-effect choices.

### 4.3 Methodology-Aligned AI-Washing Evidence

After the timing-validation layer, the results section can move to the paper's explicit AI-washing construct. This is where the narrative should become narrower and more disciplined. Rather than treating every credibility metric as equally central, the text should focus on the methodology-aligned specification built around the actionable-to-speculative ratio and the patent-mismatch interaction.

[Insert Table 6 here]

[Insert Table 6B here]

The discussion here should emphasize the main design logic: the slope on the `A/S` ratio is positive in non-mismatch years, while the interaction term is negative in mismatch years. The stronger and cleaner pattern at `t+1` should be treated as the main result, with the `t+2` version described as a nearby companion rather than an equally strong headline object.

[Insert Figure 3 here]

Figure 3 should be introduced as the visual companion to Table 6. It makes the interaction tangible by showing how the relation between disclosure credibility and future AI patenting differs between mismatch and non-mismatch firm-years.

[Insert Figure 4 here]

Figure 4 should then make the mismatch construct concrete at the sample level. The text around Figure 4 can transition from the regression evidence to descriptive heterogeneity: mismatch rises sharply late in the sample and is concentrated in a small set of broad sectors.

### 4.4 Who Exhibits PatentMismatch?

Once the paper has established what mismatch is and why it matters for the disclosure-innovation relation, the next natural question is which firms are more likely to exhibit it. This is where the determinants table belongs. The correct framing is descriptive cross-sectional evidence, not a mechanism claim.

[Insert Table 7C here]

The reduced-baseline determinants table is currently the cleanest candidate for the main narrative because it preserves most of the baseline-firm sample while still capturing the main financial-capacity margin. The text should note that larger firms and more profitable firms are more likely to be flagged in the simple and reduced multivariate cross-section in this design, which differs from the comparison paper and underscores that our paper is measuring a different form of mismatch.

Potential companion placement:
- If we want a second determinants object nearby, use `Table 7D` as the intensity variant.
- If we want to keep the main text tighter, retain `Table 7C` in the main narrative and move `Table 7`, `7B`, and `7D` to the appendix or supervisor-review set.

### 4.5 Appendix and Robustness Map

The appendix should defend the main-text story rather than compete with it.

Appendix candidates currently include:
- the narrower conditional validation table from the speaking-only panel
- the exploratory credibility-metric family (`Table 5 / 5B`)
- the full baseline determinants pair (`Table 7 / 7B`)
- the reduced intensity companion if not kept near the main text (`Table 7D`)
- any future count-outcome or alternative-functional-form variants we decide to keep

Suggested appendix insert markers:
- [Insert Appendix Table A1 here]
- [Insert Appendix Table A2 here]
- [Insert Appendix Table A3 here]
- [Insert Appendix Table A4 here]

### 4.6 Writing Notes

1. Keep the main text focused on the ever-speaker panel.
2. Use the timing tables to establish measurement credibility before introducing AI-washing language.
3. Let the mismatch table and its two figures carry the main AI-washing claim.
4. Treat determinants as a descriptive extension, not as proof of managerial mechanism.
5. Use appendix tables to answer foreseeable reviewer questions without overcrowding the main narrative.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-markdown", type=Path, default=OUTPUT_MARKDOWN)
    parser.add_argument("--output-docx", type=Path, default=OUTPUT_DOCX)
    parser.add_argument("--skip-docx", action="store_true")
    return parser.parse_args()


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
    args.output_markdown.write_text(SCAFFOLD_TEXT.rstrip() + "\n", encoding="utf-8")
    if args.skip_docx:
        print(f"[OK] assembled markdown results scaffold: {args.output_markdown}")
        return 0
    build_docx(args.output_markdown, args.output_docx)
    print(f"[OK] assembled markdown results scaffold: {args.output_markdown}")
    print(f"[OK] built results scaffold docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
