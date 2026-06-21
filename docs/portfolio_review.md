# Portfolio Review

## Reviewer Checklist

1. Run the commands in `docs/local_review.md`.
2. Inspect the ignored `reports/local_sentiment_report.md`.
3. Compare the synthetic rule evidence with the public-corpus baseline reports.
4. Review API validation in `tests/test_api.py` and privacy checks in
   `scripts/check_repo_guardrails.py`.
5. Optionally run the React dashboard with `MODEL_BACKEND=demo`.

## Evidence and Skills

- Reproducible Thai normalization and tokenization.
- Deterministic sentiment and explainable aspect extraction.
- Honest model comparison using macro F1 and per-class reports.
- FastAPI validation, batch inference, health reporting, and React analytics.
- Offline tests, generated evidence, CI, data licensing, and repository safety
  guardrails.

## Known Limitations

The synthetic suite is small and deliberately designed for behavior checks. The
rule predictor does not understand language. Public-corpus metrics do not predict
performance on private customer reviews. Sarcasm, negation, slang, and mixed
sentiment need human review. Authentication, persistence, and production
monitoring are outside the portfolio review path.
