# Model Governance

The production artifact remains TF-IDF + Logistic Regression. Selection uses macro F1 because Wisesight is class-imbalanced and each label must contribute equally. Accuracy is secondary; it favors the majority-heavy Linear SVM despite weaker minority-class balance.

`python -m src.evaluation.model_governance` rebuilds [`reports/model_governance.md`](../reports/model_governance.md) from checked-in held-out metrics and synthetic routing fixtures. WangchanBERTa debug mode validates the training path only; it is not a benchmark.
