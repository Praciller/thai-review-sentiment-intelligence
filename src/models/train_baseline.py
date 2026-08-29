"""Train and compare TF-IDF baseline sentiment models."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.data.dataset_paths import ensure_not_diagnostic_challenge
from src.evaluation.metrics import (
    classification_report_markdown,
    compute_classification_metrics,
)
from src.models.splitting import (
    apply_split_manifest,
    create_stratified_split,
)
from src.utils.constants import SENTIMENT_LABELS
from src.utils.reproducibility import set_global_seed

PROCESSED_DATA_PATH = Path("data/processed/wisesight_processed.csv")
SPLIT_MANIFEST_PATH = Path("data/processed/split_manifest.csv")
MODEL_OUTPUT_PATH = Path("models/baseline_model.joblib")
METRICS_OUTPUT_PATH = Path("reports/baseline_metrics.json")
REPORT_OUTPUT_PATH = Path("reports/baseline_classification_report.md")
PREDICTIONS_OUTPUT_PATH = Path("reports/baseline_predictions.csv")


@dataclass
class BaselineResult:
    model_name: str
    pipeline: Pipeline
    metrics: dict[str, Any]
    predictions: pd.DataFrame


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_features=50_000,
        sublinear_tf=True,
        tokenizer=str.split,
        preprocessor=None,
        token_pattern=None,
        lowercase=False,
    )


def build_baseline_models(seed: int) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            [
                ("tfidf", _vectorizer()),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1_000,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        ),
        "linear_svm": Pipeline(
            [
                ("tfidf", _vectorizer()),
                (
                    "classifier",
                    CalibratedClassifierCV(
                        LinearSVC(
                            class_weight="balanced",
                            random_state=seed,
                        ),
                        cv=3,
                    ),
                ),
            ]
        ),
    }


def _prediction_frame(
    *,
    test_frame: pd.DataFrame,
    pipeline: Pipeline,
    predictions: np.ndarray,
    probabilities: np.ndarray,
    model_name: str,
) -> pd.DataFrame:
    classifier = pipeline.named_steps["classifier"]
    classes = list(classifier.classes_)
    probability_by_label = {
        label: probabilities[:, classes.index(label)]
        if label in classes
        else np.zeros(len(test_frame))
        for label in SENTIMENT_LABELS
    }

    result = test_frame.loc[
        :,
        ["row_id", "text", "label", "text_length"],
    ].copy()
    result["predicted_label"] = predictions
    result["confidence"] = probabilities.max(axis=1)
    result["model_name"] = model_name
    for label, values in probability_by_label.items():
        result[f"probability_{label}"] = values
    return result.reset_index(drop=True)


def train_baseline_candidates(
    frame: pd.DataFrame,
    manifest: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, BaselineResult]:
    set_global_seed(seed)
    prepared = apply_split_manifest(frame, manifest)
    prepared["cleaned_text"] = prepared["cleaned_text"].fillna("").astype(str)
    train_frame = prepared.loc[prepared["split"] == "train"]
    test_frame = prepared.loc[prepared["split"] == "test"]
    if train_frame.empty or test_frame.empty:
        raise ValueError("split manifest must contain train and test rows")

    results: dict[str, BaselineResult] = {}
    for model_name, pipeline in build_baseline_models(seed).items():
        pipeline.fit(train_frame["cleaned_text"], train_frame["label"])
        predicted = pipeline.predict(test_frame["cleaned_text"])
        probabilities = pipeline.predict_proba(test_frame["cleaned_text"])
        metrics = compute_classification_metrics(
            test_frame["label"].tolist(),
            predicted.tolist(),
        )
        results[model_name] = BaselineResult(
            model_name=model_name,
            pipeline=pipeline,
            metrics=metrics,
            predictions=_prediction_frame(
                test_frame=test_frame,
                pipeline=pipeline,
                predictions=predicted,
                probabilities=probabilities,
                model_name=model_name,
            ),
        )
    return results


def _log_mlflow(
    *,
    result: BaselineResult,
    seed: int,
    dataset_rows: int,
) -> None:
    if os.getenv("MLFLOW_ENABLED", "false").lower() != "true":
        return

    try:
        import mlflow
    except ImportError:
        print("MLflow enabled but not installed; continuing without tracking.")
        return

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("thai-review-sentiment")
    with mlflow.start_run(run_name=result.model_name):
        mlflow.log_params(
            {
                "model_name": result.model_name,
                "seed": seed,
                "dataset_rows": dataset_rows,
                "dataset_version": "wisesight-official",
            }
        )
        mlflow.log_metrics(
            {
                key: value
                for key, value in result.metrics.items()
                if isinstance(value, float)
            }
        )


def save_baseline_artifacts(
    *,
    results: dict[str, BaselineResult],
    seed: int,
    dataset_rows: int,
    model_path: Path = MODEL_OUTPUT_PATH,
    metrics_path: Path = METRICS_OUTPUT_PATH,
    report_path: Path = REPORT_OUTPUT_PATH,
    predictions_path: Path = PREDICTIONS_OUTPUT_PATH,
) -> BaselineResult:
    best = max(
        results.values(),
        key=lambda result: (result.metrics["macro_f1"], result.model_name),
    )
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best.pipeline,
            "model_name": best.model_name,
            "labels": list(SENTIMENT_LABELS),
            "seed": seed,
            "trained_at": datetime.now(UTC).isoformat(),
        },
        model_path,
    )

    metrics_payload = {
        "best_model": best.model_name,
        "seed": seed,
        "dataset_rows": dataset_rows,
        "models": {
            name: result.metrics for name, result in results.items()
        },
    }
    metrics_path.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report_sections = ["# Baseline Classification Reports", ""]
    prediction_frames = []
    for name, result in results.items():
        report_sections.append(
            classification_report_markdown(
                result.predictions["label"],
                result.predictions["predicted_label"],
                title=name.replace("_", " ").title(),
            )
        )
        prediction_frames.append(result.predictions)
        _log_mlflow(result=result, seed=seed, dataset_rows=dataset_rows)
    report_path.write_text("\n".join(report_sections), encoding="utf-8")
    pd.concat(prediction_frames, ignore_index=True).to_csv(
        predictions_path,
        index=False,
    )
    return best


def _load_or_create_manifest(
    frame: pd.DataFrame,
    *,
    path: Path,
    seed: int,
) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    manifest = create_stratified_split(frame, seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(path, index=False)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train baseline sentiment models.")
    parser.add_argument("--input", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument(
        "--split-manifest",
        type=Path,
        default=SPLIT_MANIFEST_PATH,
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model-output", type=Path, default=MODEL_OUTPUT_PATH)
    parser.add_argument("--metrics-output", type=Path, default=METRICS_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=REPORT_OUTPUT_PATH)
    parser.add_argument(
        "--predictions-output",
        type=Path,
        default=PREDICTIONS_OUTPUT_PATH,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    ensure_not_diagnostic_challenge(args.input)
    frame = pd.read_csv(args.input)
    manifest = _load_or_create_manifest(
        frame,
        path=args.split_manifest,
        seed=args.seed,
    )
    results = train_baseline_candidates(frame, manifest, seed=args.seed)
    best = save_baseline_artifacts(
        results=results,
        seed=args.seed,
        dataset_rows=len(frame),
        model_path=args.model_output,
        metrics_path=args.metrics_output,
        report_path=args.report_output,
        predictions_path=args.predictions_output,
    )
    print(
        f"Saved {best.model_name} with macro F1 "
        f"{best.metrics['macro_f1']:.4f} to {args.model_output}"
    )


if __name__ == "__main__":
    main()
