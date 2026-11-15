"""Grounded, deterministic question answering over a caller-supplied synthetic match.

No LLM or external provider is called. Unsupported questions are declined.
"""
import re

from .engine import replay
from .models import EventType, MatchDefinition
from .shootout import evaluate_shootout


_HALFTIME_TERMS = ("half time score", "halftime score", "score at half time", "score at halftime")
_FINAL_WINDOW_TERMS = ("last 15 minutes", "final 15 minutes")


def _normalized_question(question: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", question.casefold()).split())



_HISTORICAL_TIME_PATTERNS = (
    re.compile(r"\b(?:at|in) minute (\d{1,3})\b"),
    re.compile(r"\bafter (\d{1,3}) minutes?\b"),
    re.compile(r"\bat (\d{1,3}) (\d{2})\b"),
)



def _has_explicit_historical_time(question: str) -> bool:
    """Detect explicit time requests before punctuation normalization."""
    q = question.casefold()
    return bool(re.search(
        r"\b(?:at|in)\s+minute\s+-?\d+\b"
        r"|\bafter\s+-?\d+\s+minutes?\b"
        r"|\bat\s+\d+:\d+\b",
        q,
    ))



def _historical_time(question: str):
    if re.search(
        r"\b(?:at|in)\s+minute\s+-\d+\b"
        r"|\bafter\s+-\d+\s+minutes?\b",
        question.casefold(),
    ):
        return None

    q = _normalized_question(question)
    for pattern in _HISTORICAL_TIME_PATTERNS:
        match = pattern.search(q)
        if match:
            minute = int(match.group(1))
            second = int(match.group(2)) if len(match.groups()) > 1 else 0
            if minute > 130 or second > 59:
                return None
            return minute, second
    return None


def _is_historical_question(question: str) -> bool:
    q = _normalized_question(question)
    return (
        _historical_time(question) is not None
        and ("score" in q or "leading" in q)
    )



def is_shootout_question(question: str) -> bool:
    """Distinguish shootout questions from match-time penalties."""
    q = _normalized_question(question)

    if re.search(r"\bshoot\s*out\b", q):
        return True

    match_time_context = (
        "first half",
        "second half",
        "regular time",
        "normal time",
        "during the match",
        "during the game",
        "extra time",
        "stoppage time",
        "injury time",
    )

    if any(phrase in q for phrase in match_time_context):
        return False

    if re.search(r"\b(?:at|in|during)\s+minute\s+\d+\b", q):
        return False

    if re.search(r"\bpenalties\b", q):
        return True

    return re.search(r"\bpenalty\s+kicks?\s+\d+\b", q) is not None



def is_regular_penalty_question(question: str) -> bool:
    """Identify penalty questions not explicitly about a shootout."""
    q = _normalized_question(question)

    if is_shootout_question(question):
        return False

    return re.search(r"\bpenalt(?:y|ies)\b", q) is not None


def is_temporal_question(question: str) -> bool:
    """Recognize time-scoped questions that require evidence from a specific window."""
    q = _normalized_question(question)
    return (
        any(term in q for term in (*_HALFTIME_TERMS, *_FINAL_WINDOW_TERMS))
        or _is_historical_question(question)
    )


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

    if is_regular_penalty_question(question):
        return result(
            "The recorded match events do not establish "
            "whether a goal came from a penalty kick.",
            supported=False,
        )

    if is_shootout_question(question):
        kick_match = re.search(
            r"\bpenalty\s+kick\s+(\d+)\b",
            question.casefold(),
        )

        if kick_match:
            requested_order = int(kick_match.group(1))
            kick = next(
                (
                    item for item in match.penalty_shootout
                    if item.order == requested_order
                ),
                None,
            )

            if kick is None:
                return result(
                    f"Penalty kick {requested_order} is not recorded.",
                    supported=False,
                )

            return result(
                f"Penalty kick {requested_order}: "
                f"{kick.team}, {kick.outcome.value}.",
                [kick],
            )

        if (
            re.search(r"\bhow many\b", q)
            and re.search(r"\bsaved\b", q)
        ):
            saved_kicks = sorted(
                (
                    kick for kick in match.penalty_shootout
                    if kick.outcome.value == "saved"
                ),
                key=lambda kick: kick.order,
            )
            shootout = evaluate_shootout(match)
            completed = shootout.status == "completed"

            answer = (
                f"{len(saved_kicks)} penalty shootout kicks were saved."
                if completed
                else (
                    f"{len(saved_kicks)} penalty shootout kicks were saved so far. "
                    "The shootout is still in progress."
                )
            )

            return result(
                answer,
                saved_kicks,
                supported=completed,
            )

        if not match.penalty_shootout:
            return result(
                "No penalty shootout kicks are recorded.",
                supported=False,
            )

        shootout = evaluate_shootout(match)
        ordered_kicks = sorted(
            match.penalty_shootout,
            key=lambda kick: kick.order,
        )

        if shootout.status != "completed":
            return result(
                f"Recorded penalty shootout score: "
                f"{match.home_team} {shootout.home_score}–"
                f"{shootout.away_score} {match.away_team}. "
                "The shootout winner is not yet established.",
                ordered_kicks,
                supported=False,
            )

        return result(
            f"{shootout.winner} won the penalty shootout. "
            f"Penalty shootout score: "
            f"{match.home_team} {shootout.home_score}–"
            f"{shootout.away_score} {match.away_team}.",
            ordered_kicks,
        )

    if (
        _has_explicit_historical_time(question)
        and ("score" in q or "leading" in q)
        and not _is_historical_question(question)
    ):
        return result(
            "The requested match time is invalid or unsupported.",
            supported=False,
        )

    if _is_historical_question(question):
        minute, second = _historical_time(question)
        cutoff = minute * 60 + second
        earlier_goals = [
            e for e in goals
            if e.minute * 60 + e.second <= cutoff
        ]
        home = sum(e.team == match.home_team for e in earlier_goals)
        away = sum(e.team == match.away_team for e in earlier_goals)
        score = f"{match.home_team} {home}\u2013{away} {match.away_team}"

        if "leading" in q:
            if home > away:
                answer = f"{match.home_team} was leading at {minute}:{second:02d}. Score: {score}."
            elif away > home:
                answer = f"{match.away_team} was leading at {minute}:{second:02d}. Score: {score}."
            else:
                answer = f"The match was tied at {minute}:{second:02d}. Score: {score}."
        else:
            answer = f"Recorded score at {minute}:{second:02d}: {score}."

        return result(answer, earlier_goals)

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
