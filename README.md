# Semantic Patterns

**AI/NLP pipelines for financial disclosure, source validation, and quantitative testing.**

This repository contains the code and lightweight documentation behind a research workflow for measuring AI-related language in corporate filings and testing whether those disclosure signals are supported by external evidence. The main use case is an AI-washing / disclosure-credibility project using U.S. 10-K filings, sentence-level NLP classification, patent evidence, market data, and empirical finance validation.

The project is designed around one practical question:

> Can noisy corporate AI language be converted into audited, source-linked, decision-ready signals rather than treated as raw mention counts?

## What This Repository Demonstrates

- **Financial-text NLP:** extraction and classification of AI-related sentences from SEC filings.
- **Rubric-based AI evaluation:** actionable, speculative, and irrelevant AI-language taxonomy with human-audited labels.
- **Model benchmarking:** transformer embeddings, centroid classifiers, logistic baselines, held-out evaluation, and selective-defer logic.
- **Disclosure credibility scoring:** firm-year measures that combine language quality with contemporaneous patent evidence.
- **Quantitative validation:** links from text-derived signals to patents, filing-window returns, BHARs, factor-adjusted portfolios, scrutiny, incentives, and financing windows.
- **Research QA:** versioned documentation, manifests, validation reports, generated tables, and manuscript-support workflows.

## Project Snapshot

The current AI-washing research build covers U.S. public firms from **2016 to 2025**.

Selected project-scale metrics:

| Layer | Evidence |
| --- | --- |
| Classified corpus | 147,879 AI-related sentences |
| Sentence taxonomy | actionable, speculative, irrelevant |
| Human audit | 551 adjudicated labels |
| Held-out benchmark | 120 adjudicated cases |
| Human-audit reliability | Cohen's kappa = 0.850 after adjudication |
| Held-out model quality | 85.0% accuracy; 83.6% macro-F1; 91.7% binary AI relevance |
| Firm-year panel | 50,840 firm-year observations across 5,084 firms |
| AI-talking firm-years | 13,777 firm-years with at least one classified AI sentence |
| Credibility flag | PatentMismatch exceeds 40% of AI-talking firm-years in both 2024 and 2025 |

These figures are project-level research outputs, not packaged sample data. Raw SEC, WRDS, CRSP, Compustat, and patent-linkage inputs are not bundled in the public repository.

## Pipeline Overview

```text
SEC 10-K filings
    -> sentence extraction and AI-term screening
    -> human-audited sentence taxonomy
    -> model training, benchmarking, and held-out evaluation
    -> firm-year disclosure measures
    -> patent evidence and industry-year benchmarks
    -> PatentMismatch / disclosure-credibility scores
    -> market, patent, scrutiny, incentive, and financing-window tests
    -> tables, figures, validation reports, and manuscript assets
```

The key design choice is to separate three layers that are often mixed together:

1. **Rubric reliability:** can human reviewers consistently distinguish actionable AI use from vague or irrelevant AI language?
2. **Classifier quality:** can the model scale that taxonomy without leaking future outcomes into the label construction?
3. **External validation:** do the resulting firm-year signals line up with patents, market behavior, scrutiny, incentives, and financing windows?

## Repository Structure

```text
src/semantic_ai_washing/
  data/             Filing ingestion, sentence extraction, external data pulls
  labeling/         Labeling batches, adjudication, IRR, held-out split management
  classification/   Embeddings, classifiers, model benchmarks, selective-defer tools
  aggregation/      Firm-year measures, patent merges, panel construction
  patents/          Patent keyword filters, assignee matching, patent-count construction
  analysis/         Regressions, event studies, portfolios, generated tables/figures
  diagnostics/      Environment and runtime checks
  director/         Agent-assisted workflow orchestration experiments
  labcore/          Shared runtime, registry, evidence, and manifest utilities

docs/               Environment notes, pipeline maps, project documentation
projects/           Project-scoped documentation and run registries
packages/           Extracted shared packages under development
reports/            Analysis reports, validation summaries, audit notes
paper/              Manuscript support files, generated snippets, tables, and figures
output/             Local generated reports and delivery artifacts
```

The repository has been evolving from a single-paper codebase into a reusable research-lab workspace. Some legacy modules remain for compatibility, but new code should use the canonical `semantic_ai_washing.*` namespace.

## Public / Private Boundary

This is a code-and-documentation repository. It intentionally does **not** include large or licensed research inputs such as:

- raw SEC filing corpora;
- WRDS / CRSP / Compustat extracts;
- private patent-assignee linkage workbooks;
- heavyweight intermediate panels;
- unpublished coauthor review packages.

