# VYBE: optional Azure OpenAI narration

The match replay engine and score are deterministic. Azure AI is **optional**, and the planned Azure Container Apps deployment does **not** automatically provision or configure an Azure OpenAI model.

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

The current `infra/azure/deploy.sh` does not configure Azure OpenAI credentials or deploy a model. Do not enable paid Azure AI or add secrets without explicit approval. For local smoke tests, run `pytest -q` in `apps/api`. Do not claim live Azure AI operation until it is separately verified.
