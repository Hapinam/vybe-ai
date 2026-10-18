# Ask the Match — evidence-grounded API prototype

This is a **backend-only**, deterministic question-answering endpoint. It is **not** an AI agent or live LLM integration and is not yet connected to the React UI. It accepts any valid synthetic match fixture using the existing MatchDefinition schema.

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

The API does not invoke Azure or consume model tokens. The existing per-process request guard applies, but does not constitute a distributed rate or cost quota. Follow-up work would need UI integration and a separately reviewed, tool-grounded LLM design before describing this as agentic AI.
