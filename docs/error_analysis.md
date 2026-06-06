# Error Analysis

Run:

```powershell
python -m src.evaluation.error_analysis
```

Outputs:

- `reports/error_analysis.csv`: misclassified test examples.
- `reports/error_analysis.md`: confused pairs, length buckets, hard cases, and
  practical hypotheses.

## Current Baseline Observations

The selected Logistic Regression baseline made 1,378 errors across 4,017 test
reviews, an error rate of 34.3%.

Expected difficult cases include:

- Short messages with little lexical evidence.
- Question and neutral overlap.
- Mixed sentiment forced into one label.
- Thai slang, creative spelling, and sarcasm.
- Reviews whose meaning depends on an image or conversation context.

These are hypotheses grounded in the error categories, not causal claims about
individual examples.
