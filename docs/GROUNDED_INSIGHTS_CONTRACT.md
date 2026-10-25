# PR 3 — Evidence-grounded insights and Ask the Match

> **Document status (October 25, 2026):** This file preserves historical planning, review, or test steps. Its older statements about future Azure deployment, unmerged features, or pending Foundry production tests are snapshots, **not current deployment status**. The deployed system and setup are described in [Architecture](ARCHITECTURE.md), [root README](../README.md), and [owner-observed production evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md). The final demo was uploaded to https://youtu.be/-pfgaeGjSN8. A passed CI job does not independently verify all Azure services, WCAG, cost, or browser audio.


## New endpoint

`POST /v1/matches/insights?persona=young|accessible|analyst` accepts the same validated synthetic match JSON as the replay endpoints.

Response includes:
- `recap` and `recap_evidence_event_ids`: a persona-specific, deterministic recap of the **recorded** score and goals;
- `insights[]`: one card per recorded goal, with `event_id`, `headline`, `explanation`, `impact`, `score_after`, and `evidence_event_ids`;
- `fulltime_confirmed`, `synthetic=true`, and `generation_mode=deterministic`.

All claims come from the server-side validated event stream. A goal's `impact` means **scoreboard impact only**; it does not imply momentum, tactics, xG, possession or real match coverage. The three personas change language, not facts.

## Agentic Ask safety update

`/v1/matches/director/ask` continues to use the optional Foundry-hosted model to choose one of three allowlisted read-only tools. Explicit tactical/causal questions are now declined *before* any model call, so a tool selection cannot turn an unsupported causal question into an apparently supported answer. For all other questions the answer text remains deterministic from the selected tool output, and returns its event evidence IDs.

## What this PR does not do

This PR did **not** introduce a free-form generative recap or Microsoft Foundry managed Agent Service. **The Broadcast Studio and Ask the Match UI are now wired in the deployed application.** The owner supplied production API response evidence on October 25; independent Azure inference logs remain unverified. No Azure resource or paid API call is created by this PR.

## Review checklist

- CI backend tests green.
- Confirm three personas share scores and evidence IDs, including equalizer and incomplete-match cases.
- Confirm causal questions do not call a model and remain unsupported.
- Verify existing Ask endpoint and current frontend behavior are unchanged.
