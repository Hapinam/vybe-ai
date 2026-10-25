# VYBE — production evidence (25 October 2026)

This page records owner-observed production behavior. It is not an independent Azure request-level audit.

**Application:** https://vybe-app.delightfulbay-c36e685e.germanynorth.azurecontainerapps.io

## Ask the Match

A production response reported:
- `generation_mode: foundry_model_tool_call`
- `selected_tool: get_key_moments`
- Verified evidence IDs for a synthetic match.

## Goal narration

For goal event `e2`, the production response reported:
- `generation_mode: azure_ai`
- `selected_fact_ids: ["context", "goal", "score"]`
- `evidence_event_ids: ["e2"]`
- Score: Aurora FC 1, Harbor United 0.

The response identified the match as fictional and avoided unsupported tactical claims.

## Azure-side corroboration

The owner inspected the dedicated `vybe-foundry` resource in Azure Monitor, which displayed **53.27k Processed Inference Tokens (Sum)**. This is **resource-level evidence**, not a trace linking a specific API request to an inference call.

## Speech and mobile

The owner reported successful production playback using **Azure Speech Evelyn Arabic**, including **iPhone Safari** playback documented in a screen recording.

## What this evidence does not claim

- A managed Foundry Agent Service agent.
- Exhaustive coverage of all requests, browsers or failure scenarios.
- Formal accessibility or security certification.
- A live Premier League data feed.

**Final demo:** https://youtu.be/-pfgaeGjSN8
