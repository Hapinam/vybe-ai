"""Read-only, evidence-grounded tool registry for the future Foundry Match Director.

These functions perform no network requests and never execute model-provided code.
A future agent adapter must dispatch only through call_director_tool().
"""
from collections import Counter

from .engine import replay, replay_timeline
from .models import EventType, MatchDefinition

TOOL_NAMES = ("get_match_state", "get_key_moments", "get_match_statistics")


def _ordered(match: MatchDefinition):
    return sorted(match.events, key=lambda e: (e.minute, e.second))


def get_match_state(match: MatchDefinition) -> dict:
    """Return the recorded state; never label it final without a fulltime marker."""
    state = replay(match)
    fulltime = any(e.type == EventType.fulltime for e in match.events)
    return {
        "match_id": match.match_id,
        "home_team": match.home_team,
        "away_team": match.away_team,
        "score": {"home": state.home_score, "away": state.away_score},
        "events_processed": state.events_processed,
        "fulltime_confirmed": fulltime,
        "evidence_event_ids": [e.id for e in _ordered(match) if e.type in (EventType.goal, EventType.fulltime)],
        "synthetic": True,
    }


def get_key_moments(match: MatchDefinition) -> dict:
    """Describe score changes, without inventing tactical causes."""
    home = away = 0
    moments = []
    for event in _ordered(match):
        if event.type != EventType.goal:
            continue
        before = (home, away)
        if event.team == match.home_team:
            home += 1
        else:
            away += 1
        after = (home, away)
        prior_leader = (before[0] > before[1]) - (before[0] < before[1])
        next_leader = (after[0] > after[1]) - (after[0] < after[1])
        if next_leader == 0:
            impact = "equalizer"
        elif prior_leader == 0:
            impact = "took_lead"
        elif prior_leader != next_leader:
            impact = "lead_changed"
        else:
            impact = "extended_lead"
        moments.append({
            "event_id": event.id, "minute": event.minute, "second": event.second,
            "team": event.team, "player": event.player, "impact": impact,
            "score_after": {"home": home, "away": away},
            "evidence_event_ids": [event.id],
        })
    return {"moments": moments, "synthetic": True, "tactical_causation_supported": False}


def get_match_statistics(match: MatchDefinition) -> dict:
    """Compute recorded event counts; never infer possession or expected goals."""
    state = replay(match)
    counts = Counter(e.type.value for e in match.events)
    return {
        "home_team": match.home_team, "away_team": match.away_team,
        "shots": {"home": state.shots_home, "away": state.shots_away},
        "completed_passes": {"home": state.passes_home, "away": state.passes_away},
        "recorded_event_counts": dict(sorted(counts.items())),
        "evidence_event_ids": [e.id for e in _ordered(match) if e.type in (EventType.goal, EventType.shot, EventType.pass_completed)],
        "limitations": "Recorded synthetic events only; no possession, xG, or tactical causation.",
        "synthetic": True,
    }


_DISPATCH = {
    "get_match_state": get_match_state,
    "get_key_moments": get_key_moments,
    "get_match_statistics": get_match_statistics,
}


def call_director_tool(name: str, match: MatchDefinition) -> dict:
    """Allowlist-only dispatch. Caller-supplied match must already be validated."""
    if name not in _DISPATCH:
        raise ValueError("Unsupported director tool")
    return _DISPATCH[name](match)
