PYTHON ?= python

.PHONY: setup lint format test evaluate monitor explain demo challenge api frontend-test frontend-build clean guardrails

setup:
	$(PYTHON) -m pip install -r requirements-ci.txt

lint:
	$(PYTHON) -m compileall -q src scripts tests
	$(PYTHON) scripts/check_repo_guardrails.py

format:
	@echo "No Python formatter is configured; no files changed."

test:
	$(PYTHON) -m pytest

evaluate:
	$(PYTHON) -m src.evaluation.model_governance

monitor:
	$(PYTHON) -m src.evaluation.monitoring
	$(PYTHON) -m src.evaluation.active_learning

explain:
	$(PYTHON) -m src.evaluation.explanations

demo:
	$(PYTHON) scripts/generate_local_sentiment_report.py

challenge:
	$(PYTHON) -m src.evaluation.robustness_challenge
api:
	$(PYTHON) -m uvicorn src.api.main:app --reload --port 8000

frontend-test:
	cd frontend && npm test && npm run lint

frontend-build:
	cd frontend && npm run build

guardrails:
	$(PYTHON) scripts/check_repo_guardrails.py

clean:
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in [pathlib.Path('.pytest_cache'), pathlib.Path('.tmp'), pathlib.Path('frontend/dist'), pathlib.Path('frontend/coverage'), *pathlib.Path('.').rglob('__pycache__')]]"
