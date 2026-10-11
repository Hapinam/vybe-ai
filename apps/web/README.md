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

- **Young Fan:** goal celebrations, football vocabulary, interactive goal quiz, friendly event explanations.
- **Accessible:** optional browser speech synthesis, voice speeds, expanded shot/pass descriptions, contrast and font controls, keyboard shortcuts.
- **Analyst:** recorded event totals, half comparisons, weighted 15-minute momentum and goal-based turning points.

Keyboard shortcuts in Accessible mode, outside focused interactive controls: **Space** play/pause; **Left/Right** previous/next event. **Tab** navigates interactive elements. Voice availability varies by browser and operating system.

The match timeline defaults to highlights and can be switched to all events.

## Additional experiences

- Choose **English / العربية / Čeština** for localized event captions, match recap and optional browser speech. Browser voice installation and pronunciation vary.
- Toggle **Live captions** for event-based subtitles (not speech-to-text).
- The **Match story recap** is recalculated from played events.
- In Analyst mode, select a **momentum window** to filter timeline events; clear it to see the whole timeline.
- Persona, language, contrast and font-size preferences persist locally in the browser.
- **Guided demo** cycles through three persona highlights automatically; stop it from the same control.

## Build

```powershell
npm run build
```

## Important caveats

The match is synthetic. Momentum is weighted event activity, not xG or possession. Azure integration is optional and is not proof of a live deployed service. The final browser and accessibility acceptance test is still pending.
