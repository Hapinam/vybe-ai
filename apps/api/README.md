# VYBE Synthetic Match API

Python **3.11+** and FastAPI. This service reconstructs scores and event counts from a fictional football match, and provides grounded explanations.

## Setup (Windows PowerShell)

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-test.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest tests -q
$env:VYBE_DIRECTOR_PROVIDER = "deterministic"
.\.venv\Scripts\python.exe -m uvicorn vybe.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs for the OpenAPI explorer.

## Local Ollama Match Director

Ask the Match supports optional Ollama-based tool selection through a locally running Ollama server.

The model selects from allowlisted, read-only tools. The deterministic synthetic match engine provides verified facts and evidence.

Configure the API terminal:

```powershell
$env:VYBE_DIRECTOR_PROVIDER = "ollama"
$env:VYBE_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:VYBE_OLLAMA_MODEL = "qwen3-coder:30b"
```

Start Ollama and ensure the configured model is available before starting FastAPI.

The default provider is `foundry`. Use `deterministic` to disable model-based tool selection. Provider failures fall back to deterministic answers.

The Ollama adapter restricts configured endpoints to local loopback HTTP addresses.

## Endpoints

- `GET /health`: liveness check; does not verify provider readiness.
- `POST /v1/matches/replay?through_event=N`: deterministic match state after N events.
- `POST /v1/matches/replay/states`: all post-event states in one request (the frontend uses this to avoid rate-limit exhaustion).
- `POST /v1/matches/explain/{event_id}?persona=young|accessible|analyst`: grounded goal explanation.
- `POST /v1/matches/narrate/{event_id}?persona=young|accessible|analyst`: narration with optional Azure-assisted selection of strictly verified fact segments, with deterministic fallback.

- `POST /v1/matches/ask`: legacy deterministic, evidence-backed questions about the supplied synthetic match.
- `POST /v1/matches/director/ask`: Ask the Match model-directed allowlisted tool selection with deterministic fallback.
- `POST /v1/matches/insights`: grounded persona-specific match insights.
- `POST /v1/matches/speech`: Azure AI Speech MP3 when configured; browser speech is a frontend fallback.

All `/v1/matches/*` routes share a per-process ASGI-peer limit of **240 requests/minute** and a **256 KiB** request-body limit. `/v1/matches/director/ask`, `/v1/matches/narrate/*` and `/v1/matches/speech` additionally share a **30 requests/minute** bucket. These are not distributed per-user quotas or cost caps.

Replay, explain, narrate and insights accept a synthetic match definition directly. Ask accepts `{match, question}`; Director Ask accepts `{match, question, persona}` (persona defaults to analyst). Questions are 1–300 characters. Speech instead accepts `{text, language, rate}`: text 1–1200 characters, language en/ar/cs, rate 0.5–2 (default 1), returning MP3 when configured. The bulk replay excludes the initial pre-event state. The API also supports validated extra-time and penalty-shootout records; the public fixture does not demonstrate them.

The Director has three read-only data tools: `get_match_state`, `get_key_moments`, `get_match_statistics`. Specialized temporal and shootout questions may bypass the model. Unsupported causal claims are declined. Generation modes distinguish deterministic answers, Foundry-selected tools and Ollama-selected tools; `model_declined` records a model choosing no data tool, not necessarily a provider failure. Ollama does not generate goal narration or speech.

See [local development](../../docs/LOCAL_DEVELOPMENT.md) and [testing and security](../../docs/TESTING_AND_SECURITY.md). Do not use real match claims or disclose Azure secrets in code. The deterministic event engine remains the source of truth for scores and counts.

For optional model configuration see [Foundry launch notes](../../docs/archive/FOUNDRY_REQUIRED_LAUNCH.md); for owner-observed production evidence see [October 25 evidence pack](../../docs/archive/VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). See [project README](../../README.md) for frontend setup, personas and known limitations.

## Dependency lockfile compatibility

The runtime and test lockfiles were generated on Linux
with Python 3.11. Hash-enforced installation and API tests
were validated in Linux containers using Python 3.11 and
3.13.

Native Windows installation has not been independently
validated with these lockfiles.

If installation fails on Windows, use a compatible Linux
environment or the documented Docker setup. Do not
silently bypass package hash verification.

For entirely local execution, use a clean environment
without Azure model or speech credentials. Setting the
Director provider to deterministic does not independently
disable cloud narration or speech.

The local request guard tracks at most 1024 peers per
rate limiter dictionary by default. New peers may receive
HTTP 429 when capacity is exhausted. This is not a
distributed quota or measured production capacity.
