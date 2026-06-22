# Offline Monitoring and Drift Demo

`python -m src.evaluation.monitoring` computes prediction/confidence distributions, low-confidence/negative/question rates, topic counts, review lengths, and a total-variation drift proxy against the Wisesight distribution.

[`reports/monitoring.md`](../reports/monitoring.md) uses synthetic fixtures only. No live data, persistence service, or production-monitoring claim is involved.
