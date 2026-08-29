"""Evaluate the frozen manually authored Thai robustness challenge set."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.data.dataset_paths import DIAGNOSTIC_CHALLENGE_DATASET_PATH
from src.evaluation.metrics import compute_classification_metrics
from src.models.predict import (
    BaselinePredictor,
    DemoPredictor,
    PredictionResult,
    Predictor,
)
from src.models.review_routing import RoutingDecision, route_prediction
from src.utils.constants import SENTIMENT_LABELS

CHALLENGE_DATASET_PATH = DIAGNOSTIC_CHALLENGE_DATASET_PATH
DEFAULT_REPORT_PATH = Path("reports/robustness_challenge.md")
DEFAULT_BASELINE_MODEL_PATH = Path("models/baseline_model.joblib")
DEFAULT_REVIEW_THRESHOLD = 0.55
REQUIRED_FIELDS = frozenset(
    {"id", "text", "expected_label", "slice", "rationale"}
)
ALLOWED_SLICES = (
    "negation",
    "code_switching",
    "conversational_slang",
    "emoji_punctuation",
    "question_like",
    "mixed_sentiment",
    "length_contrast",
    "spelling_variation",
    "defensible_sarcasm",
)


@dataclass(frozen=True)
class ChallengeExample:
    id: str
    text: str
    expected_label: str
    slice: str
    rationale: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "text": self.text,
            "expected_label": self.expected_label,
            "slice": self.slice,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class ChallengeEvaluationRow:
    example: ChallengeExample
    prediction: PredictionResult
    routing: RoutingDecision

    @property
    def is_correct(self) -> bool:
        return self.example.expected_label == self.prediction.predicted_label


@dataclass(frozen=True)
class ChallengeEvaluation:
    predictor_name: str
    model_version: str
    review_threshold: float
    metrics: dict[str, Any]
    per_slice: dict[str, dict[str, Any]]
    rows: tuple[ChallengeEvaluationRow, ...]
    route_counts: dict[str, int]
    low_confidence_count: int


def load_challenge_dataset(
    path: Path = CHALLENGE_DATASET_PATH,
) -> list[ChallengeExample]:
    """Load and validate the strict, human-reviewable challenge schema."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError(f"challenge dataset is invalid JSON: {path}") from exc

    if not isinstance(payload, list) or not payload:
        raise ValueError("challenge dataset must be a non-empty JSON list")

    examples: list[ChallengeExample] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(payload):
        if not isinstance(raw, dict) or set(raw) != REQUIRED_FIELDS:
            raise ValueError(
                f"challenge row {index} must contain exactly "
                f"{sorted(REQUIRED_FIELDS)}"
            )
        if not all(isinstance(value, str) for value in raw.values()):
            raise ValueError(f"challenge row {index} fields must all be strings")

        example = ChallengeExample(**raw)
        if not example.id.strip():
            raise ValueError(f"challenge row {index} has an empty id")
        if example.id in seen_ids:
            raise ValueError(f"duplicate id in challenge dataset: {example.id}")
        seen_ids.add(example.id)
        if not example.text.strip() or not example.rationale.strip():
            raise ValueError(
                f"challenge row {index} requires non-empty text and rationale"
            )
        if example.expected_label not in SENTIMENT_LABELS:
            raise ValueError(
                f"challenge row {index} has unsupported label: "
                f"{example.expected_label}"
            )
        if example.slice not in ALLOWED_SLICES:
            raise ValueError(
                f"challenge row {index} has unsupported slice: {example.slice}"
            )
        examples.append(example)
    return examples


