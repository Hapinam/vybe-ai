# VYBE Web Dashboard

React + TypeScript + Vite frontend for the fictional Aurora FC vs Harbor United replay. See the [project README](../../README.md) for complete setup and demo guidance.

## Start locally

From the repository root, start FastAPI in one terminal:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m uvicorn vybe.main:app --reload --port 8000
```

Start Vite in a second terminal:

```powershell
cd apps/web
npm install
npm run dev
```

Open the localhost URL printed by Vite (normally http://localhost:5173). The development proxy forwards `/v1` and `/health` to the API.

## Personas

- **Young Fan:** goal celebrations, football vocabulary, friendly event explanations.
- **Accessible:** optional browser speech synthesis, voice speeds, expanded shot/pass descriptions, contrast and font controls, keyboard shortcuts.
- **Analyst:** recorded event totals, half comparisons, weighted 15-minute momentum and goal-based turning points.

Keyboard shortcuts in Accessible mode, outside focused interactive controls: **Space** play/pause; **Left/Right** previous/next event. **Tab** navigates interactive elements. Voice availability varies by browser and operating system.

## Build

```powershell
npm run build
```

## Important caveats

The match is synthetic. Momentum is weighted event activity, not xG or possession. Azure integration is optional and is not proof of a live deployed service. The final browser and accessibility acceptance test is still pending.
