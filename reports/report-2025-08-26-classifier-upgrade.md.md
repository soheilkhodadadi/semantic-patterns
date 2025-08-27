

# Report: Classifier Upgrade Evaluation
filename: `report-2025-08-26-classifier-upgrade.md`*

## What changed
Upgraded the semantic classifier model to incorporate additional training data from July and improved feature extraction. This included:
- Expanded labeled dataset (+15%)
- Refactored the feature pipeline for efficiency
- Adjusted hyperparameters for better generalization

## Code integration
The new model and pipeline are integrated in the `classifier_v2` branch. Key files:
- `src/classifier/train.py`
- `src/classifier/model_v2.pkl`

To test locally, switch to the branch and run:
```bash
git checkout classifier_v2
python src/classifier/train.py --config configs/v2.yaml
```

## How to reproduce
1. Clone the repository and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run training:
   ```bash
   python src/classifier/train.py --config configs/v2.yaml
   ```
3. Evaluate:
   ```bash
   python src/classifier/evaluate.py --model model_v2.pkl
   ```

## Results
- Validation accuracy: **83.87%**
- F1 score: **0.812**
- Baseline accuracy (previous model): **80.12%**
- Training time: 12m 30s (vs. 14m previously)

## Why not merging
- Requires further testing on edge cases (see Attachment 1)
- Some performance regressions on rare classes
- Awaiting feedback from product team regarding new feature extraction

## Attachments
- Confusion matrix: `attachments/confusion_matrix_v2.png`
- Error analysis: `attachments/error_analysis_aug26.xlsx`
- Full logs: `attachments/logs_aug26.txt`

## Next steps
- Address rare class performance issues
- Solicit feedback from product team (deadline: Sept 1)
- Plan A/B test in staging environment
