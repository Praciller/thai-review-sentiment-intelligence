"""Compare saved model metrics and render the selected confusion matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.utils.constants import SENTIMENT_LABELS

BASELINE_METRICS_PATH = Path("reports/baseline_metrics.json")
TRANSFORMER_METRICS_PATH = Path("reports/transformer_metrics.json")
BASELINE_PREDICTIONS_PATH = Path("reports/baseline_predictions.csv")
TRANSFORMER_PREDICTIONS_PATH = Path("reports/transformer_predictions.csv")
COMPARISON_REPORT_PATH = Path("reports/model_comparison.md")
CONFUSION_MATRIX_PATH = Path("reports/confusion_matrix.png")


def _load_model_metrics(
    baseline_path: Path,
    transformer_path: Path,
) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        models.update(baseline.get("models", {}))
    if transformer_path.exists():
        transformer = json.loads(transformer_path.read_text(encoding="utf-8"))
        models["wangchanberta"] = transformer
    if not models:
        raise FileNotFoundError("no model metric artifacts were found")
    return models


def _load_predictions_for_model(
    model_name: str,
    *,
    baseline_path: Path,
    transformer_path: Path,
) -> pd.DataFrame:
    if model_name == "wangchanberta":
        return pd.read_csv(transformer_path)
    predictions = pd.read_csv(baseline_path)
    return predictions.loc[predictions["model_name"] == model_name].copy()


def _save_confusion_matrix(predictions: pd.DataFrame, output_path: Path) -> None:
    matrix = confusion_matrix(
        predictions["label"],
        predictions["predicted_label"],
        labels=SENTIMENT_LABELS,
    )
    figure, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(matrix, cmap="Blues")
    axis.set_xticks(np.arange(len(SENTIMENT_LABELS)), SENTIMENT_LABELS)
    axis.set_yticks(np.arange(len(SENTIMENT_LABELS)), SENTIMENT_LABELS)
    axis.set_xlabel("Predicted label")
    axis.set_ylabel("Actual label")
    axis.set_title("Sentiment confusion matrix")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axis.text(
                column,
                row,
                str(matrix[row, column]),
                ha="center",
                va="center",
                color="white"
                if matrix[row, column] > matrix.max() / 2
                else "#0F2D52",
            )
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def generate_model_comparison(
    *,
    baseline_metrics_path: Path = BASELINE_METRICS_PATH,
    transformer_metrics_path: Path = TRANSFORMER_METRICS_PATH,
    baseline_predictions_path: Path = BASELINE_PREDICTIONS_PATH,
    transformer_predictions_path: Path = TRANSFORMER_PREDICTIONS_PATH,
    report_path: Path = COMPARISON_REPORT_PATH,
    confusion_matrix_path: Path = CONFUSION_MATRIX_PATH,
) -> str:
    models = _load_model_metrics(
        baseline_metrics_path,
        transformer_metrics_path,
    )
    best_model = max(
        models,
        key=lambda name: (models[name]["macro_f1"], name),
    )
    notes = {
        "logistic_regression": "TF-IDF baseline",
        "linear_svm": "Strong calibrated baseline",
        "wangchanberta": "PyTorch Transformer",
    }
    lines = [
        "# Model Comparison",
        "",
        "| Model | Accuracy | Macro F1 | Weighted F1 | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for model_name, metrics in models.items():
        lines.append(
            f"| {model_name} | {metrics['accuracy']:.4f} | "
            f"{metrics['macro_f1']:.4f} | {metrics['weighted_f1']:.4f} | "
            f"{notes.get(model_name, '')} |"
        )
    lines.extend(
        [
            "",
            f"Best model by macro F1: **{best_model}**.",
            "",
            "All entries use the shared split manifest at "
            "`data/processed/split_manifest.csv`.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

    predictions = _load_predictions_for_model(
        best_model,
        baseline_path=baseline_predictions_path,
        transformer_path=transformer_predictions_path,
    )
    _save_confusion_matrix(predictions, confusion_matrix_path)
    return best_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare trained sentiment models.")
    parser.add_argument(
        "--baseline-metrics",
        type=Path,
        default=BASELINE_METRICS_PATH,
    )
    parser.add_argument(
        "--transformer-metrics",
        type=Path,
        default=TRANSFORMER_METRICS_PATH,
    )
    parser.add_argument(
        "--baseline-predictions",
        type=Path,
        default=BASELINE_PREDICTIONS_PATH,
    )
    parser.add_argument(
        "--transformer-predictions",
        type=Path,
        default=TRANSFORMER_PREDICTIONS_PATH,
    )
    parser.add_argument("--report", type=Path, default=COMPARISON_REPORT_PATH)
    parser.add_argument(
        "--confusion-matrix",
        type=Path,
        default=CONFUSION_MATRIX_PATH,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    best_model = generate_model_comparison(
        baseline_metrics_path=args.baseline_metrics,
        transformer_metrics_path=args.transformer_metrics,
        baseline_predictions_path=args.baseline_predictions,
        transformer_predictions_path=args.transformer_predictions,
        report_path=args.report,
        confusion_matrix_path=args.confusion_matrix,
    )
    print(f"Generated comparison; best model is {best_model}")


if __name__ == "__main__":
    main()
