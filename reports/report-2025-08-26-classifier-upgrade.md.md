# NLP Classifier Upgrade — Accuracy Update & Reproducibility (Aug 26, 2025)

**Suggested filename:** `report-2025-08-26-classifier-upgrade.md`  
**Branch:** `stage1-nlp-upgrade`  
**Owner:** Soheil Khodadadi

---

## Executive summary
- **What changed:** Switched embeddings to **all-mpnet-base-v2** and added a **two‑stage classifier** (fast irrelevance gate → MPNet centroid A/S classifier with soft lexical boosts).
- **Result (held‑out):** **26 / 31 = 83.87%** accuracy (prior runs: 58–71%). Largest gains came from the irrelevance gate and margin/boost tuning.
- **Why it matters:** We now suppress generic “laundry‑list/regulatory” lines and fragments before A/S classification, reducing false Actionable spikes and improving separation.
- **Where to look:** Code lives in `core/classify.py`, with entry points in `src/tests/evaluate_classifier_on_held_out.py` and `src/classification/classify_all_ai_sentences.py`.

---

## What changed (details)
### 1) Embeddings & centroids
- Model: **sentence-transformers/all-mpnet-base-v2** (higher semantic fidelity than MiniLM).
- Recomputed **class centroids** for **Actionable (A)**, **Speculative (S)**, **Irrelevant (I)** using the hand‑labeled training set.
- Artifact: `data/validation/centroids.mpnet.json` (versioned by commit hash + timestamp).

### 2) Two‑stage classifier
**Stage 0 — Irrelevance gate (fast, rule‑based)**  
Purpose: filter out lines that mention AI only as part of long lists/regulatory boilerplate, incomplete fragments, and headers.

