# VYBE API — First Working Slice

Python 3.11+ required.

```bash
cd apps/api
python -m venv .venv
# Activate your virtual environment
pip install -e ".[test]"
pytest -q
uvicorn vybe.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API.

- `GET /health` checks API readiness.
- `POST /v1/matches/replay` reconstructs deterministic match state from synthetic events.
- `POST /v1/matches/explain/{event_id}?persona=young|accessible|analyst` produces a fact-grounded goal explanation.

This slice intentionally uses **templates, not a live LLM**. It establishes an auditable factual baseline before AI integration. No real match data is used.
