FROM node:24-alpine AS frontend-builder

WORKDIR /app/frontend

ARG VITE_API_URL=
ENV VITE_API_URL=${VITE_API_URL}

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.12-slim AS model-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-api.txt requirements-model-build.txt ./
RUN pip install --no-cache-dir -r requirements-model-build.txt

COPY src ./src
RUN python -m src.data.load_wisesight \
    && python -m src.data.validate_data \
    && python -m src.models.train_baseline --seed 42


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    MODEL_BACKEND=baseline \
    BASELINE_MODEL_PATH=/app/models/baseline_model.joblib \
    FRONTEND_DIST_PATH=/app/frontend/dist \
    FRONTEND_ORIGINS=http://localhost:7860 \
    PYTHAINLP_DATA=/tmp/pythainlp-data \
    PORT=7860

WORKDIR /app

COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src ./src
COPY --from=model-builder /app/models/baseline_model.joblib ./models/baseline_model.joblib
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
RUN addgroup --system app \
    && adduser --system --ingroup app app

USER app

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=3)"

CMD ["sh", "-c", "exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}"]
