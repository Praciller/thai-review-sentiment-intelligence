# Model Comparison

| Model | Accuracy | Macro F1 | Weighted F1 | Notes |
|---|---:|---:|---:|---|
| logistic_regression | 0.6565 | 0.5703 | 0.6627 | TF-IDF baseline |
| linear_svm | 0.7044 | 0.5082 | 0.6788 | Strong calibrated baseline |

Best model by macro F1: **logistic_regression**.

All entries use the shared split manifest at `data/processed/split_manifest.csv`.
