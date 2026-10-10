"""HTTP API for synthetic match playback and grounded explanations."""

from fastapi import FastAPI, HTTPException, Query
from .models import MatchDefinition
from .engine import replay, explain_goal, state_dict

app = FastAPI(title="VYBE Synthetic Match API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "vybe-api"}


@app.post("/v1/matches/replay")
def replay_match(match: MatchDefinition, through_event: int | None = Query(default=None, ge=0)):
    return {"synthetic": True, "state": state_dict(replay(match, through_event))}


@app.post("/v1/matches/explain/{event_id}")
def explain_match_event(
    event_id: str,
    match: MatchDefinition,
    persona: str = Query(default="young"),
):
    try:
        return explain_goal(match, event_id, persona)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
