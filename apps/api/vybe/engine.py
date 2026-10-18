"""Deterministic match state and evidence-backed fan explanations."""

from dataclasses import dataclass, asdict, replace as dc_replace
from .models import EventType, MatchDefinition, MatchEvent


@dataclass
class MatchState:
    match_id: str
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    shots_home: int = 0
    shots_away: int = 0
    passes_home: int = 0
    passes_away: int = 0
    events_processed: int = 0


def _apply(state: MatchState, event: MatchEvent, home_team: str) -> None:
    """Apply one event without counting any action twice."""
    is_home = event.team == home_team
    if event.type == EventType.goal:
        if is_home:
            state.home_score += 1
        else:
            state.away_score += 1
    if event.type in (EventType.shot, EventType.goal):
        if is_home:
            state.shots_home += 1
        else:
            state.shots_away += 1
    if event.type == EventType.pass_completed:
        if is_home:
            state.passes_home += 1
        else:
            state.passes_away += 1
    state.events_processed += 1


def replay_timeline(match: MatchDefinition) -> list[MatchState]:
    """Snapshots 0..N in one sorted pass, equivalent to replay(match, i)."""
    state = MatchState(match_id=match.match_id, home_team=match.home_team, away_team=match.away_team)
    states = [dc_replace(state)]
    for event in sorted(match.events, key=lambda e: (e.minute, e.second)):
        _apply(state, event, match.home_team)
        states.append(dc_replace(state))
    return states


def replay(match: MatchDefinition, through_event: int | None = None) -> MatchState:
    """Reconstruct state from ordered events without mutating source data."""
    state = MatchState(match_id=match.match_id, home_team=match.home_team, away_team=match.away_team)
    events = sorted(match.events, key=lambda e: (e.minute, e.second))
    if through_event is not None:
        if through_event < 0:
            raise ValueError("through_event must be nonnegative")
        events = events[:through_event]
    for event in events:
        _apply(state, event, match.home_team)
    return state


def explain_goal(match: MatchDefinition, event_id: str, persona: str = "young") -> dict:
    """Use only observed facts; persona changes expression, never score."""
    if persona not in {"young", "accessible", "analyst"}:
        raise ValueError("unsupported persona")
    events = sorted(match.events, key=lambda e: (e.minute, e.second))
    target = next((event for event in events if event.id == event_id), None)
    if target is None or target.type != EventType.goal:
        raise ValueError("event_id must refer to a goal")
    index = next(i for i, event in enumerate(events) if event.id == event_id)
    state = replay(match, through_event=index + 1)
    score = f"{state.home_score}-{state.away_score}"
    when = f"{target.minute}:{target.second:02d}"
    if persona == "young":
        narrative = f"Goal! {target.team} scored at {when}. The score is now {score}. What a big moment!"
    elif persona == "accessible":
        narrative = f"Goal for {target.team} at minute {target.minute}, {target.second} seconds. Current score: {match.home_team} {state.home_score}, {match.away_team} {state.away_score}."
    else:
        narrative = f"Confirmed goal by {target.team} at {when}; match score is {score}. The available match data confirms the goal, but doesn't provide enough detail to explain how the chance was created."
    return {
        "event_id": target.id,
        "persona": persona,
        "narrative": narrative,
        "evidence_event_ids": [target.id],
        "score": {"home": state.home_score, "away": state.away_score},
        "synthetic": True,
    }


def state_dict(state: MatchState) -> dict:
    return asdict(state)
