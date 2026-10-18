# VYBE Synthetic Match API

Python **3.11+** and FastAPI. This service reconstructs scores and event counts from a fictional football match, and provides grounded explanations.

## Setup (Windows PowerShell)

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m uvicorn vybe.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs for the OpenAPI explorer.

## Endpoints

- `GET /health`: readiness check.
- `POST /v1/matches/replay?through_event=N`: deterministic match state after N events.
- `POST /v1/matches/replay/states`: all post-event states in one request (the frontend uses this to avoid rate-limit exhaustion).
- `POST /v1/matches/explain/{event_id}?persona=young|accessible|analyst`: grounded goal explanation.
- `POST /v1/matches/narrate/{event_id}?persona=young|accessible|analyst`: narration with optional Azure-assisted selection of strictly verified fact segments, with deterministic fallback.

- `POST /v1/matches/ask`: deterministic, evidence-backed questions about the supplied synthetic match.

All `/v1/matches/*` routes share a per-process, peer-IP limit of 60 requests per minute and a 256 KiB request-body limit. The guard is not a distributed quota.

POST endpoints take a synthetic match definition as JSON. Do not use real match claims or disclose Azure secrets in code. The deterministic event engine remains the source of truth for scores and counts.

See [project README](../../README.md) for frontend setup, personas and known limitations.
