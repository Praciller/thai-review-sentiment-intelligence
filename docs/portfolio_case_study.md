# Portfolio Case Study

## Problem

Thai review classification must expose uncertainty and operational consequences, not only a label.

## Engineering approach

The project preserves the evaluated Logistic Regression artifact and adds macro-F1 governance, confidence routing, lightweight evidence, offline drift summaries, and a synthetic review queue. FastAPI publishes typed contracts and React exposes review/escalation state.

## Verification boundary

CI runs without GPU, secrets, private data, paid services, or full Transformer training. Held-out metrics describe Wisesight only; synthetic fixtures verify behavior, not business accuracy. Live monitoring, authentication, persistence, and a full WangchanBERTa benchmark remain future work.
