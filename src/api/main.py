"""FastAPI inference application."""

from __future__ import annotations

import json
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator

from src.evaluation.explanations import explain_prediction
from src.evaluation.model_governance import build_governance_summary
from src.evaluation.monitoring import sample_summary
from src.models.model_registry import load_predictor
from src.models.predict import PredictionResult, Predictor
from src.models.review_routing import route_prediction
from src.utils.config import Settings
from src.utils.constants import SENTIMENT_LABELS


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
    selected_production_model: str
    topic: str
    topic_method: str
    route: str
    requires_human_review: bool
    reason_codes: list[str]
    confidence_threshold: float
    evidence_terms: list[str]
    topic_terms: list[str]
    explanation_mode: str
    selection_metric: str


class BatchPredictionResponse(BaseModel):
    results: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    selected_production_model: str
    runtime_model_name: str
    selection_metric: str
    human_review_threshold: float
    supported_labels: list[str]


class MonitoringResponse(BaseModel):
    sample_size: int
    prediction_distribution: dict[str, float]
    confidence_distribution: dict[str, int]
    low_confidence_rate: float
    negative_rate: float
    question_rate: float
    topic_counts: dict[str, int]
    review_length: dict[str, float]
    drift_proxy: float
    warning_flags: list[str]


class GovernanceResponse(BaseModel):
    selected_production_model: str
    selection_metric: str
    accuracy: float
    macro_f1: float
    per_class_metrics: dict[str, dict[str, float]]
    confusion_matrix_summary: str
    low_confidence_review_count: int
    human_review_threshold: float
    known_failure_modes: list[str]
    wangchanberta_status: str


class ExplanationSampleResponse(BaseModel):
    results: list[PredictionResponse]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


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
    governance_summary = build_governance_summary(
        confidence_threshold=resolved_settings.human_review_threshold
    )
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

    @app.middleware("http")
    async def enforce_request_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if (
            content_length
            and content_length.isdigit()
            and int(content_length) > resolved_settings.max_request_bytes
        ):
            return JSONResponse(
                status_code=413,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="request_too_large",
                        message="request body exceeds configured limit",
                    )
                ).model_dump(),
            )
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _error: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "request validation failed",
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, error: HTTPException):
        detail = error.detail if isinstance(error.detail, dict) else {}
        return JSONResponse(
            status_code=error.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=str(detail.get("code", "http_error")),
                    message=str(detail.get("message", "request failed")),
                )
            ).model_dump(),
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

    @app.post(
        "/predict",
        response_model=PredictionResponse,
        responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def predict(request: PredictRequest) -> PredictionResponse:
        _validate_text_length(
            request.text,
            max_length=resolved_settings.max_text_length,
        )
        result = app.state.predictor.predict([request.text])[0]
        return _to_response(
            result,
            app.state.predictor,
            resolved_settings.human_review_threshold,
            governance_summary.selected_production_model,
            governance_summary.selection_metric,
        )

    @app.post(
        "/predict-batch",
        response_model=BatchPredictionResponse,
        responses={413: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    )
    def predict_batch(request: BatchPredictRequest) -> BatchPredictionResponse:
        if len(request.texts) > resolved_settings.max_batch_size:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "batch_too_large",
                    "message": (
                        "batch exceeds maximum size of "
                        f"{resolved_settings.max_batch_size}"
                    ),
                },
            )
        for text in request.texts:
            _validate_text_length(
                text,
                max_length=resolved_settings.max_text_length,
            )
        results = app.state.predictor.predict(request.texts)
        return BatchPredictionResponse(
            results=[
                _to_response(
                    result,
                    app.state.predictor,
                    resolved_settings.human_review_threshold,
                    governance_summary.selected_production_model,
                    governance_summary.selection_metric,
                )
                for result in results
            ]
        )

    @app.get("/model-info", response_model=ModelInfoResponse)
    def model_info() -> ModelInfoResponse:
        return ModelInfoResponse(
            selected_production_model=governance_summary.selected_production_model,
            runtime_model_name=app.state.predictor.model_name,
            selection_metric=governance_summary.selection_metric,
            human_review_threshold=governance_summary.human_review_threshold,
            supported_labels=list(SENTIMENT_LABELS),
        )

    @app.get("/monitoring/sample", response_model=MonitoringResponse)
    def monitoring_sample() -> MonitoringResponse:
        return MonitoringResponse.model_validate(asdict(sample_summary()))

    @app.get("/governance", response_model=GovernanceResponse)
    def governance() -> GovernanceResponse:
        return GovernanceResponse.model_validate(asdict(governance_summary))

    @app.get("/explanations/sample", response_model=ExplanationSampleResponse)
    def explanations_sample() -> ExplanationSampleResponse:
        fixtures = json.loads(
            Path("data/sample/synthetic_reviews.json").read_text(
                encoding="utf-8"
            )
        )
        results = app.state.predictor.predict([row["text"] for row in fixtures])
        return ExplanationSampleResponse(
            results=[
                _to_response(
                    result,
                    app.state.predictor,
                    resolved_settings.human_review_threshold,
                    governance_summary.selected_production_model,
                    governance_summary.selection_metric,
                )
                for result in results
            ]
        )

    _attach_frontend(app, resolved_settings.frontend_dist_path)
    return app


def _to_response(
    result: PredictionResult,
    predictor: Predictor,
    confidence_threshold: float,
    selected_production_model: str,
    selection_metric: str,
) -> PredictionResponse:
    routing = route_prediction(
        result.text,
        result.predicted_label,
        result.confidence,
        confidence_threshold=confidence_threshold,
    )
    explanation = explain_prediction(
        result,
        pipeline=getattr(predictor, "pipeline", None),
        confidence_threshold=confidence_threshold,
    )
    return PredictionResponse.model_validate(
        {
            **asdict(result),
            **asdict(routing),
            **asdict(explanation),
            "selected_production_model": selected_production_model,
            "selection_metric": selection_metric,
        }
    )


def _validate_text_length(text: str, *, max_length: int) -> None:
    if len(text) > max_length:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "text_too_long",
                "message": f"text exceeds maximum length of {max_length}",
            },
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
