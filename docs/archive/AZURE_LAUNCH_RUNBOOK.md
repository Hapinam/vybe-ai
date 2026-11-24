# VYBE — live demo runbook

> **ARCHIVED — HISTORICAL REFERENCE ONLY (November 2026)**
>
> This document describes the original VYBE hackathon implementation, validation, planning, or submission. It is not an active deployment or testing instruction. The Azure deployment has been retired; the current public portfolio is a static GitHub Pages demonstration. See the [current README](../../README.md) and [architecture](../ARCHITECTURE.md).

## Judge-facing links

- [Former live application (retired)](https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io)
- [Final 75-second video](https://youtu.be/-pfgaeGjSN8)
- [Judges' guide](JUDGES_TESTING_GUIDE.md)

## Demo flow

1. Introduce the fictional Aurora FC vs Harbor United match and the three fan experiences.
2. Show a goal in **Young Fan** mode.
3. Switch to **Accessible Fan** to show captions, readable controls and spoken commentary.
4. Switch to **Analyst Fan** to show event-grounded statistics and timeline.
5. Use **Ask the Match** to demonstrate bounded, evidence-backed model tool selection.

The app does not consume live Premier League data. Its deterministic replay engine remains authoritative for the score and events.

## Deployment note

The existing production release uses GitHub Actions, private GHCR and Azure Container Apps. **A merge into `main` can deploy to production even when only documentation changes.** Leave the production release unchanged during judging unless the owner explicitly authorizes it.

See [architecture](../ARCHITECTURE.md) and [production Foundry evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md).

**Current policy (24 November 2026):** Azure deployment is manual-only and operationally disabled. GHCR publishing is separate and excludes documentation-only changes. Historical deployment instructions are not authorized for execution.
