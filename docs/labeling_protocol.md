# Labeling Protocol (Proposal-Aligned Rubric v2.3)

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

- `Actionable`: sentence describes a firm-specific present or past factual AI claim, including current use, implementation, capability, investment, expertise, or AI product/service offering.
- `Speculative`: sentence describes a firm-specific but vague, exploratory, or forward-looking AI narrative without a present or past factual claim of use, capability, or investment.
- `Irrelevant`: sentence mentions AI in a generic, boilerplate, market-wide, regulatory, cyber-risk, list-like, or tangential way that does not function as a firm capability claim.

Rows with labels outside this set fail QA.

## Proposal-Faithful Decision Rules

### Actionable
Prefer `Actionable` when the sentence clearly shows one or more of the following:
- current deployment or current use
- already-implemented AI workflow or operational process
- productized or embedded AI functionality
- realized execution stated as a present or past fact
- current investment, resource allocation, capability-building, or expertise that is firm-specific and presented as a fact
- present-tense commercialized AI offering, product, or service
- evidence that the firm is already using AI in a specific business activity

Technical detail is not required in the same sentence. A present-tense factual firm claim can still be `Actionable`.

A sentence may still be `Actionable` inside a risk section if it reveals current firm AI deployment or use.

### Speculative
Prefer `Speculative` when the sentence clearly shows:
- future-looking plans or intentions
- AI ambitions, aspirations, or exploratory initiatives
- expected future benefits from AI
- narrative signaling around AI transformation without operational proof
- promises, goals, or pursuits of AI capability not yet shown as implemented
- language framed as possibility, aspiration, or opportunity rather than current fact

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
- If a sentence only says AI may matter, could matter, or creates generic risks/opportunities, it is usually `Irrelevant`.
- If a sentence says the firm plans, expects, explores, or intends to use AI but does not show current operational evidence, it is `Speculative`.
- If a sentence shows a current or past factual firm claim about AI deployment, capability-building, expertise, investment, or a current AI offering, it is `Actionable` even if it does not include technical detail.
- If both action and aspiration appear, prefer:
  - `Actionable` when present or realized execution is explicit
  - `Speculative` when future intent dominates and current execution evidence is absent

## Proposal-Faithful Decision Tree

Use this order:
1. Does the sentence disclose current or past firm-specific AI deployment, embedded workflow use, operational execution, current investment/capability-building, expertise, or a commercialized AI offering?
   - If yes, label `Actionable`.
2. If not, does it describe a firm-specific AI strategy, aspiration, intention, expected benefit, exploration, or opportunity without a present/past factual claim?
   - If yes, label `Speculative`.
3. Otherwise, label `Irrelevant`.

This is intentionally short so the human rubric remains workable for IRR and second-rater use.

## Proposal-Faithful Borderline Examples

- `Speculative`: “Our global strategy includes investing in generative AI capabilities.”
  - firm-specific ambition or strategic priority, but no present execution evidence
- `Actionable`: “We offer AI-enabled technology products and services to customers.”
  - present business offering or productized capability stated as fact
- `Actionable`: “We have used our software engineering expertise to become a provider of AI-enabled transformation services.”
  - present-tense capability or offering stated as fact, even without technical implementation detail
- `Irrelevant`: “The use of AI/ML methods may create legal, cyber, and regulatory risks.”
  - generic AI risk language, not a firm capability claim
- `Speculative`: “We may find opportunities by developing and applying AI.”
  - firm-specific expected benefit or intended use without a current factual claim
- `Actionable` only by override: risk-section language that explicitly discloses current firm AI use or deployment
  - example pattern: “Our current AI underwriting system may fail under certain conditions”
  - the actionability comes from disclosing the present system, not from being inside a risk section

## Tranche-1 Realignment Rule

`labeling_batch_v1` is diagnostic tranche 1 only.

Current policy:
- tranche 1 canonical labeling is paused under the older rubric
- tranche 1 must be re-prelabeled and re-reviewed under rubric v2.3
- previously generated tranche-1 prelabels are diagnostic evidence, not final canonical labels
- canonical tranche-1 review now happens in:
  - `data/labels/v1/labeling_batch_v1_filled_v2_2.csv`
- earlier `v2` and `v2.1` review sheets remain diagnostic only

Required tranche-1 realignment outputs:
- revised protocol in this file
- tranche-1 rubric calibration note
- rebuilt slice40 extracted from raw filings
- tranche-1 assistive prelabels regenerated under rubric v2.2 before canonical human verification resumes

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
1. rubric realignment and slice40 recalibration under rubric v2.2
2. tranche 1 labeling under rubric v2.2
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

## Later Filing-Level Derived Variables

In addition to sentence-level and firm-year continuous measures, later robustness work may publish filing-level summary variables such as:
- `AnyActionable = 1` if a filing contains any actionable AI sentence
- `SpeculativeOnly = 1` if a filing contains speculative AI sentences but no actionable AI sentence

These are future derived measures and are not part of the current sentence-labeling gate.
