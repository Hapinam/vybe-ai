"""Deterministic, event-evidenced insights for three fan personas.

The model may select a tool elsewhere; match facts and narrative claims here
are exclusively derived from validated synthetic events.
"""
from .director_tools import get_key_moments, get_match_state, get_match_statistics
from .models import MatchDefinition

PERSONAS = ("young", "accessible", "analyst")
IMPACTS = {
    "equalizer": "levelled the recorded score",
    "took_lead": "put their team ahead",
    "lead_changed": "changed the recorded leader",
    "extended_lead": "increased their team's lead",
}


def match_insights(match: MatchDefinition, persona: str = "analyst") -> dict:
    if persona not in PERSONAS:
        raise ValueError("Unsupported persona")
    state = get_match_state(match)
    moments = get_key_moments(match)["moments"]
    stats = get_match_statistics(match)
    score = state["score"]
    status = "Final recorded score" if state["fulltime_confirmed"] else "Recorded score so far"
    score_text = f"{status}: {match.home_team} {score['home']}–{score['away']} {match.away_team}."
    cards = []
    for moment in moments:
        event_id = moment["event_id"]
        impact = IMPACTS[moment["impact"]]
        when = f"{moment['minute']}:{moment['second']:02d}"
        if persona == "young":
            headline = "Goal! What a moment!"
            detail = f"{moment['team']} scored at {when} and {impact}!"
        elif persona == "accessible":
            headline = f"Goal at {when}"
            detail = (f"Goal for {moment['team']} at minute {moment['minute']}, "
                      f"{moment['second']} seconds. This {impact}.")
        else:
            headline = f"Recorded goal: {moment['team']} at {when}"
            detail = (f"Score became {moment['score_after']['home']}–"
                      f"{moment['score_after']['away']}; this {impact}. "
                      "The events do not establish a tactical cause.")
        cards.append({
            "event_id": event_id, "headline": headline, "explanation": detail,
            "impact": moment["impact"], "score_after": moment["score_after"],
            "evidence_event_ids": [event_id], "synthetic": True,
        })
    if persona == "young":
        intro = f"Here's the story of the game! {score_text}"
    elif persona == "accessible":
        intro = f"Match recap. {score_text} {len(moments)} goals recorded."
    else:
        intro = (f"Event-grounded match recap. {score_text} "
                 f"Recorded shots: {stats['shots']['home']}–{stats['shots']['away']}. "
                 "No xG, possession or tactical causation is inferred.")
    return {
        "match_id": match.match_id, "persona": persona,
        "recap": intro, "recap_evidence_event_ids": state["evidence_event_ids"],
        "insights": cards, "score": score,
        "fulltime_confirmed": state["fulltime_confirmed"],
        "generation_mode": "deterministic", "synthetic": True,
        "limitations": "Fictional event feed; recorded facts only, not tactical causation.",
    }
