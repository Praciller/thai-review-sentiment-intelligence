# Thai Review Sentiment Intelligence Design

## Goal

Build a free-tier-friendly, end-to-end Thai sentiment intelligence portfolio
project: reproducible data pipeline, baseline and Transformer training, common
evaluation, FastAPI inference, and a production React dashboard.

## Scope Decisions

- Wisesight Sentiment Corpus is the only required dataset.
- The loader inspects the installed PyThaiNLP API first. If the historical
  `wisesight_sentiment` accessor is unavailable, it downloads the same official
  PyThaiNLP Wisesight repository files and records the resolved source.
- Canonical labels are `positive`, `negative`, `neutral`, and `question`; raw
  aliases such as `pos`, `neg`, `neu`, and `q` are normalized at the data boundary.
- One deterministic split manifest is written and reused by all model families.
- Baseline model is the default API runtime because it is fast and CPU-friendly.
  A local Transformer checkpoint is selected automatically when configured.
- Topic detection remains explicitly rule-based and optional.
- MLflow integration is opt-in. Training succeeds when MLflow is absent or disabled.
- No large datasets or model artifacts are committed.

## Architecture

```text
PyThaiNLP/official corpus
        |
        v
load -> validate -> preprocess -> split manifest
        |                         |
        v                         +-> TF-IDF baselines
       EDA                        +-> WangchanBERTa Trainer
                                      |
                                      v
                             shared evaluation artifacts
                                      |
                                      v
                        model registry -> FastAPI -> React
```

Python modules expose reusable functions and thin CLI entry points. The API owns
inference only. Frontend API access is isolated in `frontend/src/services`.

## Data Contracts

Processed CSV columns:

```text
text,label,cleaned_text,text_length
```

Split manifest columns:

```text
row_id,split
```

Prediction response:

```json
{
  "text": "อาหารอร่อยมาก บริการดี",
  "predicted_label": "positive",
  "confidence": 0.94,
  "probabilities": {
    "positive": 0.94,
    "negative": 0.01,
    "neutral": 0.04,
    "question": 0.01
  },
  "model_name": "baseline-linear-svm",
  "topic": "taste",
  "topic_method": "rule_based"
}
```

## API Behavior

- `GET /health` never requires a loaded model.
- `POST /predict` accepts trimmed text from 1 to 2,000 characters.
- `POST /predict-batch` accepts 1 to 100 texts and returns ordered results.
- Model loads once through FastAPI lifespan.
- CORS origins come from `FRONTEND_ORIGINS`; wildcard origins are rejected.
- In development, missing model artifacts use an explicit deterministic demo
  predictor so the UI and API contract remain runnable. Health exposes runtime mode.

## Frontend Design

Primary routes:

1. Prediction: review input, examples, result, confidence, probabilities.
2. Batch: CSV upload, validation, preview, prediction, table, sentiment filter.
3. Dashboard: distribution, counts, average confidence, issue summary, negative rows.

Visual contract is defined in `PRODUCT.md`, `DESIGN.md`, and
`docs/design/dashboard-concept.png`. The app uses a light task-first layout with
open data bands, a restrained palette, and no decorative AI imagery.

## Testing

- Unit tests cover text normalization, repeated-character handling, tokenization,
  label normalization, and topic rules.
- Data tests cover validation cleanup and report output.
- Model tests cover deterministic splitting and metric schema using small fixtures.
- API tests inject a fake predictor and verify health, input limits, response shape,
  batch order, and CORS configuration.
- Frontend tests cover CSV parsing and dashboard aggregation.
- Browser verification covers desktop/mobile prediction, CSV batch flow, navigation,
  errors, focus visibility, and console errors.

## Success Criteria

All required CLI modules import and expose `--help`; Python tests pass; frontend
typecheck/build/tests pass; API smoke requests pass; generated docs and sample CSV
exist; Docker files parse; browser workflow completes against a local API.
