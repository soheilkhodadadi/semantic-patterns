import sys
import os
import re
import argparse
import pandas as pd

# Add src/ to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classify import classify_sentence  # base centroid classifier (A/S/I)

# ——— Quick two-stage helpers (rule gate + soft boosts; tuned) ———
import re

LISTY_TRIGGERS = re.compile(r"\b(including|such as|as well as|among other|and other)\b", re.I)
CATEGORY_WORDS = re.compile(r"\b(internet|e[- ]?commerce|web services|devices|advertis(ing|ement)|privacy|data protection|tax|employment|antitrust|tariff|omnichannel|electronic|robotics|virtual reality|blockchain|iot|cloud|edge computing)\b", re.I)
ALONGSIDE_PHRASE = re.compile(r"\b(is|are)\s+(?:among|alongside|one of|together with)\b", re.I)
GENERIC_MENTION = re.compile(r"\b(discussed|topic|focus|trend|coverage|buzzword|headline)\b", re.I)

INFRASTRUCTURE = re.compile(r"\bAI infrastructure such as (GPU|GPUs|accelerators)\b", re.I)
DATA_LEAKAGE = re.compile(r"^The use of AI .* (data leakage|exposure)", re.I)
STRATEGY_REEVAL = re.compile(r"reevaluated .* strategy .* artificial intelligence", re.I)

# Modals/intent; broadened to catch evaluating/exploring/future tense
MODALS = re.compile(r"\b(may|might|could|will|would|should|intend(?:s|ed)?\s+to|plan(?:s|ned)?\s+to|aims?\s+to|anticipate|seek|hope|explor(?:e|ing)|evaluat(?:e|ing))\b", re.I)
# Strong action cues for Actionable; prefer past/present deployments and ops
ACTION_VERBS = re.compile(r"\b(use|uses|using|deploy|deployed|embed|embedded|launch(?:ed|es)?|implement(?:ed|s)?|roll(?:ed)?\s+out|in\s+production|operational|customers|currently\s+use|reduced|improved|increased|support\s+live\s+operations|recommend|enhance|develop|build|apply|applied|applying|improve|improving|operate|operating)\b", re.I)
PCT_OR_NUM = re.compile(r"\b\d+(?:\.\d+)?%|\b\d{2,}\b")

# Extra refinements for evaluation stage
RISK_TERMS = re.compile(r"\b(risk|liability|lawsuit|lawsuits?|legal claim|legal liability|regulators?|regulation|compliance|reputation(al)?)\b", re.I)
FUTURE_PHRASES = re.compile(r"\b(will|going to|in the future|expected to|plan(?:s|ned)? to|intend(?:s|ed)? to)\b", re.I)
DEPLOYMENT_TERMS = re.compile(r"\b(deploy|deployed|launched?|rolled out|support live|operational|currently use)\b", re.I)

FOCUS_ON_AI = re.compile(r"focus(ed)? on .* (products|services).* based on AI", re.I)
FUTURE_FEATURES = re.compile(r"future (features|services)", re.I)


def adjust_scores_v2(text: str, scores: dict) -> dict:
    """Enhanced adjustment: risk/legal cues boost Speculative, deployment cues boost Actionable."""
    s = dict(scores)
    if RISK_TERMS.search(text):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.08
    if FUTURE_PHRASES.search(text):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.05
    if DEPLOYMENT_TERMS.search(text):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.08
    return s


def is_irrelevant_by_rules(text: str, min_tokens: int = 6) -> bool:
    """Lightweight coarse filter for obvious Irrelevant sentences.
    - Very short or header-like lines
    - Laundry-list/regulatory lists where AI is one of many items
    - 'alongside/among/one of' mentions with other techs
    - Glossary/definition style lines
    - Generic 'AI is discussed/focus/trend' statements
    """
    toks = text.split()
    if len(toks) < min_tokens:
        return True
    if text.endswith(":") or text.isupper():
        return True
    # glossary / definition
    if re.search(r"\b(glossary|definition|defined as)\b", text, re.I):
        return True

    # list/laundry-list style with AI among many items (relax thresholds)
    commas = text.count(",")
    has_list_trigger = bool(LISTY_TRIGGERS.search(text))
    has_category = bool(CATEGORY_WORDS.search(text))
    and_count = text.lower().count(" and ")
    if has_category and (has_list_trigger or commas >= 1 or and_count >= 1):
        # light density check only when long enough
        if len(toks) > 10 and not ACTION_VERBS.search(text):
            return True

    # "AI is among/alongside/one of ..." patterns
    if ALONGSIDE_PHRASE.search(text) and CATEGORY_WORDS.search(text):
        return True

    # generic sector/media focus without firm action
    if GENERIC_MENTION.search(text) and CATEGORY_WORDS.search(text):
        return True

    if INFRASTRUCTURE.search(text):
        return True
    if DATA_LEAKAGE.search(text):
        return True
    if STRATEGY_REEVAL.search(text):
        return True

    return False


