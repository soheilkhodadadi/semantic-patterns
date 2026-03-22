# PatentMismatch Construct V1

Date:
- `2026-03-21`

Panel:
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Purpose

`PatentMismatch` operationalizes the methodology's idea of divergence between AI talk quality and contemporaneous AI innovation. It is designed for the methodology-aligned AI-washing table that regresses future AI patent outcomes on the `A_S` ratio and the interaction `A_S × PatentMismatch`.

## Construction

At the firm-year level:

1. `LowCredibility_{i,t} = 1` if the firm-year is an AI-talking year and either:
- `A_S` is in the bottom year-specific quartile among AI-talking firm-years, or
- `SpecShare` is in the top year-specific quartile among AI-talking firm-years.

2. `WeakPatentRelative_{i,t} = 1` if contemporaneous `log(1 + AI patents)` is below the industry-year mean of contemporaneous `log(1 + AI patents)`.

3. `PatentMismatch_{i,t} = 1` if:
- the firm-year is an AI-talking year,
- `LowCredibility_{i,t} = 1`, and
- `WeakPatentRelative_{i,t} = 1`.

4. `AS_x_PatentMismatch_{i,t} = A_S_{i,t} × PatentMismatch_{i,t}`.

## Current incidence

Using the regression-ready ever-speaker annual panel:

- Ever-speaker firm-year observations: `18,741`
- AI-talking firm-year observations: `6,152`
- `PatentMismatch = 1` observations: `1,972`
- Mismatch share of the ever-speaker sample: `0.105`
- Mismatch share of AI-talking firm-years: `0.321`

## Interpretation

This construct is intentionally conservative in two ways:

- it only flags firm-years that actually talk about AI, and
- it requires weak contemporaneous AI patenting relative to the industry-year benchmark.

So the interaction coefficient in the methodology-aligned regression should be read as attenuation of the credibility-innovation slope in low-credibility / weak-innovation years.

## Current empirical read

In the first methodology-aligned tables:

- `A_S` enters positively,
- `A_S × PatentMismatch` enters negatively,
- the negative interaction is clearer at `t+1` than at `t+2`,
- and the industry×year specification produces the strongest version of the pattern.

That is directionally aligned with the methodology expectation that AI-washing weakens the positive link between credible AI talk and future AI innovation.
