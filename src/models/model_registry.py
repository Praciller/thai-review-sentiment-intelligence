"""Resolve one inference backend at application startup."""

from __future__ import annotations

from src.models.predict import (
    BaselinePredictor,
    DemoPredictor,
    Predictor,
    TransformerPredictor,
)
from src.utils.config import Settings


def load_predictor(settings: Settings) -> Predictor:
    backend = settings.model_backend

    if backend == "transformer":
        if not settings.transformer_model_path.exists():
            raise FileNotFoundError(settings.transformer_model_path)
        return TransformerPredictor(settings.transformer_model_path)

    if backend == "baseline":
        if not settings.baseline_model_path.exists():
            raise FileNotFoundError(settings.baseline_model_path)
        return BaselinePredictor(settings.baseline_model_path)

    if backend == "demo":
        return DemoPredictor()

    transformer_config = settings.transformer_model_path / "config.json"
    if transformer_config.exists():
        return TransformerPredictor(settings.transformer_model_path)
    if settings.baseline_model_path.exists():
        return BaselinePredictor(settings.baseline_model_path)
    if settings.app_env != "production":
        return DemoPredictor()
    raise RuntimeError("no trained model artifact is available in production")
