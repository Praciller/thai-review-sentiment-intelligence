"""Offline confidence and drift-proxy monitoring from safe sample batches."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import median
from typing import Sequence

from src.models.predict import DemoPredictor, PredictionResult
from src.utils.constants import SENTIMENT_LABELS


REFERENCE_DISTRIBUTION = {
    "positive": 4778 / 26749,
    "negative": 6824 / 26749,
    "neutral": 14572 / 26749,
    "question": 575 / 26749,
}


@dataclass(frozen=True)
class MonitoringSummary:
    sample_size: int
    prediction_distribution: dict[str, float]
    confidence_distribution: dict[str, int]
    low_confidence_rate: float
    negative_rate: float
    question_rate: float
    topic_counts: dict[str, int]
    review_length: dict[str, float]
    drift_proxy: float
    warning_flags: tuple[str, ...]


def summarize_predictions(
    results: Sequence[PredictionResult],
    *,
    reference_distribution: dict[str, float] | None = None,
    confidence_threshold: float = 0.7,
) -> MonitoringSummary:
    if not results:
        raise ValueError("at least one prediction is required")
    total = len(results)
    label_counts = Counter(result.predicted_label for result in results)
    distribution = {
        label: label_counts[label] / total for label in SENTIMENT_LABELS
    }
    confidence_distribution = {
        "low": sum(result.confidence < confidence_threshold for result in results),
        "medium": sum(
            confidence_threshold <= result.confidence < 0.85
            for result in results
        ),
        "high": sum(result.confidence >= 0.85 for result in results),
    }
    lengths = sorted(len(result.text) for result in results)
    reference = reference_distribution or REFERENCE_DISTRIBUTION
    drift_proxy = 0.5 * sum(
        abs(distribution[label] - reference.get(label, 0.0))
        for label in SENTIMENT_LABELS
    )
    low_rate = confidence_distribution["low"] / total
    negative_rate = label_counts["negative"] / total
    question_rate = label_counts["question"] / total
    warnings = []
    if drift_proxy > 0.2:
        warnings.append("prediction_distribution_drift")
    if low_rate > 0.35:
        warnings.append("high_low_confidence_rate")
    if negative_rate > 0.4:
        warnings.append("high_negative_rate")
    if question_rate > 0.25:
        warnings.append("high_question_rate")
    return MonitoringSummary(
        sample_size=total,
        prediction_distribution=distribution,
        confidence_distribution=confidence_distribution,
        low_confidence_rate=low_rate,
        negative_rate=negative_rate,
        question_rate=question_rate,
        topic_counts=dict(
            sorted(Counter(result.topic for result in results).items())
        ),
        review_length={
            "min": lengths[0],
            "median": float(median(lengths)),
            "p95": float(
                lengths[min(len(lengths) - 1, int(len(lengths) * 0.95))]
            ),
            "max": lengths[-1],
        },
        drift_proxy=drift_proxy,
        warning_flags=tuple(warnings),
    )


def sample_summary() -> MonitoringSummary:
    fixtures = json.loads(
        Path("data/sample/synthetic_reviews.json").read_text(encoding="utf-8")
    )
    return summarize_predictions(
        DemoPredictor().predict([row["text"] for row in fixtures])
    )


def render_report(summary: MonitoringSummary) -> str:
    data = asdict(summary)
    lines = [
        "# Offline Monitoring and Drift Demo",
        "",
        "This report uses synthetic sample reviews. It is not live production "
        "monitoring.",
        "",
        f"- Sample size: {summary.sample_size}",
        f"- Low-confidence rate: {summary.low_confidence_rate:.1%}",
        f"- Negative rate: {summary.negative_rate:.1%}",
        f"- Question rate: {summary.question_rate:.1%}",
        "- Prediction-distribution drift proxy (total variation): "
        f"{summary.drift_proxy:.3f}",
        f"- Warning flags: {', '.join(summary.warning_flags) or 'none'}",
        "",
    ]
    sections = (
        ("Prediction distribution", "prediction_distribution"),
        ("Confidence distribution", "confidence_distribution"),
        ("Topic counts", "topic_counts"),
        ("Review length", "review_length"),
    )
    for heading, key in sections:
        lines.extend(
            [
                f"## {heading}",
                "",
                "```json",
                json.dumps(data[key], ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/monitoring.md"))
    args = parser.parse_args()
    summary = sample_summary()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(summary), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
