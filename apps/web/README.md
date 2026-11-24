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
Remove-Item Env:VITE_DEMO_MODE -ErrorAction SilentlyContinue
npm.cmd ci
npm.cmd run dev
```

Open the localhost URL printed by Vite (normally http://localhost:5173). The development proxy forwards `/v1` and `/health` to the API.

## Personas

- **Young Fan:** goal celebrations, football vocabulary, interactive goal quiz, friendly event explanations.
- **Accessible:** historical server-side Azure Speech with browser fallback in the full-stack mode, voice speeds, expanded shot/pass descriptions, contrast and font controls, keyboard shortcuts.
- **Analyst:** recorded event totals, half comparisons, weighted 15-minute momentum and goal-based turning points.

Keyboard shortcuts in Accessible mode, outside focused interactive controls: **Space** play/pause; **Left/Right** previous/next event. **Tab** navigates interactive elements. Voice availability varies by browser and operating system.

The match timeline defaults to highlights and can be switched to all events.

## Additional experiences

- Choose **English / العربية / Čeština** for localized event captions, match recap and optional browser speech. Browser voice installation and pronunciation vary.
- Toggle **Live captions** for event-based subtitles (not speech-to-text).
- The **Match story recap** is recalculated from played events.
- In Analyst mode, select a **momentum window** to filter timeline events; clear it to see the whole timeline.
- Persona, language, contrast, font-size, captions, timeline view, event details, expanded narration and speech speed persist locally in the browser when storage is available; blocked storage does not prevent playback.
- **Guided demo** cycles through three persona highlights automatically; stop it from the same control.

## Build

```powershell
npm.cmd run build
```

## Windows PowerShell: `npm.cmd` and `npx.cmd`

PowerShell may reject `npm` or `npx` with an error about `npm.ps1` / `npx.ps1` and the execution policy. In PowerShell, use the Windows `.cmd` entry points instead:

```powershell
npm.cmd ci
npm.cmd run dev
npm.cmd run build
npx.cmd playwright install chromium
npx.cmd playwright test
```

In Windows **CMD**, **Git Bash**, **Linux**, and **macOS**, use `npm` and `npx` without `.cmd` (for example, `npx playwright test`). You do **not** need to change the PowerShell execution policy or run as administrator. Playwright starts the Vite development server automatically when running tests. The automated spoken-commentary test mocks browser speech; it does not verify audible output.

## Static portfolio mode

The frontend supports a static portfolio build using pre-recorded synthetic match data, including replay states, persona-specific narrations, insights and five suggested Ask the Match questions.

The four JSON datasets contain 31 post-event snapshots, 12 goal narrations, three persona insight datasets and 15 question/persona entries. Questions must match the five English suggestions exactly after trimming whitespace. Ask the Match uses the complete fixture and may reveal future replay events. Language selection localizes event captions, recap and speech, not the entire interface or Ask the Match. Other questions receive a static-demo limitation response. No FastAPI backend, Ollama model, Foundry inference or Azure services are used in this mode.

```powershell
npm.cmd ci
$env:VITE_DEMO_MODE = "static"
npm.cmd run build
npm.cmd run preview
```

The production base path is `/vybe-ai/`, matching the GitHub Pages repository path.

Do not describe this mode as a live AI experience.

## Test separation

The normal Playwright configuration excludes `fullstack.spec.ts`; the separate full-stack configuration requires a running FastAPI service. See [testing and security](../../docs/TESTING_AND_SECURITY.md) and [local development](../../docs/LOCAL_DEVELOPMENT.md).

## Important caveats

The match is synthetic. Momentum is weighted event activity, not xG or possession. The original Azure Container Apps deployment has been retired; the current public portfolio is a frontend-only static GitHub Pages build. The owner supplied October 25 production responses reporting Foundry tool selection and Azure AI narration, and reported Evelyn Arabic speech acceptance. These observations are not independent Azure inference logs or a full accessibility certification. See [evidence](../../docs/archive/VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md).
