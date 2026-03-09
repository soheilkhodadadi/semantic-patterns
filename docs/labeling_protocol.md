# Labeling Protocol (Proposal-Aligned Rubric v2)

This protocol defines how to label AI-related filing sentences for the AI-washing project after proposal-methodology alignment.

## Purpose

The project is not only a sentence classifier. It is a predictive credibility-measure project.

The sentence labels exist to support firm-year measures that can later be tested against observable AI capability proxies such as:
- AI-related patents
- AI-skills job postings

Because of that objective:
- rubric refinement is allowed during development calibration
- rubric drift is not allowed after rubric freeze
- the frozen held-out set remains evaluation-only throughout

## Scope and Unit of Labeling

- Labeling unit: sentence-level with context metadata.
- Required contextual fields: `source_file`, `source_year`, `source_form`, `source_cik`, `sentence_index`.
- Stable IDs:
  - `sentence_norm`: lowercase + strip punctuation + collapse whitespace.
  - `sentence_id`: `sha1(sentence_norm)[:16]`.
  - `sample_id`: `sha1(source_file|sentence_index|sentence_norm)[:16]`.

## Allowed Labels

- `Actionable`: sentence describes explicit current or realized firm-specific AI deployment, implementation, embedded workflow, productized use, or measurable operational execution.
- `Speculative`: sentence describes firm-specific aspirational, exploratory, or forward-looking AI narrative without operational proof.
- `Irrelevant`: sentence mentions AI in a generic, boilerplate, market-wide, regulatory, cyber-risk, list-like, or tangential way that does not function as a firm capability claim.

Rows with labels outside this set fail QA.

## Proposal-Faithful Decision Rules

### Actionable
Prefer `Actionable` when the sentence clearly shows one or more of the following:
- current deployment or current use
- already-implemented AI workflow or operational process
- productized or embedded AI functionality
- realized execution with concrete detail
- evidence that the firm is already using AI in a specific business activity

A sentence may still be `Actionable` inside a risk section if it reveals current firm AI deployment or use.

### Speculative
Prefer `Speculative` when the sentence clearly shows:
- future-looking plans or intentions
- AI ambitions, aspirations, or exploratory initiatives
- expected future benefits from AI
- narrative signaling around AI transformation without operational proof
- promises, goals, or pursuits of AI capability not yet shown as implemented

A sentence is not `Speculative` simply because it is uncertain or risk-oriented. It must still be a firm-specific AI narrative claim.

### Irrelevant
Prefer `Irrelevant` when the sentence is:
- generic AI market or technology commentary
- generic legal, cyber, regulatory, or business-risk language about AI
- broad boilerplate mention of AI among many topics
- not really a firm capability claim
- discussing AI as an external topic rather than the firm's own implemented or aspired capability

## Borderline Rules

- Generic AI regulatory, cyber, or market-risk language is `Irrelevant` unless the sentence also reveals current firm AI deployment.
- If a sentence only says AI may matter, could matter, or creates risks/opportunities in general, it is usually `Irrelevant`.
- If a sentence says the firm plans, expects, explores, or intends to use AI but does not show current operational evidence, it is `Speculative`.
- If a sentence shows current or realized deployment, it is `Actionable` even if it also contains risk or forward-looking context.
- If both action and aspiration appear, prefer:
  - `Actionable` when present or realized execution is explicit
  - `Speculative` when future intent dominates and current execution evidence is absent

## Tranche-1 Realignment Rule

`labeling_batch_v1` is diagnostic tranche 1 only.

Current policy:
- tranche 1 canonical labeling is paused under the older rubric
- tranche 1 must be re-prelabeled and re-reviewed under rubric v2
- previously generated tranche-1 prelabels are diagnostic evidence, not final canonical labels

Required tranche-1 realignment outputs:
- revised protocol in this file
- tranche-1 rubric realignment note
- tranche-1 assistive prelabels regenerated under rubric v2 before canonical human verification resumes

## Uncertainty Policy

- Use `is_uncertain=1` when label confidence is insufficient.
- Always provide `uncertainty_note` for uncertain rows.
- Uncertain rows may be retained for adjudication but should be clearly marked.

## Data Hygiene Rules

- No empty sentences.
- No missing labels for non-uncertain rows.
- Minimum token count: `>= 6`.
- No overlap by `sentence_norm` with the frozen held-out set:
  - `data/validation/held_out_sentences.csv`
- Deduplication policy:
  - exact dedupe by `sentence_norm`
  - exact text dedupe by `sentence_text_id`
  - conflicting duplicates must be routed before canonical merge

## Frozen Held-Out Policy

- `data/validation/held_out_sentences.csv` remains frozen evaluation-only.
- It must not be repurposed for training, tranche selection, or assistive prompt examples.
- It must not be reused as the IRR source set.

## Assistive API Policy

- OpenAI API output is assistive-only and never canonical by default.
- API output is not IRR and must not replace the second-rater workflow.
- Human raters remain the source of truth for final canonical labels.
- Assistive prelabels may populate review columns only.
- Assistive prelabels must never overwrite canonical `label`.
- Returned confidence is informational only.
- No downstream outcomes, patents, returns, or later panel variables may appear in prompts or adjudication reasoning.

## Calibration and Freeze

### Calibration
During development, rubric refinement is allowed when:
- tranche evidence shows the current labels do not reflect the proposal's construct
- predeclared predictive-validity checks show weak directional fit between disclosure measures and later AI capability proxies

### Freeze
Rubric freeze is required before publication-scale deployment.

After provisional freeze:
- large-scale labeling and retraining proceed under the frozen rubric
- any later rubric change requires a formal review-driven return to rubric realignment

## IRR Workflow

IRR is a human-human reliability check on the canonical labeled pool.

Required design:
- stratified sample covering at least `100` firms
- balanced by industry and year
- two independent human raters
- third adjudicator for disagreements
- report Cohen's kappa overall and by class

IRR gate policy:
- human-human only
- `kappa > 0.7`
- at least `100` reviewed items
- by-class kappa diagnostics required before retraining

## Iteration 2 Execution Model

Iteration 2 is no longer interpreted as continuous labeling under the old rubric.

It now proceeds in this order:
1. rubric realignment
2. tranche 1 labeling under rubric v2
3. sentence-pool expansion
4. tranche 2 labeling
5. tranche 3 labeling
6. canonical label merge
7. IRR and adjudication
8. provisional rubric freeze and split registry
9. label sufficiency gate

Fixed tranche sizes:
- tranche 1 = `240`
- tranche 2 = `160`
- tranche 3 = `160`

Retraining remains blocked until all of the following pass:
- `>=500` adjudicated labels
- `>=80` labels per class
- zero held-out overlap
- proposal-style IRR gate
- split registry freeze
- provisional rubric freeze

## Later Measure Construction

Later firm-year construction should explicitly publish:
- `AI Focus = log(1 + AI sentences)`
- `log(1 + A)`
- `log(1 + S)`
- `SpecShare = S / (A + S)`
- `CredAI = z(A) - z(S)`
- `A_S = log(1 + A / (1 + S))`

These measures are part of the proposal's core methodology and must remain visible in the roadmap and review artifacts.
