# Figure 4. PatentMismatch Incidence Over Time and by Industry

## Purpose
This figure makes the mismatch construct concrete after the main methodology-aligned mismatch regressions. It shows when PatentMismatch incidents are most prevalent and where they are concentrated across broad industry groupings.

## Input Sample
- Source panel: `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- Sample restriction for plotting: AI-talking firm-years only (`any_ai_talk = 1`), because `PatentMismatch` is defined only when AI disclosure is observed.

## Construct Used
- `PatentMismatch = 1` when low-credibility disclosure composition (`low A_S` or `high SpecShare`) coincides with weak contemporaneous AI patenting relative to the industry-year benchmark.

## Figure Design
- Panel A: annual PatentMismatch incident count and annual PatentMismatch share among AI-talking firm-years.
- Panel B: top industry buckets by PatentMismatch incident count, annotated with mismatch share and AI-talking sample size.
- Industry buckets are broad SIC2-based sectors for readability in a one-page figure.

## Narrative Role
This figure follows the mismatch regression table. The goal is not causal identification; it is to make the phenomenon visible in the sample by showing whether mismatch is concentrated in particular years or sectors.

## Output Artifacts
- Image: `output/figures/delivery_figures_v1/figure_4_mismatch_incidence_industry_prelim_v1.png`
- Review DOCX: `output/doc/delivery_figures_v1/figure_4_mismatch_incidence_industry_prelim_v1.docx`
