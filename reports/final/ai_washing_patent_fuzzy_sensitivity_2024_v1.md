# AI-Washing Patent Fuzzy Sensitivity 2024 V1

## Purpose

This note records the bounded `2024` fuzzy-matching sensitivity run for the
patent lane.

The goal was to test whether tight fuzzy matching could serve as a useful
robustness supplement to the current exact normalized hybrid method.

## Inputs

Outputs:
- `reports/final/ai_washing_patent_fuzzy_sensitivity_2024_v1.json`
- `reports/final/ai_washing_patent_fuzzy_sensitivity_2024_v1_examples.csv`

Settings:
- year: `2024`
- families:
  - `grant`
  - `pregrant`
- thresholds:
  - `0.90`
  - `0.95`
- gap rule:
  - `min_gap = 0.03`

## Results

### Grant family

Baseline:
- total patent matches: `40,931`
- AI patent matches: `2,122`

Fuzzy `0.90`:
- total patent matches: `105,018`
- AI patent matches: `4,453`
- added total matches: `64,087`
- added AI matches: `2,331`

Fuzzy `0.95`:
- total patent matches: `76,063`
- AI patent matches: `3,621`
- added total matches: `35,132`
- added AI matches: `1,499`

### Pregrant family

Baseline:
- total applications: `27,595`
- AI applications: `1,849`

Fuzzy `0.90`:
- total applications: `72,886`
- AI applications: `3,923`
- added total applications: `45,291`
- added AI applications: `2,074`

Fuzzy `0.95`:
- total applications: `51,557`
- AI applications: `3,302`
- added total applications: `23,962`
- added AI applications: `1,453`

## Critical read

These jumps are too large to be credible as a benign robustness effect.

Manual spot checks show the current fuzzy supplement is pulling in clearly bad
matches driven by short or generic normalized terms.

Examples from the sample file:
- `City of Hope` -> matched to `CITY HOLDING CO` through `city`
- `NingBo New Beam ...` -> matched through `new`
- `CAPITAL ONE SERVICES, LLC` -> matched to `MARKFORGED HOLDING CORP` through
  `one`
- `INTELLECTUAL DISCOVERY CO., LTD.` -> matched to `WARNER BROS DISCOVERY INC`
  through `discovery`
- `EMERALD LAKE HILLS, L.L.C.` -> matched to `EMERALD HOLDING INC` through
  `emerald`
- `ADVANCED VIEW INC.` -> matched to `VIEW INC` through `view`

So even with:
- high thresholds
- a token-overlap rule
- a best-vs-second-best gap rule

the current fuzzy implementation remains too permissive.

## Conclusion

The current fuzzy supplement should **not** be scaled to `2014-2025`.

Recommended posture:
- keep the exact normalized hybrid method as the baseline
- keep the current fuzzy run only as a rejected stress test

## If we revisit fuzzy matching later

It would need stronger constraints first, such as:
- reject single generic matched tokens
- require multiple meaningful shared tokens
- add a stoplist for generic terms like `city`, `new`, `one`, `view`,
  `discovery`, `southern`
- possibly require a curated alias dictionary or historical legal-name registry

That would be a new method, not a small parameter tweak.

## Bottom line

The bounded fuzzy test was worth running because it gives a clean answer:

`the current exact normalized hybrid patent matching method is the right baseline, and the current fuzzy supplement is too noisy to use even as a routine robustness lane`
