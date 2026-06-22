from src.evaluation.active_learning import select_review_queue
from src.models.predict import PredictionResult


def prediction(text, label, confidence, topic="other"):
    return PredictionResult(text, label, confidence, {}, "test", topic)


def test_queue_prioritizes_uncertain_negative_and_question_reviews():
    results = [
        prediction("ดีมาก", "positive", 0.95),
        prediction("ส่งช้ามาก ราคาแพง", "negative", 0.45, "delivery"),
        prediction("เปิดกี่โมง?", "question", 0.82),
    ]

    queue = select_review_queue(results, limit=2)

    assert queue[0].text == "ส่งช้ามาก ราคาแพง"
    assert "low_confidence" in queue[0].reason_codes
    assert queue[1].predicted_label == "question"
    assert all(item.text != "ดีมาก" for item in queue)
