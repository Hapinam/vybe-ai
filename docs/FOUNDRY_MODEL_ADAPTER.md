# Foundry-hosted model tool calling (PR 2)

This adapter is **not** a deployed Microsoft Foundry Agent Service agent. It uses an Azure OpenAI-compatible chat-completions model deployment, which may be managed through Microsoft Foundry. The model **selects one tool**, and VYBE executes only the allowlisted read-only tool; the final answer is rendered deterministically from verified tool data. The model does **not** generate free-form final text. This distinction matters for accurate hackathon claims.

## Endpoint

`POST /v1/matches/director/ask` accepts `{"match": <validated MatchDefinition>, "question": "...", "persona": "young|accessible|analyst"}`.

- Without configuration, it returns deterministic Ask the Match output and `generation_mode=deterministic`.
- With valid model configuration and a valid tool selection, it returns `generation_mode=foundry_model_tool_call`, `selected_tool` and `evidence_event_ids`.
- Invalid tool calls, invalid arguments, malformed model replies, network failures and timeouts fall back safely. No arbitrary tool URLs, dynamic code or model-provided match facts are executed.
- The existing `/v1/matches/ask` endpoint is unchanged.
- Tool calls are capped at **one per request** and model output is capped at 100 tokens, 8192 response bytes and 6 seconds network timeout. These limits are **not** a monetary spending cap.

## Optional server-side configuration

- `VYBE_FOUNDRY_MODEL_ENDPOINT`: HTTPS Azure OpenAI resource root, e.g. `https://YOUR-RESOURCE.openai.azure.com`
- `VYBE_FOUNDRY_MODEL_DEPLOYMENT`: approved model deployment name
- `VYBE_FOUNDRY_MODEL_KEY`: secret; never commit, log or expose in browser

These settings are **not** added to the Azure deployment script. No paid services are provisioned by this PR. Before live use, verify model compatibility with `tool_choice=required`, quota, price, Azure policy and deployment permissions. A real model call and managed Foundry Agent Service integration remain **unverified**.

## Next steps

PR 3 should integrate the agent response into Ask the Match and add a stronger evidence-grounded recap/insights contract. If the hackathon requires **managed Foundry Agent Service**, implement and validate that separately rather than describing this model tool-calling adapter as a managed agent.
