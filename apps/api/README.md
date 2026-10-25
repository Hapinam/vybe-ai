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

- `POST /v1/matches/ask`: legacy deterministic, evidence-backed questions about the supplied synthetic match.
- `POST /v1/matches/director/ask`: Ask the Match model-directed allowlisted tool selection with deterministic fallback.
- `POST /v1/matches/insights`: grounded persona-specific match insights.
- `POST /v1/matches/speech`: Azure AI Speech MP3 when configured; browser speech is a frontend fallback.

All `/v1/matches/*` routes share a per-process ASGI-peer limit of **240 requests/minute** and a **256 KiB** request-body limit. `/v1/matches/director/ask`, `/v1/matches/narrate/*` and `/v1/matches/speech` additionally share a **30 requests/minute** bucket. These are not distributed per-user quotas or cost caps.

POST endpoints take a synthetic match definition as JSON. Do not use real match claims or disclose Azure secrets in code. The deterministic event engine remains the source of truth for scores and counts.

For optional model configuration see [Foundry launch notes](../../docs/FOUNDRY_REQUIRED_LAUNCH.md); for owner-observed production evidence see [October 25 evidence pack](../../docs/VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). See [project README](../../README.md) for frontend setup, personas and known limitations.
