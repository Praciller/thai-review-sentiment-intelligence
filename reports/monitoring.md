# Offline Monitoring and Drift Demo

This report uses synthetic sample reviews. It is not live production monitoring.

- Sample size: 10
- Low-confidence rate: 40.0%
- Negative rate: 40.0%
- Question rate: 10.0%
- Prediction-distribution drift proxy (total variation): 0.445
- Warning flags: prediction_distribution_drift, high_low_confidence_rate

## Prediction distribution

```json
{
  "positive": 0.4,
  "negative": 0.4,
  "neutral": 0.1,
  "question": 0.1
}
```

## Confidence distribution

```json
{
  "low": 4,
  "medium": 3,
  "high": 3
}
```

## Topic counts

```json
{
  "delivery": 4,
  "other": 2,
  "price": 2,
  "service": 1,
  "waiting_time": 1
}
```

## Review length

```json
{
  "min": 26,
  "median": 31.5,
  "p95": 43.0,
  "max": 43
}
```
