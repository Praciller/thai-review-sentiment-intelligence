from src.models.review_routing import route_prediction


def test_routes_predictions_by_operational_risk():
    question = route_prediction("ส่งวันอาทิตย์ไหม?", "question", 0.91)
    negative = route_prediction("ส่งช้ามาก ราคาแพง", "negative", 0.88)
    uncertain = route_prediction("อาหารโอเค", "neutral", 0.52)
    positive = route_prediction("อาหารอร่อยมาก", "positive", 0.93)

    assert question.route == "support_workflow"
    assert "question_intent" in question.reason_codes
    assert negative.route == "escalation_queue"
    assert {"negative_sentiment", "contains_delivery_issue", "contains_price_issue"} <= set(negative.reason_codes)
    assert uncertain.route == "human_review"
    assert "low_confidence" in uncertain.reason_codes
    assert positive.route == "auto_label"
    assert positive.confidence_threshold == 0.7


def test_mixed_sentiment_requires_human_review_even_when_confident():
    decision = route_prediction(
        "อาหารอร่อยแต่ส่งช้ามาก",
        "negative",
        0.92,
    )

    assert decision.route == "human_review"
    assert "possible_mixed_sentiment" in decision.reason_codes


def test_thai_negation_does_not_create_false_positive_evidence():
    decision = route_prediction("ส่งช้ามาก บริการไม่ดี", "negative", 0.9)

    assert decision.route == "escalation_queue"
    assert "possible_mixed_sentiment" not in decision.reason_codes
