"""Fine-tune a Thai Transformer sentiment classifier with PyTorch Trainer."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import softmax

from src.evaluation.metrics import (
    classification_report_markdown,
    compute_classification_metrics,
)
from src.models.splitting import apply_split_manifest
from src.utils.constants import SENTIMENT_LABELS
from src.utils.reproducibility import set_global_seed

DEFAULT_MODEL_NAME = "airesearch/wangchanberta-base-att-spm-uncased"
PROCESSED_DATA_PATH = Path("data/processed/wisesight_processed.csv")
SPLIT_MANIFEST_PATH = Path("data/processed/split_manifest.csv")
MODEL_OUTPUT_DIR = Path("models/wangchanberta_sentiment")
METRICS_OUTPUT_PATH = Path("reports/transformer_metrics.json")
REPORT_OUTPUT_PATH = Path("reports/transformer_classification_report.md")
PREDICTIONS_OUTPUT_PATH = Path("reports/transformer_predictions.csv")


def _debug_sample(frame: pd.DataFrame, *, seed: int) -> pd.DataFrame:
    sampled_indices: list[int] = []
    for _, group in frame.groupby(["split", "label"], sort=True):
        sampled_indices.extend(
            group.sample(
                n=min(len(group), 8),
                random_state=seed,
            ).index.tolist()
        )
    sampled = frame.loc[sampled_indices].reset_index(drop=True)
    if sampled.empty:
        raise ValueError("debug sample is empty")
    return sampled


def _build_hf_dataset(
    frame: pd.DataFrame,
    *,
    tokenizer: Any,
    label_to_id: dict[str, int],
    max_length: int,
) -> Any:
    from datasets import Dataset

    prepared = pd.DataFrame(
        {
            "text": frame["text"].astype(str),
            "labels": frame["label"].map(label_to_id).astype(int),
        }
    )
    dataset = Dataset.from_pandas(prepared, preserve_index=False)

    def tokenize(batch: dict[str, list[str]]) -> dict[str, Any]:
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
        )

    return dataset.map(tokenize, batched=True, remove_columns=["text"])


def train_transformer(
    *,
    frame: pd.DataFrame,
    manifest: pd.DataFrame,
    model_name: str,
    output_dir: Path,
    metrics_output: Path,
    report_output: Path,
    predictions_output: Path,
    seed: int,
    epochs: int,
    batch_size: int,
    max_length: int,
    debug: bool,
    use_cpu: bool,
) -> dict[str, Any]:
    try:
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            DataCollatorWithPadding,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Transformer dependencies are missing. Install requirements.txt."
        ) from exc

    set_global_seed(seed)
    prepared = apply_split_manifest(frame, manifest)
    if debug:
        prepared = _debug_sample(prepared, seed=seed)
        epochs = 1

    label_to_id = {label: index for index, label in enumerate(SENTIMENT_LABELS)}
    id_to_label = {index: label for label, index in label_to_id.items()}
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(SENTIMENT_LABELS),
        label2id=label_to_id,
        id2label=id_to_label,
        ignore_mismatched_sizes=True,
    )

    datasets_by_split = {
        split_name: _build_hf_dataset(
            prepared.loc[prepared["split"] == split_name],
            tokenizer=tokenizer,
            label_to_id=label_to_id,
            max_length=max_length,
        )
        for split_name in ("train", "validation", "test")
    }
    if any(len(dataset) == 0 for dataset in datasets_by_split.values()):
        raise ValueError("train, validation, and test splits must be non-empty")

    def compute_metrics_for_trainer(eval_prediction: Any) -> dict[str, float]:
        logits, label_ids = eval_prediction
        predicted_ids = np.argmax(logits, axis=-1)
        metrics = compute_classification_metrics(
            [id_to_label[int(index)] for index in label_ids],
            [id_to_label[int(index)] for index in predicted_ids],
        )
        return {
            key: value
            for key, value in metrics.items()
            if isinstance(value, float)
        }

    report_to = (
        ["mlflow"]
        if os.getenv("MLFLOW_ENABLED", "false").lower() == "true"
        else []
    )
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        learning_rate=2e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        save_total_limit=1,
        logging_steps=1 if debug else 25,
        report_to=report_to,
        seed=seed,
        data_seed=seed,
        use_cpu=use_cpu,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=datasets_by_split["train"],
        eval_dataset=datasets_by_split["validation"],
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics_for_trainer,
    )
    trainer.train()
    test_output = trainer.predict(datasets_by_split["test"])
    predicted_ids = np.argmax(test_output.predictions, axis=-1)
    probability_matrix = softmax(test_output.predictions, axis=-1)

    test_frame = prepared.loc[prepared["split"] == "test"].reset_index(drop=True)
    y_true = test_frame["label"].tolist()
    y_pred = [id_to_label[int(index)] for index in predicted_ids]
    metrics = compute_classification_metrics(y_true, y_pred)
    metrics_payload = {
        "model_name": model_name,
        "debug": debug,
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        **metrics,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    metrics_output.write_text(
        json.dumps(metrics_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_output.write_text(
        classification_report_markdown(
            y_true,
            y_pred,
            title="WangchanBERTa Classification Report",
        ),
        encoding="utf-8",
    )

    predictions = test_frame.loc[
        :,
        ["row_id", "text", "label", "text_length"],
    ].copy()
    predictions["predicted_label"] = y_pred
    predictions["confidence"] = probability_matrix.max(axis=1)
    predictions["model_name"] = "wangchanberta"
    for label, label_id in label_to_id.items():
        predictions[f"probability_{label}"] = probability_matrix[:, label_id]
    predictions.to_csv(predictions_output, index=False)
    return metrics_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fine-tune WangchanBERTa for sentiment classification."
    )
    parser.add_argument("--input", type=Path, default=PROCESSED_DATA_PATH)
    parser.add_argument(
        "--split-manifest",
        type=Path,
        default=SPLIT_MANIFEST_PATH,
    )
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--output-dir", type=Path, default=MODEL_OUTPUT_DIR)
    parser.add_argument("--metrics-output", type=Path, default=METRICS_OUTPUT_PATH)
    parser.add_argument("--report-output", type=Path, default=REPORT_OUTPUT_PATH)
    parser.add_argument(
        "--predictions-output",
        type=Path,
        default=PREDICTIONS_OUTPUT_PATH,
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--cpu", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    frame = pd.read_csv(args.input)
    manifest = pd.read_csv(args.split_manifest)
    metrics = train_transformer(
        frame=frame,
        manifest=manifest,
        model_name=args.model_name,
        output_dir=args.output_dir,
        metrics_output=args.metrics_output,
        report_output=args.report_output,
        predictions_output=args.predictions_output,
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        max_length=args.max_length,
        debug=args.debug,
        use_cpu=args.cpu,
    )
    print(
        f"Saved Transformer checkpoint to {args.output_dir}; "
        f"macro F1={metrics['macro_f1']:.4f}"
    )


if __name__ == "__main__":
    main()
