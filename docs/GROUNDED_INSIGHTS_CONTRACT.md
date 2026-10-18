# PR 3 — Evidence-grounded insights and Ask the Match

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

This PR does **not** introduce a free-form generative recap, Microsoft Foundry managed Agent Service, or UI wiring. The new endpoint is ready for the upcoming Broadcast Studio/AI Personalization UI PR. The model tool-selection integration is still not live-verified. No Azure resource or paid API call is created by this PR.

## Review checklist

- CI backend tests green.
- Confirm three personas share scores and evidence IDs, including equalizer and incomplete-match cases.
- Confirm causal questions do not call a model and remain unsupported.
- Verify existing Ask endpoint and current frontend behavior are unchanged.