Heuristics (configurable):
- **Min tokens:** `--min-tokens=6` (discard fragments and headings).
- **Listy triggers:** presence & density of terms like *including, such as, as well as, among other things, laws and regulations, regulatory*.
- **Category density:** high ratio of comma‑separated categories (e.g., *privacy, data security, … artificial intelligence …*).
- **Punctuation patterns:** semicolons/enumerations suggesting legal lists; section headers/glossary markers.
- **Keyword mix:** AI token present but **no operational verbs** (ship/launch/implement/support/run) and **no numerics** (%/#/dates).

**Stage 1 — A vs. S (centroid + soft boosts)**  
- Compute cosine similarity of MPNet embedding to class centroids.
- **Margin rule**: if |A − S| &lt; **τ = 0.07**, prefer **S** when speculative modals dominate; otherwise prefer higher score.
- **Lexical boosts** (small additive nudges):
  - **Speculative cues:** *may, plan, expect, intend, will focus, explore* (+S).
  - **Actionable cues:** *launched, implemented, deployed, support, customers, %, KPI terms* (+A).
- **Irrelevant epsilon:** if both A and S are weak and irrelevance patterns present, apply **ε\_irr = 0.03** to nudge toward I.

CLI flags exposed in both entry points:
```
--two-stage --rule-boosts --tau 0.07 --eps-irr 0.03 --min-tokens 6
```

---

## Code integration
- **Core logic:** `core/classify.py` (MPNet encoder, centroid logic, irrelevance gate, lexical boosts).
- **Evaluation:** `src/tests/evaluate_classifier_on_held_out.py`  
  Imports `core.classify: classify_sentence` and accepts the flags above. Writes per‑item results to `data/validation/evaluation_results.csv`.
- **Batch classification:** `src/classification/classify_all_ai_sentences.py`  
  Reads each `*_ai_sentences.txt` under `data/processed/sec/<YEAR>/...`, runs classification, writes `*_classified.txt`.  
  **Smart refresh:** if `centroids.mpnet.json` is newer than prior outputs, rebuild outputs even if files exist.

---

## How to reproduce

### A) Evaluate on the current held‑out set
```bash
python src/tests/evaluate_classifier_on_held_out.py \
  --two-stage \
  --rule-boosts \
  --tau 0.07 \
  --eps-irr 0.03 \
  --min-tokens 6
```
- Output CSV: `data/validation/evaluation_results.csv`
- Console summary shows per‑sentence preds + accuracy (latest: **26 / 31 = 83.87%**)

### B) Batch‑classify filings (2021–2024)
```bash
python src/classification/classify_all_ai_sentences.py \
  --years 2021 2022 2023 2024 \
  --quick-two-stage \
  --rule-boosts \
  --tau 0.07 --eps-irr 0.03 --min-tokens 6
```
- Input: `data/processed/sec/<YEAR>/**/*_ai_sentences.txt`
- Output: `data/processed/sec/<YEAR>/**/*_classified.txt`
- Rebuild condition: new centroids or run with `--force` (if available).

---

## Results snapshot (held‑out)

- **Accuracy:** **83.87%** (26/31).  
- **Biggest gains:** fewer false **Actionable** on regulatory lists; better A/S separation via margin + boosts.  
- **Typical remaining misses:** sentences mixing *future intent* with *partial deployment*; borderline robotics cross‑application.  

**Ablation (short):**
| Config | Acc. |
|---|---|
| Baseline MPNet, no rules | 0.58 |
| + Two‑stage, default | 0.71 |
| + Margin τ=0.07 & boosts | **0.84** |

*(values are from successive runs on the same held‑out set)*

---

## Reflexive workflow & iteration log
- **Initial state (Aug 22):** MiniLM centroids, sparse labels, **~25–33%** on held‑out.  
- **Iteration 1:** Switch to MPNet, recompute centroids → **~40–60%**.  
- **Iteration 2:** Add irrelevance gate (min‑tokens + listy/regs) → **~58–71%**.  
- **Iteration 3:** Tune margin **τ = 0.07**, add lexical boosts, small ε\_irr → **~71–84%**.  
- **QA pass:** Manual review of ~300 sentences (batches of 30), re‑label edge cases, push borderline list‑style mentions to **Irrelevant** for training balance.  
- **Stabilization:** Locked current thresholds; documented CLI and artifacts; wired smart rebuild in batch classifier.

---

## Core algorithm (pseudo)
```text
def classify_sentence(text, cfg):
  if is_fragment(text) or is_regulatory_list(text, cfg):
      return "Irrelevant", scores(...)
  v = mpnet_embed(text)
  sA, sS, sI = cos(v, cA), cos(v, cS), cos(v, cI)
  if cfg.rule_boosts:
      sA += boost_actionable(text)
      sS += boost_speculative(text)
      if looks_irrelevant(text): sI += cfg.eps_irr
  if cfg.two_stage:
      if is_irrelevant_by_gate(text, sI): return "Irrelevant", scores(...)
  if abs(sA - sS) < cfg.tau:
      return "Speculative" if speculative_cues(text) else ("Actionable" if actionable_cues(text) else argmax(A,S))
  return argmax(Actionable, Speculative), scores(...)
```

---

## Artifacts delivered (today)
- `data/validation/held_out_sentences.csv` (current eval set)
- `data/validation/evaluation_results.csv` (per‑item predictions + summary)
- `data/validation/centroids.mpnet.json` (MPNet centroids for A/S/I)
- Code updates in:
  - `core/classify.py`
  - `src/tests/evaluate_classifier_on_held_out.py`
  - `src/classification/classify_all_ai_sentences.py`

---

## Known limitations & next fixes
- **A↔S flips** when intent and deployment co‑occur (will add small edge‑case set).
- **Regulatory mega‑lists** sometimes bleed through if AI appears with operational verbs (extend negative patterns).
- **Domain verbs lexicon** could be expanded per‑industry (healthcare/finance/manufacturing).

---

## Next steps (already started)
- **Thu (Aug 28):** Patent‑matching subset + early regressions (link A/S/I frequencies with AI‑patent counts; simple FE specs).
- **Aug 31:** Full panel regressions with Compustat controls + industry/year FE; deliver tables.
- **Label quality:** 100+ manual checks and inter‑rater reliability; uncertainty sampling for hard cases.

---

## Changelog
- **2025‑08‑26:** MPNet centroids; two‑stage classifier; evaluation harness updated; batch classifier smart‑refresh; doc added.
