# VYBE AI Grounding — Current implementation

## Verified facts first

Match scores and event data come from the deterministic replay engine. Optional Azure OpenAI narration never calculates scores or supplies new match facts. The backend builds a small set of server-authored, evidence-backed sentences (goal, score, synthetic context).

## What the model can actually do

The model returns JSON with **1–3 segments**, each containing `fact_id` and `text`. It can select and order facts for the requested persona. Every selected text must match the corresponding server-authored sentence **verbatim**. Goal and score segments are mandatory. Optional `opening` and `closing` must exactly match the persona's approved phrases; no arbitrary prose is accepted.

The backend rejects duplicate JSON keys, unknown/repeated fact IDs, schema violations, oversized output, altered fact text and unapproved framing. Invalid, filtered, missing or unavailable Azure responses fall back to deterministic narration. Provider rejection is logged without exposing credentials.

The `azure_ai` generation mode means the model selected/ordered verified fact segments, possibly with approved framing. It **does not** mean free-form generative analysis or agentic reasoning.

## Limitations

The supplied fact bundle does not currently include player names or tactical context. This is fictional synthetic data, not an official match feed. Azure integration is optional and is **not deployed by the current deployment script**. No Azure account or key is required for local development or CI.

## Tests

```bash
cd apps/api
pip install -e ".[test]"
pytest -q
```
