"""Prediction implementations shared by FastAPI and local scripts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

import joblib
import numpy as np

from src.features.preprocess_thai_text import (
    detect_topic,
    normalize_label,
    preprocess_for_baseline,
)
from src.utils.constants import SENTIMENT_LABELS


@dataclass(frozen=True)
class PredictionResult:
    text: str
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]
    model_name: str
    topic: str
    topic_method: str = "rule_based"


class Predictor(Protocol):
    model_name: str

    def predict(self, texts: Sequence[str]) -> list[PredictionResult]:
        """Predict ordered sentiment results for input texts."""


class BaselinePredictor:
    def __init__(self, model_path: Path) -> None:
        bundle = joblib.load(model_path)
        if not isinstance(bundle, dict) or "pipeline" not in bundle:
            raise ValueError("invalid baseline model bundle")
        self.pipeline = bundle["pipeline"]
        self.model_name = str(bundle.get("model_name", "baseline"))

    def predict(self, texts: Sequence[str]) -> list[PredictionResult]:
        cleaned = [preprocess_for_baseline(text) for text in texts]
        predicted = self.pipeline.predict(cleaned)
        probability_matrix = self.pipeline.predict_proba(cleaned)
        classes = list(self.pipeline.named_steps["classifier"].classes_)

        results = []
        for index, text in enumerate(texts):
            probabilities = {
                label: float(probability_matrix[index, classes.index(label)])
                if label in classes
                else 0.0
                for label in SENTIMENT_LABELS
            }
            results.append(
                PredictionResult(
                    text=text,
                    predicted_label=str(predicted[index]),
                    confidence=max(probabilities.values()),
                    probabilities=probabilities,
                    model_name=self.model_name,
                    topic=detect_topic(text),
                )
            )
        return results


class TransformerPredictor:
    def __init__(self, model_path: Path, *, max_length: int = 256) -> None:
        try:
            import torch
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
        except ImportError as exc:
            raise RuntimeError(
                "Transformer dependencies are missing. Install requirements.txt."
            ) from exc

        self._torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            use_fast=False,
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path
        )
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.model.eval()
        self.max_length = max_length
        self.model_name = "wangchanberta"

    def predict(self, texts: Sequence[str]) -> list[PredictionResult]:
        encoded = self.tokenizer(
            list(texts),
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        encoded = {
            key: value.to(self.device) for key, value in encoded.items()
        }
        with self._torch.no_grad():
            logits = self.model(**encoded).logits
            probability_matrix = self._torch.softmax(logits, dim=-1).cpu().numpy()

        id_to_label = {
            int(index): normalize_label(label)
            for index, label in self.model.config.id2label.items()
        }
        results = []
        for row_index, text in enumerate(texts):
            probabilities = {
                label: 0.0 for label in SENTIMENT_LABELS
            }
            for class_id, probability in enumerate(
                probability_matrix[row_index]
            ):
                label = id_to_label[class_id]
                probabilities[label] = float(probability)
            predicted_label = max(probabilities, key=probabilities.get)
            results.append(
                PredictionResult(
                    text=text,
                    predicted_label=predicted_label,
                    confidence=probabilities[predicted_label],
                    probabilities=probabilities,
                    model_name=self.model_name,
                    topic=detect_topic(text),
                )
            )
        return results


class DemoPredictor:
    """Deterministic local fallback for API and frontend development."""

    model_name = "demo-rule-based"
    _positive = ("ดี", "อร่อย", "ชอบ", "เยี่ยม", "คุ้ม", "ประทับใจ", "สะอาด")
    _negative = ("แย่", "ช้า", "แพง", "เสีย", "สกปรก", "รอนาน", "ไม่ดี")
    _question = ("ไหม", "หรือ", "กี่", "เมื่อไหร่", "?", "หรือเปล่า")

    def predict(self, texts: Sequence[str]) -> list[PredictionResult]:
        return [self._predict_one(text) for text in texts]

    def _predict_one(self, text: str) -> PredictionResult:
        positive_matches = sum(token in text for token in self._positive)
        negative_matches = sum(token in text for token in self._negative)
        question_matches = sum(token in text for token in self._question)
        scores = {
            "positive": 0.8 + positive_matches,
            "negative": 0.8 + negative_matches,
            "neutral": 0.8,
            "question": 0.8 + question_matches,
        }
        raw = np.array([scores[label] for label in SENTIMENT_LABELS], dtype=float)
        exponentials = np.exp(raw - raw.max())
        normalized = exponentials / exponentials.sum()
        probabilities = {
            label: float(normalized[index])
            for index, label in enumerate(SENTIMENT_LABELS)
        }
        if question_matches:
            predicted_label = "question"
        elif negative_matches and negative_matches >= positive_matches:
            predicted_label = "negative"
        elif positive_matches:
            predicted_label = "positive"
        else:
            predicted_label = "neutral"
        return PredictionResult(
            text=text,
            predicted_label=predicted_label,
            confidence=probabilities[predicted_label],
            probabilities=probabilities,
            model_name=self.model_name,
            topic=detect_topic(text),
        )
