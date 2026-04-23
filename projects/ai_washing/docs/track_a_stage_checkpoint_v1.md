# AI-Washing Track A Stage Checkpoint V1

## Purpose

This note is the live stage checkpoint for Track A.

Use it when resuming work to answer:

1. which Track A stage is currently active?
2. which stages are complete enough to stop revisiting?
3. what is the next concrete step after the current one?

This is the working status layer that sits on top of:

- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/projects/ai_washing/docs/track_a_execution_plan_v1.md`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`

## Current status as of 2026-04-10

### A1. 2025 filing refresh

Status:
- complete enough for current execution

Interpretation:
- the refreshed filing and patent backbone is no longer the blocker for Track A
- remaining refresh work can continue, but it is not on the current critical
  path

### A2. Model accuracy and robustness refresh

Status:
- complete enough for provisional economics execution

Key outcomes:
- `IRR v3 rerun` passed with `kappa = 0.85`
- local layered classifier plus API-A defer is the provisional winner
- the `conf49` shadow full-corpus API tranche is still running

Open tail:
- finish the running API-A deferred slice
- merge shard outputs back into the master deferred sheet

### A3. Capital-market consequence execution

Status:
- active stage

Substage status:

1. A3.1 filing event spine
   - complete
2. A3.2 filing-level AI measures
   - complete
3. A3.3 WRDS bridge
   - complete for the matched sample
   - `54 / 65` filings linked to `permno`
   - unresolved `11` rows isolated as audit tail
4. A3.4 daily event-return windows
   - complete
   - `54` filings with complete `CAR[-1,+1]`
   - `54` filings with complete `CAR[-2,+2]`
5. A3.5 lagged annual controls
   - complete
   - `54 / 54` filings received a lagged `comp.funda` control row
6. A3.6 first regression-ready estimation sample
   - complete
   - core CAR sample: `54`
   - extended CAR sample with R&D intensity: `42`
   - `BHAR 6m` core sample: `52`
7. A3.7 first regression implementation
   - complete
   - first pilot filing-date CAR and `BHAR 6m` regressions now exist on the matched sample
8. A3.8 expansion from pilot to hybrid-backed filing panel
   - active
   - broader raw WRDS fundamentals and monthly market inputs are already pulled
   - note: the current `13,777`-row WRDS backbone is still the observed AI-talking firm-year surface, not the fully expanded annual ever-speaker scaffold
   - the corrected pre-hybrid annual ever-speaker panel rebuild now exists at `50,840` rows across `5,084` firms and `10` years
   - the current blocker is the running `conf49` deferred API-A tranche
   - after that, merge provisional hybrid labels back into the broader filing panel, expand the annual panel to the full ever-speaker firm-year grid, and rerun the event-study regressions on the expanded sample

### A4. Identification design selection

Status:
- planned, not yet active

Interpretation:
- the design choice is already pointing toward post-ChatGPT interaction
- but the next practical step is still to expand the pilot event-study surface
  onto the broader hybrid-backed filing panel, not to open a new
  identification memo yet

### A5. Track A execution checkpoint

Status:
- pending

Exit condition:
- expanded market-reaction regression runs exist on the broader hybrid-backed
  filing panel
- the provisional hybrid classifier output is merged back into the deferred
  classification lane
- we can then decide whether Track A is ready to promote into the next paper
  execution phase

## Active stage

Current active stage:
- `A3.8`

Current concrete task:
- expand the pilot event-study regression surface from the matched `54`-filing sample to the broader hybrid-backed filing panel after the running API-A deferred slice finishes

## Immediate next steps

1. let the running `conf49` API-A tranche finish on the deferred slice
2. merge shard outputs back into the master deferred sheet
3. rebuild the filing-level AI measures and event-study panel on the broader provisional hybrid sample
4. derive expanded controls and market features from the already-pulled WRDS raw layers
5. rerun the first CAR and `BHAR 6m` regressions on the expanded panel

## Playbook review

Director playbook library was checked during the repeated shell / supervision
issues.

Current read:
- no existing curated playbook directly matches the Codex-shell background
  supervision issue
- the correct response was a low-blast-radius operational change:
  move long API runs to foreground Mac Terminal supervision with `caffeinate`

So the blocker was not a reusable extraction/model failure pattern.
It was a runtime-supervision issue.

## Bottom line

Track A is no longer in planning mode.

It is in active capital-market execution, and the current working stage is:
- `A3.8 expansion from pilot to hybrid-backed filing panel`