def adjust_scores(text: str, scores: dict) -> dict:
    """Softly nudge scores using simple lexical cues."""
    s = dict(scores)
    if MODALS.search(text):
        s["Speculative"] = s.get("Speculative", 0.0) + 0.06
    if ACTION_VERBS.search(text) or PCT_OR_NUM.search(text):
        s["Actionable"] = s.get("Actionable", 0.0) + 0.06
    return s


def should_force_speculative(text: str) -> bool:
    """If explicit intent/future language appears and no strong action cues are present, force Speculative."""
    if (MODALS.search(text) and not ACTION_VERBS.search(text)) or FOCUS_ON_AI.search(text) or FUTURE_FEATURES.search(text):
        return True
    return False


def classify_two_stage(text: str, tau: float = 0.07, eps_irr: float = 0.03, min_tokens: int = 6, use_rule_boosts: bool = False):
    # Step 1: obvious Irrelevant
    if is_irrelevant_by_rules(text, min_tokens=min_tokens):
        return "Irrelevant", {"Actionable": 0.0, "Speculative": 0.0, "Irrelevant": 1.0, "fine_margin": None}

    # Step 2: Actionable vs Speculative with optional boosts
    label, scores = classify_sentence(text)
    if use_rule_boosts:
        scores = adjust_scores(text, scores)
        scores = adjust_scores_v2(text, scores)

    # Hard override: explicit future/intent with no strong action cues
    if should_force_speculative(text):
        scores["Speculative"] = scores.get("Speculative", 0.0) + 0.1

    a, s, irr = scores.get("Actionable", 0.0), scores.get("Speculative", 0.0), scores.get("Irrelevant", 0.0)
    fine_margin = abs(a - s)

    # If A/S are very close and Irrelevant is competitive, prefer Speculative to avoid over-claiming Actionable
    if fine_margin < tau and irr >= max(a, s) - eps_irr:
        label = "Speculative" if s >= a else "Actionable"
    else:
        label = "Speculative" if s >= a else "Actionable"

    scores["fine_margin"] = round(fine_margin, 3)
    return label, scores


def main():
    ap = argparse.ArgumentParser(description="Evaluate classifier on held‑out sentences.")
    ap.add_argument("--file", default="data/validation/held_out_sentences.csv", help="Held‑out CSV with columns: sentence,label")
    ap.add_argument("--two-stage", action="store_true", help="Use quick two‑stage (rule gate + A/S margin)")
    ap.add_argument("--rule-boosts", action="store_true", help="Apply soft boosts for A/S scores")
    ap.add_argument("--tau", type=float, default=0.05, help="Fine A/S margin threshold (default 0.05)")
    ap.add_argument("--eps-irr", type=float, default=0.02, help="Irrelevant closeness epsilon (default 0.02)")
    ap.add_argument("--min-tokens", type=int, default=6, help="Min tokens for non‑fragment (default 6)")
    args = ap.parse_args()

    df = pd.read_csv(args.file)

    correct = 0
    rows = []

    for _, row in df.iterrows():
        sent = str(row["sentence"]).strip()
        true = str(row["label"]).strip()
        if args.two_stage:
            pred, scores = classify_two_stage(sent, tau=args.tau, eps_irr=args.eps_irr, min_tokens=args.min_tokens, use_rule_boosts=args.rule_boosts)
        else:
            pred, scores = classify_sentence(sent)
        match = (pred == true)
        rows.append((sent, true, pred, match, scores))
        print(f"\n📝 {sent}\n✅ True: {true} | 🔮 Predicted: {pred} | {'✔️' if match else '❌'}")
        print(f"📊 Scores: {scores}")
        if match:
            correct += 1

    total = len(df)
    acc = correct / total if total else 0.0
    print(f"\n🎯 Accuracy: {correct} / {total} = {acc:.2%}")

    outp = "data/validation/evaluation_results.csv"
    pd.DataFrame(rows, columns=["sentence", "true_label", "predicted_label", "match", "scores"]).to_csv(outp, index=False)
    print(f"Saved details to {outp}")


if __name__ == "__main__":
    main()
