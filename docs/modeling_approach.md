# Modeling Approach

## Shared Evaluation

All models reuse `data/processed/split_manifest.csv`, generated with stratified
70/15/15 train, validation, and test partitions using seed 42.

Metrics:

- Accuracy
- Macro precision and recall
- Macro F1
- Weighted F1
- Confusion matrix

Macro F1 is the model-selection metric because the dataset is imbalanced.

## Baselines

1. Word unigram/bigram TF-IDF plus class-balanced Logistic Regression.
2. Word unigram/bigram TF-IDF plus class-balanced Linear SVM calibrated with
   three-fold cross-validation for probabilities.

The saved joblib bundle contains the complete vectorizer/classifier pipeline,
labels, seed, model name, and training timestamp.

## Transformer

Default checkpoint:

```text
airesearch/wangchanberta-base-att-spm-uncased
```

The Trainer path uses raw review text, dynamic padding, configurable batch size,
best-checkpoint loading by macro F1, and the shared split manifest.

Debug mode samples at most eight rows per label per split and forces one epoch:

```powershell
python -m src.models.train_transformer --debug --seed 42 --cpu
```

On June 6, 2026, the WangchanBERTa debug pipeline completed on CPU. Debug metrics
are not reported as benchmark results because the sample is intentionally tiny.

## Optional MLflow

Set:

```text
MLFLOW_ENABLED=true
MLFLOW_TRACKING_URI=http://localhost:5000
```

Baseline metrics and parameters are logged when MLflow is installed and enabled.
Training remains functional when MLflow is disabled.