Heavy runtime artifacts are kept outside git in a local runtime workspace. The GitHub repository keeps the code, lightweight documentation, reproducibility scaffolding, and public-safe project structure.

## Environment Setup

Python baseline: **3.11+**

Recommended local setup:

```bash
make bootstrap
source .venv/bin/activate
make doctor
make lint
pytest -q
```

The Makefile configures the local path profile needed by the current workspace layout. For detailed environment notes, see [docs/environment_setup.md](docs/environment_setup.md).

## Core Workflow Commands

The exact end-to-end run depends on access to local data inputs. The commands below show the canonical module pattern used throughout the repo.

### 1. Extract AI-related sentences

```bash
python -m semantic_ai_washing.data.extract_ai_sentences \
  --input-dir data/processed/sec \
  --keywords data/metadata/ai_keywords.txt \
  --include-forms 10-K
```

### 2. Classify extracted sentences

```bash
python -m semantic_ai_washing.classification.classify_all_ai_sentences
```

### 3. Evaluate held-out classification quality

```bash
python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out
```

### 4. Aggregate firm-year disclosure measures

```bash
python -m semantic_ai_washing.aggregation.aggregate_classification_counts
```

### 5. Build panels and empirical outputs

Representative modules:

```bash
python -m semantic_ai_washing.aggregation.build_ever_speaker_annual_panel
python -m semantic_ai_washing.analysis.prepare_panel_for_regression
python -m semantic_ai_washing.analysis.run_modular_regression_portfolio
python -m semantic_ai_washing.analysis.generate_delivery_table_artifacts
python -m semantic_ai_washing.analysis.generate_paper_assets
```

Use `python -m semantic_ai_washing.<module>` for new work. Legacy direct `src/...` script calls are compatibility paths, not the preferred public interface.

## Selected Technical Components

### AI sentence taxonomy

The classification layer separates AI-related sentences into:

- **Actionable:** concrete AI deployment, embedded workflow, internal tool, or productized use.
- **Speculative:** aspirational or forward-looking AI language without enough operational detail.
- **Irrelevant:** generic or tangential AI references that do not indicate the firm's own capability.

### PatentMismatch scoring

`PatentMismatch` flags AI-talking firm-years where low-credibility disclosure composition coincides with weak contemporaneous AI patent support relative to industry-year peers. Future patent outcomes are excluded from score construction and used only for validation.

### Market and outcome validation

The analysis layer includes event-window returns, post-filing BHARs, calendar-time long-short portfolios, factor-adjusted alpha tests, patent-realization tests, SEC scrutiny blocks, executive-incentive links, and capital-raising windows. Results are interpreted with bounded claims: broad validation evidence is separated from sparse or exploratory evidence.

## Documentation Map

Good starting points:

- [docs/environment_setup.md](docs/environment_setup.md) - local environment and tooling
- [docs/pipeline_map.md](docs/pipeline_map.md) - pipeline orientation
- [docs/labeling_protocol.md](docs/labeling_protocol.md) - sentence-labeling logic
- [docs/preliminary_delivery_status_2026-03-20.md](docs/preliminary_delivery_status_2026-03-20.md) - historical delivery checkpoint
- [projects/ai_washing/README.md](projects/ai_washing/README.md) - project-scoped front door
- [docs/roadmap_v2/current_state_navigation_v1.md](docs/roadmap_v2/current_state_navigation_v1.md) - current restructure/navigation state

## Development Notes

Quality checks:

```bash
make format
make lint
pytest -q
```

Project conventions:

- Use `semantic_ai_washing.*` imports for new code.
- Keep heavyweight private data out of git.
- Prefer small, auditable modules and generated manifests over one-off notebooks.
- Record validation outputs and assumptions in `reports/` or project-scoped docs.
- Treat AI-assisted classification and writing workflows as auditable systems: preserve rubrics, held-out tests, source checks, and human review decisions.

## Related Portfolio Angles

This repository supports three public-facing portfolio themes:

1. **AI/NLP Evaluation for Financial Text** - audited sentence taxonomy, model benchmarking, held-out evaluation, and leakage checks.
2. **Disclosure Credibility Scoring** - source-linked scoring that combines text composition with patent evidence and documented interpretation limits.
3. **Quantitative Validation of AI/Text Signals** - empirical finance tests that connect NLP-derived disclosure signals to patents, returns, scrutiny, incentives, and financing windows.

## Status

Active research codebase. The AI-washing project is an active manuscript and technical research build, while the repository is also being refactored into a more reusable research-lab workspace. Public users should treat this as a technical research portfolio and codebase rather than a plug-and-play data package.

## License

See [LICENSE](LICENSE).
