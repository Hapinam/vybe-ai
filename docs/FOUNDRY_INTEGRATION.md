# VYBE: grounded Azure OpenAI-compatible narration

The match replay engine and score are deterministic. Azure AI narration has a safe fallback when not configured or unavailable. The application is deployed to Azure Container Apps, but deployment alone does not prove a model call. Owner-observed production response evidence from October 25 is in [the evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md); independent Azure inference traces remain unverified.

## Integration

`POST /v1/matches/narrate/{event_id}?persona=young|accessible|analyst` returns verified synthetic-event narration. Without Azure configuration, or if the model returns an invalid/filtered response, it returns deterministic narration.

Configuration (only with separate owner approval for costs and live service):
- `VYBE_AZURE_OPENAI_ENDPOINT`: HTTPS resource root such as `https://your-resource.openai.azure.com`
- `VYBE_AZURE_OPENAI_DEPLOYMENT`: model deployment name
- `VYBE_AZURE_OPENAI_KEY`: secret; never place in source control, frontend assets or logs

The adapter calls the Azure OpenAI chat-completions REST API. It is **not** a general Foundry agent or Microsoft Agent Framework integration. Not every Foundry project endpoint is compatible.

## Current safety boundary

The server prepares a minimal, trusted bundle of goal, score and synthetic-context fact sentences. The model may choose and order 1–3 exact fact segments and use optional persona-specific, allowlisted opening/closing phrases. The server checks the complete JSON schema, duplicate keys, response size, required goal and score facts, fact IDs, verbatim text equality and persona framing. Unverified output is rejected and deterministic narration used instead.

The model **cannot** freely invent football commentary. Player names and tactical explanations are not in the model's current fact bundle. See [AI grounding](AI_GROUNDING.md) for precise limitations.

## Deployment boundary

The legacy `infra/azure/deploy.sh` is not the current production update path. The deployed app is updated via GitHub Actions, private GHCR and Azure Container Apps; secrets are provisioned separately and must remain server-side. For local smoke tests, run `pytest -q` in `apps/api`. Do not present owner-observed API modes as independent Azure resource logs.
