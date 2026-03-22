"""Build a modular results-transition notes guide in Markdown and DOCX."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"
OUTPUT_MARKDOWN = REPO_ROOT / "output" / "paper" / "results_transition_notes_v1.md"
OUTPUT_DOCX = REPO_ROOT / "output" / "doc" / "results_transition_notes_v1.docx"

TRANSITION_TEXT = """# Results Transition Notes V1

This document is a companion to the results scaffold. It is meant to make drafting easier by providing paragraph-level bridge text between the validated tables and figures. The language here is intentionally close to manuscript prose, but it should still be treated as adaptable working text rather than final copy.

## How To Use This File

Use each block as a starting paragraph or transition paragraph when moving from one empirical object to the next. The aim is to keep the results section focused, cumulative, and easy to follow without forcing every idea into the same paragraph.

## 1. Opening the Results Section

The results section begins by defining the sample and descriptive landscape rather than jumping immediately into hypothesis tests. This ordering matters because the ever-speaker annual panel is broader than the earlier disclosure-conditioned sample and is the first design in this project that supports meaningful comparisons across prior, contemporaneous, and future AI patent outcomes. The descriptive evidence therefore does more than summarize variables: it clarifies the sample logic that makes the later timing analysis interpretable.

[Insert Table 1 here]

## 2. Table 1 to Figure 1

Table 1 establishes the scale and skewness of the main measures, but the broader point is easier to see once the same information is viewed dynamically. In particular, the table shows that AI disclosure and AI patent outcomes are both highly uneven, with patenting especially sparse even in the ever-speaker universe. Figure 1 therefore shifts from static distributions to the time path of disclosure itself, allowing the reader to see whether the growth in AI-related language reflects a broad rise in narrative intensity and whether that increase is concentrated in specific components of the disclosure mix.

[Insert Figure 1 here]

## 3. Figure 1 to Figure 2

Figure 1 makes clear that AI-related disclosure expands sharply over the sample period, but disclosure alone is not the outcome of interest. The empirical question is whether the narrative layer aligns with observable innovation activity. Figure 2 therefore introduces AI patenting as the external benchmark used throughout the remainder of the paper. This figure is helpful because it shows that AI patenting is present and increasing, but still sparse and uneven enough to remain a demanding validation target for any disclosure-based measure.

[Insert Figure 2 here]

## 4. Figure 2 to Table 2

Once the reader has seen the descriptive evolution of disclosure and patenting, the next step is to ask whether broad AI disclosure intensity contains information about innovation timing. Table 2 provides that first validation test. The goal here is not yet to distinguish among types of AI-related language, but simply to establish that the filing-based AI narrative layer is not pure noise. If broad AI focus is positively associated with AI patent outcomes across multiple horizons, then it becomes worthwhile to ask whether decomposing that language into more credible and less credible components improves the signal.

[Insert Table 2 here]

## 5. Table 2 to Table 3

Table 2 shows that broad disclosure intensity is informative, but it leaves open whether all AI-related language carries the same meaning. That is the reason for moving immediately to Table 3. Instead of treating AI disclosure as a single undifferentiated construct, Table 3 asks whether actionable and speculative-only language follow different timing profiles with respect to AI patent outcomes. This is the central motivation for the decomposition-based design: if the coefficients differ materially across the two disclosure types, then the composition of AI-related language is empirically meaningful rather than merely descriptive.

[Insert Table 3 here]

## 6. Table 3 to Tables 4 and 4B

Table 3 introduces the composition result, but it does not yet show the full timing pattern in a literature-style way. Tables 4 and 4B provide that next layer by laying out the timing matrix directly. The point of these tables is not to force the data into a single stylized fact, but to let the reader see whether the relevant relations are primarily backward-looking, contemporaneous, or forward-looking, and whether those patterns remain stable once the specification changes. Read together, these timing matrices make the disclosure decomposition more concrete and show that actionable and speculative-only language do not map onto innovation timing in the same way.

[Insert Table 4 here]

