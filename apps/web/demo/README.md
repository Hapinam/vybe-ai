# VYBE automated demo recorder (draft)

This records the actual browser interface using Playwright's built-in video capture. It does **not** fabricate Azure AI behavior or mock backend responses.

## Prerequisites

- Node dependencies installed in `apps/web` and Playwright Chromium installed.
- FastAPI running locally at `http://127.0.0.1:8000` in a separate terminal.
- Port 5173 available (the recorder starts Vite itself).

From Windows CMD in `C:\Users\hapin\Codes\vybe-ai\apps\web`:

```cmd
npx.cmd playwright test --config=demo/playwright.demo.config.ts
```

The raw **WebM** browser recording is saved in `apps/web/demo-output/` under the test's output directory (look for `video.webm`). The script captures roughly 26–30 seconds of the live application and validates that the backend is responding. It does **not** capture speech/system audio. A narrated MP4 under two minutes requires a separate voice-over and editing/export pass; this is not the finished submission video.

## Draft narration / storyboard (English)

- **0–10s — The problem:** "Football is universal, but every fan experiences it differently. VYBE makes one match feel personal."
- **10–30s — Young Fan:** "For younger fans, we simplify the action with clear explanations, celebrations, and a football quiz."
- **30–55s — Accessible Fan:** "For fans who need more control, we offer captions, contrast options, readable text, and step-by-step navigation."
- **55–80s — Analyst:** "For analysts, VYBE reveals match momentum, turning points, and evidence tied to synthetic events."
- **80–105s — Grounded intelligence:** "A deterministic match engine preserves the score and facts. Narration uses validated evidence; Azure AI integration will only be described as live after deployment and verification."
- **105–110s — Closing:** "VYBE. Every fan belongs."

## Recording integrity

- The match is explicitly **synthetic**, not real Premier League data.
- The guided demo is a real UI feature and rotates Young Fan → Accessible → Analyst.
- If the backend is unavailable, the test fails instead of recording an apparently working demo.
- The recorder currently produces a **draft silent clip**, not a final narrated hackathon submission.
- Never present optional Azure integration as deployed before it is verified.
