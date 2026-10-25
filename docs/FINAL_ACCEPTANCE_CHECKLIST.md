# VYBE — submission summary

This document summarizes the available submission artifacts. It is **not** an outstanding test checklist.

## Delivered

- A deployed VYBE demo with **Young Fan**, **Accessible Fan**, and **Analyst Fan**.
- A fictional, deterministic football match with evidence-backed scores and statistics.
- Server-side Microsoft Foundry model integration for bounded Ask the Match tool selection and grounded narration.
- Azure AI Speech with browser fallback.
- [Live application](https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io).
- [Final 75-second video](https://youtu.be/-pfgaeGjSN8).
- [Judges' guide](JUDGES_TESTING_GUIDE.md).

## Existing validation evidence

Earlier development records reported 24/24 manual acceptance checks, 54 API tests, four Playwright checks and successful frontend/container build checks. These are **historical results**, not newly executed tests or formal certifications.

On October 25, owner-observed production responses reported `foundry_model_tool_call` and `azure_ai` modes; the owner also reported Evelyn Arabic playback on iPhone Safari. See [the dated evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md).

## Scope

VYBE uses synthetic match data, not an official Premier League feed. It does not claim a managed Foundry Agent Service agent or independent verification of every upstream model call.
