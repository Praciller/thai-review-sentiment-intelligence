"""Deterministic local review-queue selection for synthetic/sample data."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from src.features.preprocess_thai_text import TOPIC_KEYWORDS, clean_text
from src.models.predict import DemoPredictor, PredictionResult
from src.models.review_routing import route_prediction


@dataclass(frozen=True)
class ReviewQueueItem:
    text: str
    predicted_label: str
    confidence: float
    priority_score: float
    reason_codes: tuple[str, ...]


def select_review_queue(
    results: Sequence[PredictionResult],
    *,
    limit: int = 20,
    confidence_threshold: float = 0.7,
) -> list[ReviewQueueItem]:
    if limit < 1:
        raise ValueError("limit must be positive")
    queue = []
    for result in results:
        routing = route_prediction(result.text, result.predicted_label, result.confidence, confidence_threshold=confidence_threshold)
        reasons = list(routing.reason_codes)
        topics = _matched_topics(result.text)
        score = 0.0
        score += max(0.0, confidence_threshold - result.confidence) * 10
        score += 2.0 if result.predicted_label == "negative" else 0.0
        score += 2.5 if result.predicted_label == "question" else 0.0
        score += 2.0 if "possible_mixed_sentiment" in reasons else 0.0
        if len(result.text) >= 120:
            score += 1.0
            reasons.append("long_multi_aspect_review")
        if len(topics) > 1:
            score += 1.0
            reasons.append("multiple_aspects")
        if result.predicted_label == "question":
            score += 1.0
            reasons.append("rare_class_candidate")
        if score:
            queue.append(ReviewQueueItem(result.text, result.predicted_label, result.confidence, round(score, 3), tuple(dict.fromkeys(reasons))))
    return sorted(queue, key=lambda item: (-item.priority_score, item.text))[:limit]


def _matched_topics(text: str) -> list[str]:
    cleaned = clean_text(text)
    return [topic for topic, terms in TOPIC_KEYWORDS.items() if any(term in cleaned for term in terms)]


def render_report() -> str:
    fixtures = json.loads(Path("data/sample/synthetic_reviews.json").read_text(encoding="utf-8"))
    queue = select_review_queue(DemoPredictor().predict([row["text"] for row in fixtures]))
    lines = [
        "# Synthetic Active-Learning Review Queue",
        "",
        "This deterministic queue uses only repository sample data; it does not persist private reviews.",
        "",
        "| Rank | Label | Confidence | Priority | Reason codes | Synthetic review |",
        "|---:|---|---:|---:|---|---|",
    ]
    for rank, item in enumerate(queue, 1):
        safe_text = item.text.replace("|", "\\|")
        lines.append(f"| {rank} | {item.predicted_label} | {item.confidence:.3f} | {item.priority_score:.3f} | {', '.join(item.reason_codes)} | {safe_text} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/active_learning_queue.md"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
