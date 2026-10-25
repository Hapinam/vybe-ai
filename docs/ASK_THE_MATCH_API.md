# Ask the Match — deterministic legacy endpoint and model-directed UI

The **legacy** `POST /v1/matches/ask` endpoint is deterministic and remains available. The **current React Ask the Match UI** uses `POST /v1/matches/director/ask`, which can invoke a Foundry-hosted Azure OpenAI-compatible model to select an allowlisted read-only tool. Valid model responses are evidence-grounded; unavailable or invalid model results fall back safely. This is model tool calling, **not** managed Foundry Agent Service. Both paths use synthetic match facts.

POST `/v1/matches/ask`

```json
{
  "question": "Who scored?",
  "match": {
    "match_id": "demo",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
      {"id": "g1", "minute": 12, "team": "Aurora", "player": "Alex", "type": "goal"}
    ]
  }
}
```

Responses include `answer`, `supported`, `synthetic`, `generation_mode` and `evidence_event_ids`. Supported questions: goal scorers, halftime score (requires a halftime marker), final score (requires fulltime marker), recorded events in the final 15 minutes (requires fulltime marker). Questions about causes and momentum are declined with a definition of the indicator; unsupported requests are not guessed.

**The legacy `/v1/matches/ask` endpoint** does not invoke Azure or consume model tokens. **The current `/v1/matches/director/ask` endpoint can consume model tokens** when configured. The per-process request guard is not a distributed rate or cost quota. Owner-observed production evidence from October 25 is in [the evidence pack](VYBE_FOUNDRY_LIVE_EVIDENCE_2026-10-25.md); independent Azure-side inference traces remain unverified.
