# VYBE: optional Azure AI commentary

The match engine and score are deterministic. AI never computes the match state.

## Integration
The `/v1/matches/narrate/{event_id}` endpoint provides an optional Azure OpenAI-compatible model call. Without configuration it returns the existing deterministic explanation. It is not yet a multi-agent workflow or Microsoft Agent Framework implementation.

## Configuration (only after Azure access and costs are approved)
- `VYBE_AZURE_OPENAI_ENDPOINT`: HTTPS Azure OpenAI resource endpoint, e.g. `https://your-resource.openai.azure.com`
- `VYBE_AZURE_OPENAI_DEPLOYMENT`: model deployment name
- `VYBE_AZURE_OPENAI_KEY`: secret; never commit this value

This adapter uses the Azure OpenAI deployment REST API and may require a compatible model deployment and permissions. Microsoft Foundry projects may use different endpoints; this implementation does not yet support every Foundry project endpoint.

## Safety boundaries
The system sends a minimal synthetic event fact bundle and asks for grounded commentary. A basic response check rejects outputs missing the team or score; **this is not a complete hallucination validator**. Before using generated text in judging, add stronger structured-output verification against an explicit allowlist of facts, evaluation tests, content safety review, and a clear generation badge in the UI.

Never put keys in GitHub, frontend bundles or screenshots. Prefer managed identity in a later production implementation. The demo does not use real Premier League feeds, footage or statistics.

## Local smoke test
```bash
cd apps/api
pip install -e ".[test]"
pytest -q
```
