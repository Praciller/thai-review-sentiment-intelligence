import pytest

from src.models.model_registry import load_predictor
from src.models.predict import DemoPredictor
from src.utils.config import Settings


def test_missing_artifact_falls_back_only_outside_production(tmp_path):
    settings = Settings(
        app_env="development",
        model_backend="auto",
        baseline_model_path=tmp_path / "missing.joblib",
        transformer_model_path=tmp_path / "missing-transformer",
    )

    assert isinstance(load_predictor(settings), DemoPredictor)

    production = settings.model_copy(update={"app_env": "production"})
    with pytest.raises(RuntimeError, match="no trained model artifact"):
        load_predictor(production)
