# Figure 3 Spec Card V1

Date:
- `2026-03-22`

Title:
- `Figure 3. Patent Alignment and Mismatch by A/S Quantile`

## Purpose

This figure is the visual companion to the methodology-aligned mismatch table.
It shows how future AI patenting differs between mismatch and non-mismatch
firm-years across the disclosure-credibility distribution.

## Input

- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Design

Sample:
- regression-ready ever-speaker annual panel
- plotted observations restricted to AI-talking firm-years

Construction:
- pooled quantile bins of `A_S` among AI-talking firm-years
- plotted points use the within-bin median `A_S`
- split each bin by `PatentMismatch`

Panel A:
- model-implied within-sample effect on `log(1 + AI patents)` at `t+1`
- series:
  - no mismatch
  - `PatentMismatch = 1`

Panel B:
- model-implied within-sample effect on `log(1 + AI patents)` at `t+2`
- series:
  - no mismatch
  - `PatentMismatch = 1`

## Narrative Role

Expected read:
- non-mismatch firm-years should show a stronger positive gradient across `A_S` quartiles
- mismatch firm-years should show attenuation of future AI patenting, especially at `t+1`
- the figure should make the interaction result in Table 6 visually intuitive

## Output Artifacts

- `output/figures/delivery_figures_v1/figure_3_patent_mismatch_alignment_prelim_v1.png`
- `output/doc/delivery_figures_v1/figure_3_patent_mismatch_alignment_prelim_v1.docx`
