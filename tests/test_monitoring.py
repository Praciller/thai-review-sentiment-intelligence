from src.evaluation.monitoring import summarize_predictions
from src.models.predict import DemoPredictor


def test_monitoring_summary_covers_distribution_drift_and_warnings():
    results = DemoPredictor().predict([
        "ดีมาก",
        "ส่งช้ามาก",
        "ราคาเท่าไหร่?",
        "ข้อมูลทั่วไป",
    ])

    summary = summarize_predictions(
        results,
        reference_distribution={"positive": 1.0, "negative": 0.0, "neutral": 0.0, "question": 0.0},
    )

    assert sum(summary.prediction_distribution.values()) == 1.0
    assert summary.question_rate == 0.25
    assert summary.topic_counts["delivery"] == 1
    assert summary.review_length["max"] >= summary.review_length["median"]
    assert summary.drift_proxy > 0
    assert "prediction_distribution_drift" in summary.warning_flags
