# Microsoft Foundry — implemented integration

Microsoft Foundry integration is part of the VYBE hackathon demo. This document explains what was built, rather than defining pending launch gates.

## What Foundry does

- **Ask the Match:** The backend permits the model to choose from a bounded set of read-only match-data tools. Server-side validation constrains the answer to verified synthetic events.
- **Goal narration:** The model assists with selection and ordering of verified fact segments. The deterministic match engine remains the source of truth.
- **Fallback:** When a model response is unavailable or invalid, deterministic responses keep the match experience usable.

VYBE uses a **Foundry-hosted Azure OpenAI-compatible model**, not a managed Foundry Agent Service agent.

## Production observation — October 25, 2026

The owner captured a production Ask the Match response with `generation_mode=foundry_model_tool_call` and `selected_tool=get_key_moments`, and a goal narration response with `generation_mode=azure_ai` and verified fact IDs. Azure Monitor also showed **53.27k Processed Inference Tokens** at the resource level; this supports activity on the resource but is not a request-level trace.

See [the dated evidence](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md) and [architecture](ARCHITECTURE.md).

These observations are presented with their limits; no additional outage simulation, certification or submission approval is claimed or requested here.
