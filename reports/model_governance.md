# Model Governance

- Selected production model: `logistic_regression`
- Selection metric: `macro_f1` (0.5731)
- Accuracy: 0.6545
- Human-review threshold: 0.70
- Low-confidence synthetic review count: 4

Macro F1 is the selection metric because each sentiment class contributes equally despite strong class imbalance. Accuracy favors the majority-heavy SVM, while macro F1 better exposes weak minority-class behavior.

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| positive | 0.4982 | 0.5635 | 0.5288 | 717 |
| negative | 0.6506 | 0.7791 | 0.7091 | 1023 |
| neutral | 0.7735 | 0.6284 | 0.6934 | 2185 |
| question | 0.2587 | 0.5977 | 0.3611 | 87 |

## Confusion matrix summary

2626/4012 correct; largest confusion is neutral → positive (348 reviews).

## Known failure modes

- sarcasm
- slang
- code-switching
- mixed sentiment
- question-like reviews

## Transformer status

WangchanBERTa debug mode is not a benchmark; no full benchmark is claimed.

These values describe the documented held-out Wisesight baseline and synthetic routing checks; they are not business accuracy claims.
