# Methodology Metric Role Audit V1

Date:
- `2026-03-21`

Source reviewed:
- `paper/source/AI Washing - SK - Methodology.docx`

## Main conclusion

The methodology does **not** treat all narrative metrics as interchangeable patent-prediction regressors.

The current `Table 5 / Table 5B` family is useful as an exploratory credibility-metric table, but it is **not** the final methodology-aligned AI-washing specification.

The methodology instead distinguishes three roles:

1. baseline intensity / control-style measures
2. secondary credibility-tilt robustness measures
3. primary AI-washing specification

## Metric roles from the methodology

### `AI_Focus`

Closest wording / formula:
- `AI Focus_{i,t} = log(1 + AI sentences_{i,t})`

Role:
- baseline intensity measure
- also proposed as an industry-year narrative trend control in heterogeneity / robustness work

Interpretation:
- useful benchmark regressor or control
- not the primary AI-washing construct

### `SpecShare`

Closest wording / formula:
- `SpecShare_{i,t} = S_{i,t} / (A_{i,t} + S_{i,t})`

Role:
- credibility-tilt measure
- secondary robustness check in the methodology
- also part of the qualitative mismatch logic: high `SpecShare` contributes to low-credibility years

Interpretation:
- conceptually weak or negative against future patents
- conceptually positive against mismatch / washing risk

### `CredAI`

Closest wording / formula:
- `CredAI_{i,t} = z(A_{i,t}) - z(S_{i,t})`
- within-sample standardization

Role:
- secondary credibility-tilt robustness measure

Interpretation:
- conceptually positive against future innovation if it captures credibility
- conceptually negative against mismatch / washing risk

### `A_S`

Closest wording / formula:
- `A_S_{i,t} = log(1 + A_{i,t} / (1 + S_{i,t}))`

Role:
- **primary AI-washing proxy**
- enters the methodology's explicit AI-washing regression

Interpretation:
- positive main effect expected against future patents / innovation
- should be the anchor measure when we build the actual AI-washing table

### `SpecMinusAct`

Methodology status:
- not present in the methodology doc

Role:
- repo-side exploratory construct only

Interpretation:
- should not be treated as a primary methodology-backed construct

### `PatentMismatch`

Closest wording:
- firm-years with low credibility (`low A_S / high SpecShare`) and weak contemporaneous AI patenting relative to the industry-year

Role:
- component of the **primary AI-washing specification**
- used through `A_S x PatentMismatch`

Interpretation:
- methodology expects the interaction coefficient to be negative:
  - `beta_2 < 0`
- the idea is attenuation of the credibility-innovation link in mismatch years

## Methodology-aligned regression roles

### Baseline predictive validation

Methodology expectation:
- use narrative content to predict innovation at horizons `l in {0,1,2}`
- firm and year FE as baseline
- industry x year FE as robustness
- actionable language should be positive
- speculative language should be weaker or zero

Implication for current tables:
- `Table 2`, `Table 3`, and `Table 4 / 4B` fit this lane well

### AI-washing specification

Methodology expectation:
- use:
  - `A_S`
  - `A_S x PatentMismatch`
- test innovation at `t+1` and `t+2`
- `SpecShare` and `CredAI` are secondary robustness checks, not the headline AI-washing design

Implication for current tables:
- the current `Table 5 / 5B` should be treated as:
  - exploratory credibility-metric evidence
  - likely appendix or supervisor-review material
- the methodology-aligned AI-washing table is now implemented as:
  - `Table 6 / 6B`
  - using `A_S` and `A_S x PatentMismatch`

## Delivery implication

Recommended positioning now:
- keep `Table 5 / 5B` as modular exploratory credibility tables
- do **not** present them as the final AI-washing specification
- use `Table 6 / 6B` as the methodology-aligned AI-washing table family

That keeps the delivery package honest while preserving the useful work already done.