[Insert Table 4B here]

## 7. Tables 4 and 4B to Table 6

The timing matrices establish that the disclosure composition contains information, but they still stop short of the paper's actual AI-washing construct. The next step is therefore to narrow the discussion and move from general timing validation to the methodology-aligned specification. Table 6 does that by centering the analysis on the actionable-to-speculative ratio and its interaction with PatentMismatch. This is the point in the results where the paper should shift from asking whether AI disclosure aligns with innovation outcomes at all to asking whether the quality of that disclosure matters differently when the underlying patent record is weak.

[Insert Table 6 here]

[Insert Table 6B here]

## 8. Table 6 to Figure 3

Table 6 provides the main interaction result, but interactions are often easier to understand once translated into a visual slope comparison. Figure 3 therefore serves as a direct companion rather than an independent piece of evidence. Its role is to make the regression logic intuitive: in non-mismatch firm-years, a higher actionable-to-speculative ratio is associated with stronger future AI patent outcomes, whereas in mismatch firm-years that relation is sharply attenuated or turns negative. That visual contrast helps the reader see why the interaction term is the key methodology-aligned AI-washing result.

[Insert Figure 3 here]

## 9. Figure 3 to Figure 4

After the interaction has been established statistically and visualized graphically, it becomes natural to ask how common the mismatch phenomenon actually is and where it appears in the sample. Figure 4 answers that descriptive question. It moves from regression evidence to sample-level incidence by showing both the time evolution of PatentMismatch and its concentration across broad sectors. That shift is useful because it makes clear that the mismatch construct is not an abstract regression artifact; it is a pattern that becomes more prevalent late in the sample and is concentrated in specific parts of the economy.

[Insert Figure 4 here]

## 10. Figure 4 to Table 7C

Once the paper has shown what PatentMismatch is and where it appears, the next natural question is who is more likely to exhibit it. Table 7C is the cleanest current entry point for that discussion because it preserves much more of the baseline-firm sample than the fullest multivariate version while still retaining the main financial-capacity controls. The right framing here is descriptive rather than mechanistic: the table identifies which firm characteristics are associated with mismatch in this design, and the fact that the pattern differs from the comparison paper is informative rather than problematic because the two papers are measuring different kinds of inconsistency between narrative claims and underlying innovation activity.

[Insert Table 7C here]

## 11. Main Text to Appendix

At this point, the main narrative is already complete: the reader has seen the sample, the disclosure buildup, the patent benchmark, the timing validation, the methodology-aligned mismatch result, the visual companion figures, and the first determinants evidence. The appendix should therefore be introduced as a place where the paper answers reasonable follow-up questions without distracting from that core sequence. The most natural appendix objects are the narrower speaking-only validation table, the exploratory credibility-metric family, and the fuller determinants variants, especially those that retain the R&D intensity measure or use the intensity-based mismatch outcome.

[Insert Appendix Table A1 here]

[Insert Appendix Table A2 here]

[Insert Appendix Table A3 here]

[Insert Appendix Table A4 here]

## 12. Closing Results Paragraph

Taken together, the results support a coherent interpretation of the disclosure measures. Broad AI-related narrative intensity is informative about AI innovation outcomes, but the composition of that language matters as well. More importantly, the methodology-aligned mismatch design shows that credibility in AI-related disclosure is associated with stronger future AI patent outcomes precisely when the underlying patent record does not already signal a mismatch. The final implication is not that all AI-related disclosure is misleading, but that the credibility of that disclosure varies systematically and can be studied using a design that links filing language to observed innovation behavior.
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
    args.output_markdown.write_text(TRANSITION_TEXT.rstrip() + "\n", encoding="utf-8")
    if args.skip_docx:
        print(f"[OK] assembled markdown transition notes: {args.output_markdown}")
        return 0
    build_docx(args.output_markdown, args.output_docx)
    print(f"[OK] assembled markdown transition notes: {args.output_markdown}")
    print(f"[OK] built transition notes docx: {args.output_docx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
