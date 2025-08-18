import sys
import os
import pandas as pd

# Add src/ to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classify import classify_sentence

# Load held-out validation file
df = pd.read_csv("data/validation/held_out_sentences.csv")

# Evaluate predictions
correct = 0
results = []

for idx, row in df.iterrows():
    sent = row["sentence"]
    true = row["label"]
    pred, scores = classify_sentence(sent)
    match = pred == true
    results.append((sent, true, pred, match, scores))
    print(f"\n📝 {sent}\n✅ True: {true} | 🔮 Predicted: {pred} | {'✔️' if match else '❌'}")
    print(f"📊 Scores: {scores}")
    if match:
        correct += 1

# Print final accuracy
total = len(df)
print(f"\n🎯 Accuracy: {correct} / {total} = {correct/total:.2%}")

# Save results to CSV
pd.DataFrame(results, columns=["sentence", "true_label", "predicted_label", "match", "scores"])\
  .to_csv("data/validation/evaluation_results.csv", index=False)
