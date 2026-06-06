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

The response includes the predicted label, confidence, probabilities for all four
classes, model name, and rule-based topic.

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

## Security

- Empty and whitespace-only text is rejected.
- Text and batch sizes are bounded.
- Full review text is not logged by application code.
- CORS accepts only comma-separated `FRONTEND_ORIGINS`.
- Wildcard CORS configuration is rejected.
