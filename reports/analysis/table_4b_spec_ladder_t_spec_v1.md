# Table 4B Spec Card

Table title:
- `Table 4B. Specification Ladder for Contemporaneous AI Patent Timing`

Status:
- preliminary appendix / companion robustness table

## Purpose

This is the nearest-neighbor companion to Table 4.

Instead of future AI patenting at `t+1`, it uses contemporaneous AI patenting at `t`.
That lets us compare whether the result is primarily forward-looking or contemporaneous without mixing both stories in one object.

## Input

- primary file:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Dependent Variable

- `log(1 + AI patents_t)`

## Panels

### Panel A

- `has_actionable`

### Panel B

- `has_spec_only`

## Columns / Specification Ladder

- `(1)` firm + year FE, full sample
- `(2)` industry + year FE, full sample
- `(3)` firm + year FE, non-financial sample
- `(4)` firm + year FE, non-financial and non-utility sample

## Main-Text / Appendix Boundary

- companion / appendix candidate

Reason:
- it is a natural alternative angle on the same test
- it helps us interpret whether the timing relation is contemporaneous rather than predictive
- it should remain separate from Table 4 rather than be stacked into the same object

## Output Artifacts

- `paper/generated/tables/table_4b_spec_ladder_t_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_4b_spec_ladder_t_prelim_v1.docx`
