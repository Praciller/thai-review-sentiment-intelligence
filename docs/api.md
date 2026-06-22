# API

## Run

```powershell
uvicorn src.api.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs>

## Health

```http
GET /health
```

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_name": "logistic_regression",
  "runtime_mode": "development"
}
```

## Single Prediction

```http
POST /predict
Content-Type: application/json
```

```json
{
  "text": "อาหารอร่อยมาก บริการดี"
}
```

The response includes label probabilities, model/topic metadata, review route,
threshold, reason codes, evidence/topic terms, explanation mode, and the model
selection metric.

## Batch Prediction

```http
POST /predict-batch
Content-Type: application/json
```

```json
{
  "texts": [
    "อร่อยมาก",
    "รอนานเกินไป",
    "ร้านเปิดกี่โมง"
  ]
}
```

Batch requests preserve input order and accept 1-100 reviews. Each review is
limited to 2,000 trimmed Unicode characters.

## Governance Endpoints

```http
GET /model-info
GET /monitoring/sample
GET /governance
GET /explanations/sample
```

These return typed, local artifacts. Monitoring and explanation samples use the
repository's synthetic fixture batch; they do not query private or live data.

## Security

- Empty and whitespace-only text is rejected.
- Text and batch sizes are bounded.
- Declared request-body size is bounded.
- Validation and limit failures use structured error codes without echoing input.
- Full review text is not logged by application code.
- CORS accepts only comma-separated `FRONTEND_ORIGINS`.
- Wildcard CORS configuration is rejected.