def evaluate_predictor(
    predictor: Predictor,
    examples: list[ChallengeExample],
    *,
    review_threshold: float,
) -> ChallengeEvaluation:
    """Run one predictor over the frozen examples without fitting anything."""
    predictions = predictor.predict([example.text for example in examples])
    if len(predictions) != len(examples):
        raise ValueError("predictor returned a different number of rows")

    rows: list[ChallengeEvaluationRow] = []
    for example, prediction in zip(examples, predictions, strict=True):
        if prediction.predicted_label not in SENTIMENT_LABELS:
            raise ValueError(
                f"predictor returned unsupported label: {prediction.predicted_label}"
            )
        routing = _route_prediction(
            example.text,
            prediction,
            review_threshold,
        )
        rows.append(
            ChallengeEvaluationRow(
                example=example,
                prediction=prediction,
                routing=routing,
            )
        )

    expected = [row.example.expected_label for row in rows]
    predicted = [row.prediction.predicted_label for row in rows]
    per_slice: dict[str, dict[str, Any]] = {}
    label_order = {label: index for index, label in enumerate(SENTIMENT_LABELS)}
    for slice_name in ALLOWED_SLICES:
        slice_rows = [row for row in rows if row.example.slice == slice_name]
        if not slice_rows:
            continue
        slice_expected = [row.example.expected_label for row in slice_rows]
        slice_predicted = [row.prediction.predicted_label for row in slice_rows]
        present_labels = sorted(
            set(slice_expected), key=lambda label: label_order[label]
        )
        metrics = compute_classification_metrics(
            slice_expected,
            slice_predicted,
        )
        per_slice[slice_name] = {
            "count": len(slice_rows),
            "labels": present_labels,
            "accuracy": metrics["accuracy"],
            "macro_f1": _macro_f1_for_labels(metrics, present_labels),
        }

    return ChallengeEvaluation(
        predictor_name=str(
            getattr(predictor, "model_name", predictor.__class__.__name__)
        ),
        model_version=str(getattr(predictor, "model_version", "unknown")),
        review_threshold=float(review_threshold),
        metrics=compute_classification_metrics(expected, predicted),
        per_slice=per_slice,
        rows=tuple(rows),
        route_counts=dict(
            sorted(Counter(row.routing.route for row in rows).items())
        ),
        low_confidence_count=sum(
            _prediction_score(row.prediction) < review_threshold for row in rows
        ),
    )


def _prediction_score(prediction: PredictionResult) -> float:
    score = getattr(prediction, "model_score", None)
    if score is None:
        score = getattr(prediction, "confidence", None)
    if score is None:
        raise ValueError("predictor result has no model score or confidence")
    return float(score)


def _route_prediction(
    text: str,
    prediction: PredictionResult,
    review_threshold: float,
) -> RoutingDecision:
    score = _prediction_score(prediction)
    try:
        return route_prediction(
            text,
            prediction.predicted_label,
            score,
            review_threshold=review_threshold,
        )
    except TypeError as exc:
        if "review_threshold" not in str(exc):
            raise
        return route_prediction(
            text,
            prediction.predicted_label,
            score,
            confidence_threshold=review_threshold,
        )


