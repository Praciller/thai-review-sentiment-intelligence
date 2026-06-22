# Explainability

Responses expose `evidence_terms`, `topic_terms`, `reason_codes`, and `explanation_mode`. `tfidf_weights` ranks review terms using compatible artifact coefficients; `keyword_demo` is the deterministic fallback.

Run `python -m src.evaluation.explanations` to rebuild [`reports/explanations.md`](../reports/explanations.md). These are approximate model/debug aids, not causal explanations.
