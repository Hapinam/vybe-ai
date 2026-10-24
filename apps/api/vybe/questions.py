"""Grounded, deterministic question answering over a caller-supplied synthetic match.

No LLM or external provider is called. Unsupported questions are declined.
"""
import re

from .engine import replay
from .models import EventType, MatchDefinition


_HALFTIME_TERMS = ("half time score", "halftime score", "score at half time", "score at halftime")
_FINAL_WINDOW_TERMS = ("last 15 minutes", "final 15 minutes")


def _normalized_question(question: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\\s]", " ", question.casefold()).split())


def is_temporal_question(question: str) -> bool:
    """Recognize time-scoped questions that require evidence from a specific window."""
    q = _normalized_question(question)
    return any(term in q for term in (*_HALFTIME_TERMS, *_FINAL_WINDOW_TERMS))


def ask_match(match: MatchDefinition, question: str) -> dict:
    q = _normalized_question(question)
    events = sorted(match.events, key=lambda e: (e.minute, e.second))
    goals = [e for e in events if e.type == EventType.goal]

    def result(answer: str, evidence=(), supported=True):
        return {
            "answer": answer,
            "evidence_event_ids": [e.id for e in evidence],
            "supported": supported,
            "generation_mode": "deterministic",
            "synthetic": True,
        }

    if any(term in q for term in ("who scored", "goal scorers", "goalscorers", "who scored the goals")):
        if not goals:
            return result("No goals are recorded in the supplied events.")
        parts = [
            f"{e.player or 'Unspecified player'} ({e.team}, {e.minute}:{e.second:02d})"
            for e in goals
        ]
        return result("Recorded goals: " + "; ".join(parts) + ".", goals)

    if any(term in q for term in ("half time score", "halftime score", "score at half time", "score at halftime")):
        half = next((e for e in events if e.type == EventType.halftime), None)
        if half is None:
            return result("A halftime marker is missing, so the halftime score cannot be confirmed.", supported=False)
        earlier = [e for e in events if (e.minute, e.second) <= (half.minute, half.second)]
        h = sum(e.type == EventType.goal and e.team == match.home_team for e in earlier)
        a = sum(e.type == EventType.goal and e.team == match.away_team for e in earlier)
        return result(f"At halftime: {match.home_team} {h}–{a} {match.away_team}.",
                      [e for e in earlier if e.type == EventType.goal] + [half])

    if any(term in q for term in ("final score", "full time score", "fulltime score", "what was the score")):
        if not any(e.type == EventType.fulltime for e in events):
            return result("The supplied events have no fulltime marker, so a final score cannot be confirmed.", supported=False)
        state = replay(match)
        return result(f"Final recorded score: {match.home_team} {state.home_score}–{state.away_score} {match.away_team}.",
                      goals + [e for e in events if e.type == EventType.fulltime])

    if any(term in q for term in ("last 15 minutes", "final 15 minutes")):
        fulltime = next((e for e in reversed(events) if e.type == EventType.fulltime), None)
        if fulltime is None:
            return result("The supplied events have no fulltime marker; the final 15 minutes cannot be established.", supported=False)
        end = fulltime.minute * 60 + fulltime.second
        recent = [e for e in events if end - 900 <= e.minute * 60 + e.second <= end]
        if not recent:
            return result("No events were recorded in the final 15 minutes.")
        counts = {}
        for e in recent:
            counts[e.type.value] = counts.get(e.type.value, 0) + 1
        summary = ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in sorted(counts.items()))
        return result(f"Recorded events in the final 15 minutes: {summary}.", recent)

    if re.search(r"\b(?:why|caus\w*|tactic\w*|strateg\w*|formation\w*|momentum)\b", q):
        return result(
            "The supplied events do not establish tactical causes. The momentum indicator is a weighted event-activity metric (goal=3, shot=2, completed pass=1), not xG or proof of causation.",
            supported=False,
        )

    return result("I cannot answer that question from the supported synthetic event facts.", supported=False)
