# Security and Privacy Guardrails

The offline default uses synthetic data and needs no secrets, paid service, GPU, hosted database, or private review data.

`python scripts/check_repo_guardrails.py` rejects environment files, secret-like values, PII-like sample data, model/checkpoint binaries, local databases, caches/build output, notebooks with outputs, local user paths in Markdown, and files above 5 MiB.

The API limits text, batch, and declared request-body sizes; uses explicit CORS origins; returns structured errors; and refuses missing model artifacts in production.
