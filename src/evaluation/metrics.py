"""Common model metrics and report formatting."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from src.utils.constants import SENTIMENT_LABELS


def compute_classification_metrics(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    *,
    labels: Sequence[str] = SENTIMENT_LABELS,
) -> dict[str, Any]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                labels=labels,
                average="macro",
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                labels=labels,
                average="macro",
                zero_division=0,
            )
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                labels=labels,
                average="macro",
                zero_division=0,
            )
        ),
        "weighted_f1": float(
            f1_score(
                y_true,
                y_pred,
                labels=labels,
                average="weighted",
                zero_division=0,
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
            labels=labels,
        ).tolist(),
        "labels": list(labels),
    }


def classification_report_markdown(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    *,
    title: str,
    labels: Sequence[str] = SENTIMENT_LABELS,
) -> str:
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    lines = [
        f"# {title}",
        "",
        "| Label | Precision | Recall | F1 | Support |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in labels:
        metrics = report[label]
        lines.append(
            f"| {label} | {metrics['precision']:.4f} | "
            f"{metrics['recall']:.4f} | {metrics['f1-score']:.4f} | "
            f"{int(metrics['support'])} |"
        )
    lines.extend(
        [
            "",
            f"- Accuracy: {report['accuracy']:.4f}",
            f"- Macro F1: {report['macro avg']['f1-score']:.4f}",
            f"- Weighted F1: {report['weighted avg']['f1-score']:.4f}",
            "",
        ]
    )
    return "\n".join(lines)
