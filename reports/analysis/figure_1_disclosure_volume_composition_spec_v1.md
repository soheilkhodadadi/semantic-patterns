# Figure 1 Spec Card V1

Date:
- `2026-03-21`

Title:
- `Figure 1. AI Disclosure Volume and Composition Over Time`

## Purpose

This figure is the first descriptive visual for the main-text story.
It shows how AI disclosure grows over time and how its composition changes.

## Input

- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`

## Design

Panel A:
- mean AI sentence counts per firm-year
- series:
  - total AI sentences
  - actionable sentences
  - speculative sentences

Panel B:
- composition over time
- series:
  - mean actionable share among AI-talking firm-years
  - mean speculative share among AI-talking firm-years
  - share of ever-speaker firm-years with any AI disclosure

## Narrative Role

Expected read:
- AI disclosure volume rises strongly over time
- actionable and speculative components both grow
- composition changes can be read separately from volume growth

## Output Artifacts

- `output/figures/delivery_figures_v1/figure_1_disclosure_volume_composition_prelim_v1.png`
- `output/doc/delivery_figures_v1/figure_1_disclosure_volume_composition_prelim_v1.docx`
