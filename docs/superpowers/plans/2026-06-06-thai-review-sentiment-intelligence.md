# Thai Review Sentiment Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans`.
> Steps use checkbox syntax for tracking.

**Goal:** Deliver the requirements as a runnable Thai NLP portfolio repository.

**Architecture:** A deterministic Python data/ML pipeline produces versioned
artifacts consumed by a model registry and FastAPI. A React/Vite client consumes
only the HTTP contract and computes presentation summaries locally.

**Tech Stack:** Python 3.12, pandas, scikit-learn, PyThaiNLP, PyTorch,
Transformers, FastAPI, pytest, React 19, Vite 8, Tailwind CSS 4, Recharts, Vitest.

---

### Task 1: Foundation and preprocessing

**Files:** `requirements.txt`, `src/features/preprocess_thai_text.py`,
`tests/test_preprocess.py`, config/package files.

- [ ] Write behavior tests for normalization, URLs, whitespace, repeated Thai
      characters, tokenization, labels, and topics.
- [ ] Run focused tests and confirm RED.
- [ ] Implement the smallest reusable preprocessing API.
- [ ] Run focused tests and confirm GREEN.

### Task 2: Data ingestion, validation, and EDA

**Files:** `src/data/load_wisesight.py`, `src/data/validate_data.py`,
`src/data/eda.py`, `notebooks/01_eda.ipynb`, `tests/test_data_pipeline.py`.

- [ ] Add fixture-driven tests for label normalization, empty removal, duplicates,
      report fields, figures, and deterministic output paths.
- [ ] Implement official corpus resolution, CSV persistence, validation report,
      EDA summary, and two figures.
- [ ] Run data tests and CLI smoke checks.

### Task 3: Modeling and evaluation

**Files:** `src/models/*`, `src/evaluation/*`, `tests/test_modeling.py`.

- [ ] Test deterministic stratified split and common metric schema.
- [ ] Implement Logistic Regression and calibrated Linear SVM pipelines.
- [ ] Save model bundle, per-model metrics, predictions, and classification report.
- [ ] Implement WangchanBERTa Trainer CLI with debug subset and one epoch.
- [ ] Implement model comparison, confusion matrix, and error analysis.
- [ ] Run model tests and `--help` smoke checks without downloading a model.

### Task 4: FastAPI inference

**Files:** `src/api/main.py`, `src/models/predict.py`,
`src/models/model_registry.py`, `tests/test_api.py`.

- [ ] Write API tests with injected predictor; confirm RED.
- [ ] Implement lifespan model loading, CORS, Pydantic validation, single/batch
      prediction, and deterministic demo fallback.
- [ ] Run API tests and live curl smoke requests.

### Task 5: React application

**Files:** `frontend/src/**`, `frontend/package.json`, Vite/Tailwind config.

- [ ] Test CSV parsing and result aggregation.
- [ ] Build navigation, prediction, batch, and dashboard routes.
- [ ] Implement required components, API service, responsive table, skeletons,
      errors, keyboard focus, and semantic chart summaries.
- [ ] Run Vitest, TypeScript, ESLint, and production build.

### Task 6: Delivery artifacts

**Files:** Dockerfiles, Compose, docs, README, sample data, screenshots,
`PORTFOLIO_REVIEW.md`.

- [ ] Add local and Docker setup with optional MLflow.
- [ ] Document data source, architecture, modeling, API, frontend, and limitations.
- [ ] Add evidence-based screenshots from the running application.
- [ ] Run full verification and requirement coverage review.

### Verification Commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall src
.\.venv\Scripts\python.exe -m src.models.train_transformer --help
.\.venv\Scripts\python.exe -m src.models.train_baseline --help
Set-Location frontend
npm test -- --run
npm run lint
npm run build
Set-Location ..
docker compose config
```
