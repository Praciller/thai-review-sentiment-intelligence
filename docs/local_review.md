# Local Review

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-ci.txt
$env:DATA_MODE = "synthetic"
$env:MODEL_MODE = "local"
$env:ENABLE_EXTERNAL_AI = "false"
$env:MODEL_BACKEND = "demo"
python -m pytest
python scripts/generate_local_sentiment_report.py
python scripts/check_repo_guardrails.py
```

Expected results: all tests pass, the guardrail prints `repository guardrails
passed`, and the generator writes the ignored
`reports/local_sentiment_report.md` from ten synthetic fixtures. No API key,
external AI call, network request, hosted database, or private review is needed.

Run the API and frontend if browser review is needed:

```powershell
$env:MODEL_BACKEND = "demo"
uvicorn src.api.main:app --reload --port 8000
Set-Location frontend
npm ci
npm run dev
```

Open `http://localhost:5173`; API health is `http://localhost:8000/health`.

## Troubleshooting

- If `python` is unavailable, install Python 3.12 or use its absolute executable.
- If script execution is blocked, run `Set-ExecutionPolicy -Scope Process Bypass`.
- If port 8000 is busy, stop the existing process or select another port and set
  `VITE_API_URL` to match.
- If the API reports a trained artifact is missing, confirm
  `$env:MODEL_BACKEND = "demo"` for the offline path.