def _baseline_threshold(model_path: Path) -> float:
    manifest_path = model_path.with_suffix(".manifest.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return float(payload["selected_review_threshold"])


def _evaluate_baseline(
    model_path: Path,
    examples: list[ChallengeExample],
) -> ChallengeEvaluation:
    if not model_path.is_file():
        raise FileNotFoundError(
            f"selected production baseline artifact is missing: {model_path}; "
            "use --demo-only only for an explicitly demo-only report"
        )
    predictor = BaselinePredictor(model_path)
    return evaluate_predictor(
        predictor,
        examples,
        review_threshold=_baseline_threshold(model_path),
    )


def _format_metric(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def _macro_f1_for_labels(
    metrics: dict[str, Any],
    labels: list[str],
) -> float:
    """Calculate present-label macro F1 from the all-label confusion matrix."""
    matrix = metrics["confusion_matrix"]
    positions = {label: index for index, label in enumerate(metrics["labels"])}
    f1_values = []
    for label in labels:
        index = positions[label]
        true_positive = matrix[index][index]
        actual = sum(matrix[index])
        predicted = sum(row[index] for row in matrix)
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / actual if actual else 0.0
        f1_values.append(
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
    return sum(f1_values) / len(f1_values)


def _confusion_matrix_markdown(
    evaluation: ChallengeEvaluation,
) -> list[str]:
    labels = evaluation.metrics["labels"]
    matrix = evaluation.metrics["confusion_matrix"]
    lines = [
        f"### {evaluation.predictor_name}",
        "",
        "Rows are expected labels; columns are predicted labels.",
        "",
        "| Expected \\ Predicted | " + " | ".join(labels) + " |",
        "|---|" + "---:|" * len(labels),
    ]
    lines.extend(
        "| " + label + " | " + " | ".join(str(value) for value in row) + " |"
        for label, row in zip(labels, matrix, strict=True)
    )
    return lines


def _routing_lines(evaluation: ChallengeEvaluation) -> list[str]:
    total = len(evaluation.rows)
    low_rate = evaluation.low_confidence_count / total if total else 0.0
    lines = [
        f"### {evaluation.predictor_name}",
        "",
        f"- Review threshold: `{evaluation.review_threshold:.2f}` "
        "(model score, not a calibrated probability)",
        f"- Low-confidence rows: {evaluation.low_confidence_count}/{total} "
        f"({low_rate:.1%})",
        "- Routes: "
        + ", ".join(
            f"`{route}`={count}"
            for route, count in evaluation.route_counts.items()
        ),
        "",
        "Rows routed away from `auto_label` are review/support evidence, not "
        "automatic business decisions.",
        "",
    ]
    routed_rows = [row for row in evaluation.rows if row.routing.requires_human_review]
    if routed_rows:
        lines.extend(
            [
                "| ID | Expected | Predicted | Route | Reason codes |",
                "|---|---|---|---|---|",
            ]
        )
        lines.extend(
            "| {id} | {expected} | {predicted} | `{route}` | {reasons} |".format(
                id=row.example.id,
                expected=row.example.expected_label,
                predicted=row.prediction.predicted_label,
                route=row.routing.route,
                reasons=", ".join(row.routing.reason_codes) or "none",
            )
            for row in routed_rows[:12]
        )
        if len(routed_rows) > 12:
            lines.append(f"| … | | | | {len(routed_rows) - 12} more routed rows |")
    else:
        lines.append("No rows were routed away from `auto_label`.")
    lines.append("")
    return lines


def _failure_lines(evaluation: ChallengeEvaluation) -> list[str]:
    failures = [row for row in evaluation.rows if not row.is_correct]
    lines = [
        f"### {evaluation.predictor_name}",
        "",
        f"Misclassified rows: **{len(failures)} of {len(evaluation.rows)}**.",
        "",
    ]
    if not failures:
        lines.append("No failures on this small fixture.")
        lines.append("")
        return lines

    lines.extend(
        [
            "The table shows the first 12 failures in frozen fixture order; the "
            "count above does not hide failures outside the table.",
            "",
            "| ID | Expected | Predicted | Score | Route | Text | Ground-truth rationale |",
            "|---|---|---|---:|---|---|---|",
        ]
    )
    lines.extend(
        "| {id} | {expected} | {predicted} | {score:.4f} | `{route}` | {text} | {rationale} |".format(
            id=row.example.id,
            expected=row.example.expected_label,
            predicted=row.prediction.predicted_label,
            score=_prediction_score(row.prediction),
            route=row.routing.route,
            text=_escape_table(row.example.text),
            rationale=_escape_table(row.example.rationale),
        )
        for row in failures[:12]
    )
    lines.append("")
    return lines


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_report(
    *,
    examples: list[ChallengeExample],
    baseline: ChallengeEvaluation | None,
    demo: ChallengeEvaluation | None,
) -> str:
    lines = [
        "# Thai Sentiment Robustness Challenge",
        "",
        "This is a small, manually authored, synthetic diagnostic fixture. It is "
        "not a new benchmark and must not be used as training, hyperparameter "
        "tuning, or model-selection data.",
        "",
        "## Methodology",
        "",
        f"- Frozen examples: {len(examples)}",
        f"- Slices: {', '.join(ALLOWED_SLICES)}",
        "- Provenance: manually authored synthetic Thai text; no scraped customer "
        "reviews and no private data.",
        "- The selected production baseline is evaluated as currently built; no "
        "retraining, challenge-set tuning, or threshold selection is performed.",
        "- Overall macro F1 uses all four contract labels. Per-slice macro F1 uses "
        "only labels present in that slice.",
        "",
        "## Selected production baseline",
        "",
    ]
    if baseline is None:
        lines.extend(
            [
                "The selected production baseline was not evaluated in this "
                "invocation. A model artifact is required for this section; this "
                "report is demo-only.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- Model: `{baseline.predictor_name}`",
                f"- Model version: `{baseline.model_version}`",
                f"- Routing threshold: `{baseline.review_threshold:.2f}`",
                "",
                "| Accuracy | Macro F1 |",
                "|---:|---:|",
                f"| {baseline.metrics['accuracy']:.4f} | "
                f"{baseline.metrics['macro_f1']:.4f} |",
                "",
            ]
        )

    lines.extend(["## Deterministic demo predictor", ""])
    if demo is None:
        lines.extend(["Not evaluated.", ""])
    else:
        lines.extend(
            [
                f"- Model: `{demo.predictor_name}`",
                f"- Model version: `{demo.model_version}`",
                "- This result is separate demo evidence and is not a production "
                "baseline result.",
                "",
                "| Accuracy | Macro F1 |",
                "|---:|---:|",
                f"| {demo.metrics['accuracy']:.4f} | "
                f"{demo.metrics['macro_f1']:.4f} |",
                "",
            ]
        )

    lines.extend(
        [
            "## Per-slice results",
            "",
            "Per-slice figures are descriptive diagnostics on a tiny, intentionally "
            "non-representative fixture.",
            "",
            "| Slice | N | Baseline accuracy | Baseline macro F1 | Demo accuracy | Demo macro F1 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for slice_name in ALLOWED_SLICES:
        baseline_slice = baseline.per_slice.get(slice_name) if baseline else None
        demo_slice = demo.per_slice.get(slice_name) if demo else None
        source_slice = baseline_slice or demo_slice
        count = source_slice["count"] if source_slice else 0
        lines.append(
            f"| {slice_name} | {count} | "
            f"{_format_metric(baseline_slice['accuracy'] if baseline_slice else None)} | "
            f"{_format_metric(baseline_slice['macro_f1'] if baseline_slice else None)} | "
            f"{_format_metric(demo_slice['accuracy'] if demo_slice else None)} | "
            f"{_format_metric(demo_slice['macro_f1'] if demo_slice else None)} |"
        )
    lines.append("")

    lines.extend(["## Confusion matrices", ""])
    for evaluation in (baseline, demo):
        if evaluation is not None:
            lines.extend(_confusion_matrix_markdown(evaluation))
            lines.append("")

    lines.extend(["## Low-confidence and review-routing behavior", ""])
    for evaluation in (baseline, demo):
        if evaluation is not None:
            lines.extend(_routing_lines(evaluation))

    lines.extend(["## Representative failure examples", ""])
    for evaluation in (baseline, demo):
        if evaluation is not None:
            lines.extend(_failure_lines(evaluation))

    lines.extend(
        [
            "## Limitations",
            "",
            "- The fixture is small, manually authored, and designed to expose "
            "specific linguistic slices; its scores are not population estimates.",
            "- Ground truth for mixed and sarcasm-like text is judgment-based even "
            "where the rationale is deliberately conservative.",
            "- Results can reflect vocabulary coverage and preprocessing behavior "
            "rather than broad Thai language competence.",
            "- Routing uses the existing operational policy and model score; it is "
            "not a calibrated uncertainty estimate or a safety guarantee.",
            "- Wisesight held-out evaluation remains the benchmark evidence for the "
            "selected model; this synthetic challenge is diagnostic evidence only.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_report(
    *,
    dataset_path: Path = CHALLENGE_DATASET_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
    baseline_model_path: Path | None = DEFAULT_BASELINE_MODEL_PATH,
    include_demo: bool = True,
) -> str:
    examples = load_challenge_dataset(dataset_path)
    baseline = (
        _evaluate_baseline(baseline_model_path, examples)
        if baseline_model_path is not None
        else None
    )
    demo_threshold = baseline.review_threshold if baseline else DEFAULT_REVIEW_THRESHOLD
    demo = (
        evaluate_predictor(
            DemoPredictor(),
            examples,
            review_threshold=demo_threshold,
        )
        if include_demo
        else None
    )
    report = render_report(examples=examples, baseline=baseline, demo=demo)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate the frozen Thai robustness challenge fixture."
    )
    parser.add_argument("--dataset", type=Path, default=CHALLENGE_DATASET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--baseline-model",
        type=Path,
        default=DEFAULT_BASELINE_MODEL_PATH,
    )
    parser.add_argument(
        "--demo-only",
        action="store_true",
        help="skip the selected production baseline and report demo evidence only",
    )
    parser.add_argument(
        "--no-demo",
        action="store_true",
        help="omit the separate deterministic demo predictor section",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = generate_report(
        dataset_path=args.dataset,
        report_path=args.output,
        baseline_model_path=None if args.demo_only else args.baseline_model,
        include_demo=not args.no_demo,
    )
    print(f"wrote {args.output} ({len(report.splitlines())} lines)")


if __name__ == "__main__":
    main()
