"""FastAPI inference application."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator

from src.models.model_registry import load_predictor
from src.models.predict import PredictionResult, Predictor
from src.utils.config import Settings


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    runtime_mode: str


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    predicted_label: str
    confidence: float
    probabilities: dict[str, float]
    model_name: str
    topic: str
    topic_method: str


class BatchPredictionResponse(BaseModel):
    results: list[PredictionResponse]


class PredictRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must not be empty")
        return cleaned


class BatchPredictRequest(BaseModel):
    texts: list[str]

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, values: list[str]) -> list[str]:
        if not values:
            raise ValueError("texts must contain at least one item")

        cleaned_values = []
        for index, value in enumerate(values):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError(f"texts[{index}] must not be empty")
            cleaned_values.append(cleaned)
        return cleaned_values


def create_app(
    *,
    settings: Settings | None = None,
    predictor_factory: Callable[[], Predictor] | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings()
    resolved_factory = predictor_factory or (
        lambda: load_predictor(resolved_settings)
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.predictor = resolved_factory()
        yield
        app.state.predictor = None

    app = FastAPI(
        title="Thai Review Sentiment Intelligence API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        predictor = app.state.predictor
        return HealthResponse(
            status="ok",
            model_loaded=predictor is not None,
            model_name=predictor.model_name,
            runtime_mode=resolved_settings.app_env,
        )

    @app.post("/predict", response_model=PredictionResponse)
    def predict(request: PredictRequest) -> PredictionResponse:
        _validate_text_length(
            request.text,
            max_length=resolved_settings.max_text_length,
        )
        result = app.state.predictor.predict([request.text])[0]
        return _to_response(result)

    @app.post("/predict-batch", response_model=BatchPredictionResponse)
    def predict_batch(request: BatchPredictRequest) -> BatchPredictionResponse:
        if len(request.texts) > resolved_settings.max_batch_size:
            raise HTTPException(
                status_code=422,
                detail=(
                    "batch exceeds maximum size of "
                    f"{resolved_settings.max_batch_size}"
                ),
            )
        for text in request.texts:
            _validate_text_length(
                text,
                max_length=resolved_settings.max_text_length,
            )
        results = app.state.predictor.predict(request.texts)
        return BatchPredictionResponse(
            results=[_to_response(result) for result in results]
        )

    _attach_frontend(app, resolved_settings.frontend_dist_path)
    return app


def _to_response(result: PredictionResult) -> PredictionResponse:
    return PredictionResponse.model_validate(asdict(result))


def _validate_text_length(text: str, *, max_length: int) -> None:
    if len(text) > max_length:
        raise HTTPException(
            status_code=422,
            detail=f"text exceeds maximum length of {max_length}",
        )


def _attach_frontend(app: FastAPI, dist_path: Path) -> None:
    resolved_dist = dist_path.resolve()
    index_path = resolved_dist / "index.html"
    if not index_path.is_file():
        return

    assets_path = resolved_dist / "assets"
    if assets_path.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_path),
            name="frontend-assets",
        )

    @app.get("/", include_in_schema=False)
    def frontend_root() -> FileResponse:
        return FileResponse(index_path)

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_route(full_path: str) -> FileResponse:
        requested_path = (resolved_dist / full_path).resolve()
        try:
            requested_path.relative_to(resolved_dist)
        except ValueError:
            return FileResponse(index_path)
        if requested_path.is_file():
            return FileResponse(requested_path)
        return FileResponse(index_path)


app = create_app()
