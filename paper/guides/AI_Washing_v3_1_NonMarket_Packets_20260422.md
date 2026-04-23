# AI-Washing v3.1 Non-Market Packet Queue

Date: 2026-04-22  
Status: Active execution queue  
Scope: measurement validation, alternative construct variants, real outcomes, and the financing / governance consequence lane after the market-identification package.

## 1. Why This Queue Exists

The stricter market package did its job.

It showed that the paper can keep a market section, but it should not lean on a broad underreaction or correction claim as the main empirical payoff. The strongest path now is to deepen the parts of the paper that are already more defensible:

- audited measurement;
- construct validation;
- stronger non-market consequences;
- disciplined extension checks for nearby AI-washing variants;
- financing / incentive consequences only where the current panel can support them.

This queue turns that pivot into a stable sequence so we do not drift into ad hoc tests.

## 2. Current Working Principle

For the next wave, the goal is not to rescue every prior hypothesis.
The goal is to find the strongest paper-grade evidence that survives scrutiny.

That means:

1. start with tests that use the current canonical panel cleanly;
2. separate true empirical runs from data-gap or feasibility work;
3. treat nearby construct variants as an extension layer, not a retroactive replacement for the audited canonical construct;
4. only promote a variant or consequence block into the main text if it is both interpretable and more defensible than the alternatives.

## 3. Packet Sequence

### Packet A. Construct-Variant Validation Screen

Test family:
- `test_16_construct_variant_screen`

Question:
- among nearby AI-washing indicators, which ones most cleanly predict later technology realization inside the AI-talking sample?

Why this goes first:
- it uses the current annual panel immediately;
- it strengthens the paper's measurement and validation spine;
- it tells us whether the canonical `PatentMismatch` remains the right main construct or whether a nearby variant deserves appendix / robustness status.

Prespecified sample:
- AI-talking firm-years only.

Prespecified outcomes:
- `log_patents_ai_lead1`
- `log_patents_ai_lead2`
- `log_applications_ai_lead1`
- `log_applications_ai_lead2`

Prespecified variants:
- `PatentMismatch` (canonical grant-based mismatch)
- `StrictPatentMismatch` (stricter low-credibility disclosure rule + weak grant-based capability)
- `ApplicationMismatch` (low-credibility disclosure + weak application-based capability)
- `LowCredibility` (disclosure-side only)
- `WeakPatentRelative` (capability-side only)

Core controls:
- `AI_Focus`
- `ln_assets`
- `leverage`
- `cash`
- `roa`

Design rule:
- firm and year fixed effects;
- firm-clustered standard errors;
- same sample discipline across variants and outcomes wherever feasible.

Decision rule:
- keep the canonical construct as main if it remains among the strongest and most interpretable predictors of later AI realization;
- graduate any stronger nearby variant into appendix / robustness only if it adds a cleaner story rather than just one isolated coefficient.

### Packet B. Stronger Real-Outcome Dynamics

Test family:
- `test_17_real_outcome_dynamics`

Question:
- do low-credibility AI disclosers subsequently differ in real operating and innovation behavior once we focus on the strongest horizons and the AI-talking sample?

Why this is second:
- it turns the paper away from fragile market-return claims and toward consequences that are closer to firm behavior.

Prespecified outcome family:
- future `ROA`
- future `sales_growth`
- future `CAPX/assets`
- future `R&D/assets`
- at `t+1` and `t+2`

Planned comparison sets:
- canonical `PatentMismatch`
- best surviving variant from Packet A if it is clearly more informative
- optional AI-talking-only refinement if that materially improves interpretability

Decision rule:
- prioritize outcomes that show a coherent economic story across horizon and sign, not just isolated significance;
- if the strongest pattern is something like lower later profitability but higher later R&D, write that as a costly catch-up or delayed capability-build story only if the timing is consistent.

### Packet C. Financing / Incentive Consequence Refresh

Test family:
- `test_18_financing_incentives_refresh`

Question:
- do the current panel's valuation and financing fields contain a defensible non-market consequence block once we revisit them under the new discipline?

Why this is third:
- some financing proxies already exist in the current panel;
- the governance side does not yet, so this packet must separate what we can estimate now from what still needs data.

Current feasible lane with existing data:
- refresh the existing valuation / financing setup built around market-capitalization and share-growth outcomes;
- consider non-big refinement only if the main table is diffuse but directionally coherent.

Current not-yet-feasible lane with the canonical panel alone:
- board governance;
- institutional ownership;
- analyst coverage or forecast dispersion;
- richer issuance incentives beyond the current share-growth proxy.

Deliverables:
- one empirical refresh if the current fields support it;
- one short data-gap note listing what additional sources would be needed for a true governance / institutional extension.

## 4. What Counts As Success In This Queue

Success is not “every packet yields a main-text table.”

Success is:
- we learn which construct version is strongest;
- we learn which non-market outcomes are economically coherent;
- we stop spending time on weak lanes once the evidence says they are weak;
- by the end, the paper has a cleaner backbone for main text and appendix.

## 5. Immediate Execution Order

1. run Packet A now;
2. freeze the main and appendix candidates from Packet A;
3. open Packet B using the winning construct posture from Packet A;
4. only then decide how much effort Packet C deserves with the current panel.
