# VYBE AI Grounding — Current implementation

## Verified facts first

Match scores and event data come from the deterministic replay engine. Optional Azure OpenAI narration never calculates scores or supplies new match facts. The backend builds a small set of server-authored, evidence-backed sentences (goal, score, synthetic context).

## What the model can actually do

The model returns JSON with **1–3 segments**, each containing `fact_id` and `text`. It can select and order facts for the requested persona. Every selected text must match the corresponding server-authored sentence **verbatim**. Goal and score segments are mandatory. Persona-specific opening and closing are assembled from fixed, allowlisted phrases by the server; arbitrary model prose is not accepted.

The backend rejects duplicate JSON keys, unknown/repeated fact IDs, schema violations, oversized output, altered fact text and unapproved framing. Invalid, filtered, missing or unavailable Azure responses fall back to deterministic narration. Provider rejection is logged without exposing credentials.

The `azure_ai` generation mode means the model selected/ordered verified fact segments, possibly with approved framing. It **does not** mean free-form generative analysis or agentic reasoning.

## Limitations

The supplied fact bundle does not currently include player names or tactical context. This is fictional synthetic data, not an official match feed. Azure integration uses separately configured server-side credentials in the existing Azure Container App; the legacy provisioning script does not deploy a model. Owner-observed production responses are preserved in [the October 25 evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md), without independent Azure inference trace confirmation. No Azure account or key is required for local development or CI.

## Tests

```bash
cd apps/api
pip install -e ".[test]"
pytest -q
```
