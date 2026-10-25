# PR 4 — Broadcast Studio Mode and AI Personalization

> **Document status (October 25, 2026):** This file preserves historical planning, review, or test steps. Its older statements about future Azure deployment, unmerged features, or pending Foundry production tests are snapshots, **not current deployment status**. The deployed system and setup are described in [Architecture](ARCHITECTURE.md), [root README](../README.md), and [owner-observed production evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). The final demo was uploaded to https://youtu.be/-pfgaeGjSN8. A passed CI job does not independently verify all Azure services, WCAG, cost, or browser audio.


## UI changes

- New Broadcast Studio section driven by `POST /v1/matches/insights?persona=...`.
- Audience switcher reuses the page's Young, Accessible and Analyst selection; the selected audience changes the presentation, not the verified match facts.
- Director picks show only goals already reached in playback. Selecting an evidence event jumps the existing match replay to that event.
- The full-fixture recap is explicitly labeled as including events beyond the current replay position.
- Ask the Match now uses `/v1/matches/director/ask` and shows whether the response was deterministic or model-selected. **No live model is implied when unconfigured.**
- All existing replay controls, accessible voice options and deterministic narration remain available.

## Test and manual review gates

1. Run `cd apps/web && npm ci && npm run build && npx playwright test`.
2. Run `cd apps/api && python -m pytest tests -q`.
3. Play to a goal; Studio should reveal the goal, scoreboard impact and a clickable event evidence ID.
4. Switch personas. Scores/evidence should not change, while narrative wording changes.
5. Click evidence. Replay should jump to the event without triggering audio unexpectedly.
6. Verify keyboard Tab, visible focus, screen-reader labels, narrow viewport and Accessible high-contrast/large-text behavior.
7. Test Ask without Foundry configuration: it must clearly show deterministic fallback.
8. Do not claim Foundry Agent Service or cloud integration as verified until a real approved Azure test succeeds.

**Cost:** no paid Azure resources, API keys or provisioning are included in this PR.
