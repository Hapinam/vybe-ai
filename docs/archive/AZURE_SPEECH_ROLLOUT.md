# Azure AI Speech in VYBE

> **ARCHIVED — HISTORICAL REFERENCE ONLY (November 2026)**
>
> This document describes the original VYBE hackathon implementation, validation, planning, or submission. It is not an active deployment or testing instruction. The Azure deployment has been retired; the current public portfolio is a static GitHub Pages demonstration. See the [current README](../../README.md) and [architecture](../ARCHITECTURE.md).

VYBE uses Azure AI Speech for server-side spoken commentary, with browser SpeechSynthesis as a fallback when server audio is unavailable.

## Current implementation

- The FastAPI endpoint `POST /v1/matches/speech` provides server-side speech synthesis.
- Accessible Fan supports English, Arabic and Czech commentary and captions.
- Speech reads the supplied event-grounded text; it does not generate football facts or translate a live match.
- The application keeps text available when audio is unavailable.

## Observed production result

On October 25, 2026, the owner reported successful **Evelyn Arabic** speech playback in production and on **iPhone Safari**, supported by a screen recording. This is a specific observed playback result, not a claim about every device or browser.

See [the judges' guide](JUDGES_TESTING_GUIDE.md) and [production evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). No new rollout or approval steps are required for the submitted demo.
