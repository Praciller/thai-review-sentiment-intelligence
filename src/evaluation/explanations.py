"""Lightweight, approximate evidence for prediction debugging."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.features.preprocess_thai_text import TOPIC_KEYWORDS, clean_text, preprocess_for_baseline
from src.models.predict import DemoPredictor, PredictionResult
from src.models.review_routing import NEGATIVE_TERMS, POSITIVE_TERMS, QUESTION_TERMS, match_terms, route_prediction


@dataclass(frozen=True)
class ExplanationMetadata:
    evidence_terms: tuple[str, ...]
    topic_terms: tuple[str, ...]
    reason_codes: tuple[str, ...]
    explanation_mode: str


def explain_prediction(
    result: PredictionResult,
    *,
    pipeline: Any | None = None,
    confidence_threshold: float = 0.7,
) -> ExplanationMetadata:
    cleaned = clean_text(result.text)
    topic_terms = tuple(
        keyword
        for keyword in TOPIC_KEYWORDS.get(result.topic, ())
        if keyword.lower() in cleaned.lower()
    )
    evidence_terms = _model_evidence(result, pipeline) if pipeline is not None else ()
    mode = "tfidf_weights" if evidence_terms else "keyword_demo"
    if not evidence_terms:
        candidates = POSITIVE_TERMS + NEGATIVE_TERMS + QUESTION_TERMS
        evidence_terms = tuple(dict.fromkeys(match_terms(cleaned, candidates)))
    routing = route_prediction(
        result.text,
        result.predicted_label,
        result.confidence,
        confidence_threshold=confidence_threshold,
    )
    return ExplanationMetadata(
        evidence_terms=evidence_terms[:8],
        topic_terms=topic_terms,
        reason_codes=routing.reason_codes,
        explanation_mode=mode,
    )


def top_weighted_terms(pipeline: Any, *, limit: int = 8) -> dict[str, dict[str, list[str]]]:
    """Return global TF-IDF coefficient extremes when the artifact exposes them."""
    vectorizer = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]
    features = np.asarray(vectorizer.get_feature_names_out())
    return {
        str(label): {
            "positive": features[np.argsort(weights)[-limit:][::-1]].tolist(),
            "negative": features[np.argsort(weights)[:limit]].tolist(),
        }
        for label, weights in zip(classifier.classes_, classifier.coef_, strict=True)
    }


def _model_evidence(result: PredictionResult, pipeline: Any) -> tuple[str, ...]:
    try:
        vectorizer = pipeline.named_steps["tfidf"]
        classifier = pipeline.named_steps["classifier"]
        row = vectorizer.transform([preprocess_for_baseline(result.text)])
        class_index = list(classifier.classes_).index(result.predicted_label)
        contributions = row.multiply(classifier.coef_[class_index]).toarray()[0]
        features = np.asarray(vectorizer.get_feature_names_out())
        indices = np.flatnonzero(contributions)
        ordered = indices[np.argsort(np.abs(contributions[indices]))[::-1]]
        return tuple(features[ordered[:8]].tolist())
    except (AttributeError, KeyError, ValueError, IndexError):
        return ()


def render_report() -> str:
    fixtures = json.loads(Path("data/sample/synthetic_reviews.json").read_text(encoding="utf-8"))
    predictions = DemoPredictor().predict([row["text"] for row in fixtures])
    lines = [
        "# Explanation Evidence",
        "",
        "These explanations are approximate model/debug aids, not causal explanations.",
        "",
    ]
    for row, result in zip(fixtures, predictions, strict=True):
        metadata = explain_prediction(result)
        lines.extend([
            f"## {row['id']}",
            "",
            f"- Mode: `{metadata.explanation_mode}`",
            f"- Evidence terms: {', '.join(metadata.evidence_terms) or 'none'}",
            f"- Topic terms: {', '.join(metadata.topic_terms) or 'none'}",
            f"- Reason codes: {', '.join(metadata.reason_codes) or 'none'}",
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/explanations.md"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
