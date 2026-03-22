# Figure 2 Spec Card V1

Date:
- `2026-03-21`

Title:
- `Figure 2. AI Patent Coverage Over Time`

## Purpose

This figure gives the reader a visual sense of how sparse AI patenting is,
while also showing how patent intensity grows over time in the upper tail.

## Input

- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`

## Design

Panel A:
- share of firm-years with any AI patent

Panel B:
- mean AI patent count
- mean `log(1 + AI patents)`

## Narrative Role

Expected read:
- AI patenting remains sparse in the ever-speaker universe
- incidence rises over time
- the log transformation helps summarize growth without letting the upper tail dominate the visual

## Output Artifacts

- `output/figures/delivery_figures_v1/figure_2_ai_patent_coverage_prelim_v1.png`
- `output/doc/delivery_figures_v1/figure_2_ai_patent_coverage_prelim_v1.docx`
