from src.evaluation.explanations import explain_prediction
from src.models.predict import DemoPredictor


def test_demo_explanation_is_deterministic_and_non_causal():
    result = DemoPredictor().predict(["อาหารอร่อยแต่ส่งช้ามาก"])[0]

    first = explain_prediction(result)
    second = explain_prediction(result)

    assert first == second
    assert first.explanation_mode == "keyword_demo"
    assert {"อร่อย", "ช้า"} <= set(first.evidence_terms)
    assert "ส่ง" in first.topic_terms
    assert "possible_mixed_sentiment" in first.reason_codes

    negative = DemoPredictor().predict(["บริการไม่ดี"])[0]
    assert "ดี" not in explain_prediction(negative).evidence_terms
