"""Stable model-selection and evaluation-governance reporting."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from src.models.predict import DemoPredictor


METRICS_PATH = Path("reports/baseline_metrics.json")
FIXTURES_PATH = Path("data/sample/synthetic_reviews.json")
FAILURE_MODES = ("sarcasm", "slang", "code-switching", "mixed sentiment", "question-like reviews")


@dataclass(frozen=True)
class GovernanceSummary:
    selected_production_model: str
    selection_metric: str
    accuracy: float
    macro_f1: float
    per_class_metrics: dict[str, dict[str, float]]
    confusion_matrix_summary: str
    low_confidence_review_count: int
    human_review_threshold: float
    known_failure_modes: tuple[str, ...]
    wangchanberta_status: str


def build_governance_summary(
    *,
    metrics_path: Path = METRICS_PATH,
    confidence_threshold: float = 0.7,
) -> GovernanceSummary:
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    selected = payload["best_model"]
    metrics = payload["models"][selected]
    labels = metrics["labels"]
    matrix = metrics["confusion_matrix"]
    fixtures = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
    demo_results = DemoPredictor().predict([row["text"] for row in fixtures])
    return GovernanceSummary(
        selected_production_model=selected,
        selection_metric="macro_f1",
        accuracy=float(metrics["accuracy"]),
        macro_f1=float(metrics["macro_f1"]),
        per_class_metrics=_per_class_metrics(labels, matrix),
        confusion_matrix_summary=_confusion_summary(labels, matrix),
        low_confidence_review_count=sum(result.confidence < confidence_threshold for result in demo_results),
        human_review_threshold=confidence_threshold,
        known_failure_modes=FAILURE_MODES,
        wangchanberta_status="WangchanBERTa debug mode is not a benchmark; no full benchmark is claimed.",
    )


def _per_class_metrics(labels: list[str], matrix: list[list[int]]) -> dict[str, dict[str, float]]:
    metrics = {}
    for index, label in enumerate(labels):
        true_positive = matrix[index][index]
        predicted = sum(row[index] for row in matrix)
        actual = sum(matrix[index])
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / actual if actual else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        metrics[label] = {"precision": precision, "recall": recall, "f1": f1, "support": actual}
    return metrics


def _confusion_summary(labels: list[str], matrix: list[list[int]]) -> str:
    mistakes = [
        (matrix[actual][predicted], labels[actual], labels[predicted])
        for actual in range(len(labels))
        for predicted in range(len(labels))
        if actual != predicted
    ]
    count, actual, predicted = max(mistakes)
    correct = sum(matrix[index][index] for index in range(len(labels)))
    total = sum(sum(row) for row in matrix)
    return f"{correct}/{total} correct; largest confusion is {actual} → {predicted} ({count} reviews)."


def render_report(summary: GovernanceSummary) -> str:
    lines = [
        "# Model Governance",
        "",
        f"- Selected production model: `{summary.selected_production_model}`",
        f"- Selection metric: `{summary.selection_metric}` ({summary.macro_f1:.4f})",
        f"- Accuracy: {summary.accuracy:.4f}",
        f"- Human-review threshold: {summary.human_review_threshold:.2f}",
        f"- Low-confidence synthetic review count: {summary.low_confidence_review_count}",
        "",
        "Macro F1 is the selection metric because each sentiment class contributes equally despite strong class imbalance. Accuracy favors the majority-heavy SVM, while macro F1 better exposes weak minority-class behavior.",
        "",
        "## Per-class metrics",
        "",
        "| Class | Precision | Recall | F1 | Support |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, values in summary.per_class_metrics.items():
        lines.append(f"| {label} | {values['precision']:.4f} | {values['recall']:.4f} | {values['f1']:.4f} | {values['support']} |")
    lines.extend([
        "",
        "## Confusion matrix summary",
        "",
        summary.confusion_matrix_summary,
        "",
        "## Known failure modes",
        "",
        *(f"- {item}" for item in summary.known_failure_modes),
        "",
        "## Transformer status",
        "",
        summary.wangchanberta_status,
        "",
        "These values describe the documented held-out Wisesight baseline and synthetic routing checks; they are not business accuracy claims.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/model_governance.md"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(build_governance_summary()), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
