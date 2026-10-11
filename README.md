# VYBE — Every Fan Belongs

**One synthetic football match. Three ways to experience it.**

VYBE is an accessibility-first football replay prototype for the **Microsoft + Premier League Inside the Game Developer Hackathon 2026**. It presents the same fictional Aurora FC vs Harbor United match through different experiences, with grounded event data and an optional Azure AI narration integration.

> **Synthetic demo only:** Teams, players and match events are fictional. This project does not use official Premier League match feeds or claim real-time match coverage.

## Experiences

| Persona | Features |
| --- | --- |
| **Young Fan** | Goal celebration, plain-language football glossary, interactive goal quiz, approachable match commentary |
| **Accessible** | Optional browser spoken commentary, adjustable voice speed, high-contrast mode, larger text, keyboard replay shortcuts, optional descriptions of shots and passes |
| **Analyst** | Recorded shots/passes, highlights/full timeline filter, first-vs-second-half comparison, event-based momentum indicator, goal turning points and evidence-backed narratives |

**Interpreting analytics:** Momentum is a custom weighted event-activity score (goal = 3, shot = 2, completed pass = 1) in 15-minute windows. It is **not** possession, expected goals (xG), or a professional tactical model. Half comparisons use recorded synthetic events only; missing events must not be interpreted as real-world zero activity.

## Architecture

- **Frontend:** React, TypeScript, Vite, CSS; browser SpeechSynthesis API for optional spoken commentary.
- **Backend:** Python FastAPI; deterministic replay engine that calculates score, passes and shots from ordered synthetic events.
- **Narration:** Evidence-based, persona-specific commentary; optional Azure AI configuration where supported, with deterministic fallback.
- **Data:** Local synthetic match fixture. No external sports API required.

The Vite development server proxies `/v1` and `/health` to the FastAPI service on port **8000**.

## Run locally (Windows PowerShell)

Use two terminals from the repository root.

**Terminal 1 — API**

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m uvicorn vybe.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```powershell
cd apps/web
npm install
npm run dev
```

Open **http://localhost:5173** (or the port Vite prints if 5173 is occupied).

## Validation (planned final end-to-end pass)

```powershell
cd apps/web
npm run build
```

```powershell
cd apps/api
.\.venv\Scripts\python.exe -m pytest tests -q
```

Then check all three personas in the browser, play/restart/scrub, score and event progression, goal celebration, glossary, speech pause/resume and voice rates, keyboard shortcuts, high contrast and text scaling, analyst charts, mobile viewport, and reduced-motion preference. **Passing CI is not equivalent to passing this manual end-to-end check.**

## Accessible controls

In Accessible mode, **Tab** navigates controls. When focus is not inside an interactive control, **Space** toggles playback and **Left/Right arrows** step through events. Spoken commentary is optional and depends on the installed browser and operating-system voices. Voice-speed changes apply to the next utterance, not the current one.

## Azure readiness

The prototype can run locally without paid Azure resources. The Azure integration is **optional**, and cloud provisioning, credentials, costs, deployment and live service validation must be performed separately. Never commit secrets or Azure API keys. The UI distinguishes deterministic narration from Azure-assisted style selection when the backend reports that mode; do not interpret this as proof that a live Azure deployment is currently active.

## Limitations and responsible use

- Not real football match data, real-time video or an official Premier League product.
- AI-generated or AI-assisted descriptions are experimental; the deterministic event engine is the source of truth for match scores.
- Browser speech voices vary, and expanded narration needs manual timing/accessibility validation.
- Goal-based turning points are illustrative, not causal tactical analysis.
- This is a hackathon prototype; production readiness, WCAG compliance, security review and Azure integration are **not** yet certified.

## Project layout

- `apps/api/` — FastAPI routes, match engine and tests
- `apps/web/` — React replay dashboard and personas
- `apps/web/src/match.ts` — synthetic match fixture and frontend types

## Hackathon demo outline

1. Introduce the same fictional match and the three personas.
2. Play a goal in Young Fan mode; show the celebration and football word explanation.
3. Switch to Accessible; demonstrate high contrast, large text, keyboard navigation and optional narration.
4. Switch to Analyst; inspect half-by-half counts, weighted momentum and turning points.
5. Explain that all claims are grounded in synthetic events, and clearly separate optional Azure integration from verified live services.

**Every fan belongs. Every moment matters.**
