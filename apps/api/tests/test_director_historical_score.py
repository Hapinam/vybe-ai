"""Regression tests for historical match scores."""

import pytest

from vybe.models import MatchDefinition
from vybe.questions import ask_match


MATCH = MatchDefinition.model_validate({
    "match_id": "historical-score",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {"id": "kick", "minute": 0, "type": "kickoff"},
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


@pytest.mark.parametrize("question,expected,evidence", [
    ("What was the score at minute 5?", "Aurora 0–0 Harbor", []),
    ("What was the score at minute 30?", "Aurora 1–0 Harbor", ["g1"]),
    ("What was the score after 20 minutes?", "Aurora 1–0 Harbor", ["g1"]),
    ("Who was leading at 60:00?", "Aurora", ["g1"]),
    ("What was the score at minute 90?", "Aurora 1–1 Harbor", ["g1", "g2"]),
])
def test_historical_score(question, expected, evidence):
    result = ask_match(MATCH, question)

    assert result["supported"] is True
    assert expected in result["answer"]
    assert result["evidence_event_ids"] == evidence
    assert result["generation_mode"] == "deterministic"
