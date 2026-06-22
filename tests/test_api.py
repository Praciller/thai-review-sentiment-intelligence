from fastapi.testclient import TestClient

from src.api.main import create_app
from src.models.predict import PredictionResult
from src.utils.config import Settings


class FakePredictor:
    model_name = "fake-model"

    def predict(self, texts):
        return [
            PredictionResult(
                text=text,
                predicted_label="positive",
                confidence=0.7,
                probabilities={
                    "positive": 0.7,
                    "negative": 0.1,
                    "neutral": 0.1,
                    "question": 0.1,
                },
                model_name=self.model_name,
                topic="service",
                topic_method="rule_based",
            )
            for text in texts
        ]


def make_client(*, frontend_dist_path=None, max_request_bytes=250_000):
    load_count = {"value": 0}

    def predictor_factory():
        load_count["value"] += 1
        return FakePredictor()

    settings = Settings(
        app_env="test",
        frontend_origins="http://localhost:5173",
        frontend_dist_path=frontend_dist_path or "frontend/dist",
        max_text_length=20,
        max_batch_size=3,
        max_request_bytes=max_request_bytes,
    )
    app = create_app(settings=settings, predictor_factory=predictor_factory)
    return TestClient(app), load_count


def test_health_endpoint_loads_model_once_for_application_lifespan():
    client, load_count = make_client()

    with client:
        first = client.get("/health")
        second = client.get("/health")

    assert first.status_code == 200
    assert first.json() == {
        "status": "ok",
        "model_loaded": True,
        "model_name": "fake-model",
        "runtime_mode": "test",
    }
    assert second.status_code == 200
    assert load_count["value"] == 1


def test_predict_returns_required_response_structure():
    client, _ = make_client()

    with client:
        response = client.post("/predict", json={"text": "บริการดีมาก"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["text"] == "บริการดีมาก"
    assert payload["predicted_label"] == "positive"
    assert payload["confidence"] == 0.7
    assert set(payload["probabilities"]) == {
        "positive",
        "negative",
        "neutral",
        "question",
    }
    assert payload["model_name"] == "fake-model"
    assert payload["selected_production_model"] == "logistic_regression"
    assert payload["topic_method"] == "rule_based"
    assert payload["route"] == "auto_label"
    assert payload["confidence_threshold"] == 0.7
    assert payload["explanation_mode"] == "keyword_demo"
    assert payload["selection_metric"] == "macro_f1"


def test_predict_rejects_empty_or_oversized_text():
    client, _ = make_client()

    with client:
        empty = client.post("/predict", json={"text": "   "})
        oversized = client.post("/predict", json={"text": "ก" * 21})

    assert empty.status_code == 422
    assert oversized.status_code == 422
    assert empty.json()["error"]["code"] == "validation_error"
    assert oversized.json()["error"]["code"] == "text_too_long"


def test_predict_rejects_oversized_request_body():
    client, _ = make_client(max_request_bytes=10)

    with client:
        response = client.post("/predict", json={"text": "บริการดี"})

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "request_too_large"


def test_predict_batch_preserves_input_order_and_enforces_limit():
    client, _ = make_client()

    with client:
        response = client.post(
            "/predict-batch",
            json={"texts": ["รีวิวหนึ่ง", "รีวิวสอง"]},
        )
        oversized = client.post(
            "/predict-batch",
            json={"texts": ["หนึ่ง", "สอง", "สาม", "สี่"]},
        )

    assert response.status_code == 200
    assert [item["text"] for item in response.json()["results"]] == [
        "รีวิวหนึ่ง",
        "รีวิวสอง",
    ]
    assert oversized.status_code == 422
    assert oversized.json()["error"]["code"] == "batch_too_large"


def test_governance_monitoring_model_info_and_explanation_endpoints():
    client, _ = make_client()

    with client:
        model_info = client.get("/model-info")
        monitoring = client.get("/monitoring/sample")
        governance = client.get("/governance")
        explanations = client.get("/explanations/sample")

    assert model_info.status_code == 200
    assert model_info.json()["selection_metric"] == "macro_f1"
    assert model_info.json()["runtime_model_name"] == "fake-model"
    assert monitoring.status_code == 200
    assert monitoring.json()["sample_size"] == 10
    assert governance.status_code == 200
    assert governance.json()["selected_production_model"] == "logistic_regression"
    assert explanations.status_code == 200
    assert explanations.json()["results"][0]["explanation_mode"] == "keyword_demo"


def test_cors_allows_only_configured_frontend_origin():
    client, _ = make_client()

    with client:
        allowed = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        denied = client.options(
            "/predict",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert (
        allowed.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )
    assert "access-control-allow-origin" not in denied.headers


def test_serves_built_frontend_without_shadowing_api_routes(tmp_path):
    dist_path = tmp_path / "dist"
    assets_path = dist_path / "assets"
    assets_path.mkdir(parents=True)
    (dist_path / "index.html").write_text(
        "<html><body>Thai Review Intelligence</body></html>",
        encoding="utf-8",
    )
    (assets_path / "app.js").write_text(
        "console.log('ready')",
        encoding="utf-8",
    )
    client, _ = make_client(frontend_dist_path=dist_path)

    with client:
        home = client.get("/")
        spa_route = client.get("/batch")
        asset = client.get("/assets/app.js")
        health = client.get("/health")

    assert home.status_code == 200
    assert "Thai Review Intelligence" in home.text
    assert spa_route.status_code == 200
    assert "Thai Review Intelligence" in spa_route.text
    assert asset.status_code == 200
    assert asset.text == "console.log('ready')"
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
