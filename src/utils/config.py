"""Environment-backed application configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    model_backend: str = "auto"
    baseline_model_path: Path = Path("models/baseline_model.joblib")
    transformer_model_path: Path = Path("models/wangchanberta_sentiment")
    frontend_dist_path: Path = Path("frontend/dist")
    frontend_origins: str = "http://localhost:5173"
    max_text_length: int = 2_000
    max_batch_size: int = 100

    @field_validator("model_backend")
    @classmethod
    def validate_model_backend(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"auto", "baseline", "transformer", "demo"}
        if normalized not in allowed:
            raise ValueError(f"model_backend must be one of {sorted(allowed)}")
        return normalized

    @field_validator("frontend_origins")
    @classmethod
    def reject_wildcard_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not origins:
            raise ValueError("at least one frontend origin is required")
        if "*" in origins:
            raise ValueError("wildcard CORS origins are not allowed")
        return ",".join(origins)

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]
