# VYBE AI Grounding — PR #7

## Why the previous check was insufficient

Checking that generated prose contains a team name and both score digits does not prove that other statements are true. A response can mention the correct score and also invent a cross, penalty, injury, xG, or tactical cause.

## Conservative design

The Azure model is allowed to choose **only a commentary style** from a persona-specific allowlist. It returns a JSON object with the exact key `style`. The backend validates the schema and then renders all match facts itself from the deterministic match engine.

- Young: `excited` or `friendly`
- Accessible: `clear` or `calm`
- Analyst: `concise` or `neutral`

Unrecognized or malformed responses fall back to deterministic narration. The model cannot add arbitrary factual statements to the fan-facing text.

## Honest limitations

This is **AI-assisted style selection**, not open-ended generative football analysis, a multi-agent system, or a complete Foundry agent. The UI's `azure_ai` label indicates the model selected a style, **not** that it authored the factual commentary. Additional work is needed for meaningful agentic reasoning with independently verified structured claims.

The demo remains synthetic. No Azure credentials are required for local development or CI. Do not commit keys or provision paid resources without approval.

## Test

```bash
cd apps/api
pip install -e ".[test]"
pytest -q
```
