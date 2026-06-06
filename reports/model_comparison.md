# Model Comparison

| Model | Accuracy | Macro F1 | Weighted F1 | Notes |
|---|---:|---:|---:|---|
| logistic_regression | 0.6545 | 0.5731 | 0.6608 | TF-IDF baseline |
| linear_svm | 0.7116 | 0.5305 | 0.6909 | Strong calibrated baseline |

Best model by macro F1: **logistic_regression**.

All entries use the shared split manifest at `data/processed/split_manifest.csv`.
