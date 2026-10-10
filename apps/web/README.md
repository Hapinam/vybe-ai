# VYBE Live Dashboard

An accessible React + TypeScript interface connected to the synthetic FastAPI match engine.

## Start the API

```bash
cd apps/api
python -m venv .venv
# Activate the virtual environment for your operating system
pip install -e ".[test]"
uvicorn vybe.main:app --reload
```

## Start the web app (second terminal)

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173.

The Vite development server proxies `/v1` and `/health` to FastAPI on port 8000, avoiding CORS issues during local development.

## Features
- Synthetic Aurora FC vs Harbor United match playback
- Score, timeline, recorded shots, passes and progress scrubber
- Young Fan, Accessible and Analyst evidence-backed commentary
- Optional browser speech synthesis in Accessible mode
- Keyboard-friendly controls, skip link, reduced-motion support, responsive layout

## Limitations
- No Microsoft Foundry or Azure deployment in this PR
- Commentary is deterministic templates, not generative AI
- Speech synthesis availability and voice quality depend on browser/OS
- This is a synthetic football simulation, not real Premier League data
