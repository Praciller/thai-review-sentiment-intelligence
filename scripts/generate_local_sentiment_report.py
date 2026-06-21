"""Generate deterministic offline evidence from synthetic Thai reviews."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.preprocess_thai_text import (
    TOPIC_KEYWORDS,
    clean_text,
    tokenize_thai_text,
)
from src.models.predict import DemoPredictor

DEFAULT_FIXTURES = Path("data/sample/synthetic_reviews.json")
DEFAULT_OUTPUT = Path("reports/local_sentiment_report.md")


def load_fixtures(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("fixture file must contain at least one fixture")
    required = {"id", "category", "text", "expected_label"}
    if any(not isinstance(row, dict) or not required <= row.keys() for row in rows):
        raise ValueError(f"each fixture must contain: {', '.join(sorted(required))}")
    return rows


def build_report(fixtures: list[dict[str, str]]) -> list[dict[str, Any]]:
    predictions = DemoPredictor().predict([row["text"] for row in fixtures])
    evidence = []
    for row, prediction in zip(fixtures, predictions, strict=True):
        normalized = clean_text(row["text"])
        keywords = [
            keyword
            for values in TOPIC_KEYWORDS.values()
            for keyword in values
            if keyword in normalized
        ]
        evidence.append(
            {
                **row,
                "normalized_text": normalized,
                "tokens": tokenize_thai_text(normalized),
                "keywords": keywords,
                "prediction": prediction,
            }
        )
    return evidence


def render_markdown(evidence: list[dict[str, Any]]) -> str:
    correct = sum(
        row["expected_label"] == row["prediction"].predicted_label
        for row in evidence
    )
    lines = [
        "# Local Thai Sentiment Evidence",
        "",
        "This report uses deterministic synthetic fixtures. No external AI, network, "
        "hosted database, or private customer data was used.",
        "",
        "The rule-based output is demo evidence, not a production model or a basis for "
        "automated business decisions. Human review is required.",
        "",
        f"Fixture agreement: **{correct}/{len(evidence)}**. This is a behavior check on "
        "synthetic examples, not a general accuracy estimate.",
        "",
    ]
    for row in evidence:
        prediction = row["prediction"]
        keywords = ", ".join(row["keywords"]) or "none"
        lines.extend(
            [
                f"## {row['id']}: {row['category']}",
                "",
                f"- Input: {row['text']}",
                f"- Normalized: {row['normalized_text']}",
                f"- Tokens: {' | '.join(row['tokens'])}",
                f"- Expected / predicted: {row['expected_label']} / {prediction.predicted_label}",
                f"- Confidence: {prediction.confidence:.4f}",
                f"- Aspect: {prediction.topic} (`rule_based`)",
                f"- Matched aspect terms: {keywords}",
                "",
            ]
        )
    lines.extend(
        [
            "## Limitations",
            "",
            "Keyword scores cannot reliably interpret Thai negation, sarcasm, emerging "
            "slang, or mixed sentiment. Confidence is a normalized rule score, not a "
            "calibrated probability. See `docs/model_methodology.md` for the trained "
            "baseline evaluation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = build_report(load_fixtures(args.fixtures))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(evidence), encoding="utf-8")
    print(f"wrote {args.output} ({len(evidence)} synthetic fixtures, offline)")


if __name__ == "__main__":
    main()
