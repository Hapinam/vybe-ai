"""Regression tests for invalid historical time expressions."""

import pytest

from vybe.models import MatchDefinition
from vybe.questions import ask_match


MATCH = MatchDefinition.model_validate({
    "match_id": "invalid-historical-time",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


@pytest.mark.parametrize("question", [
    "What was the score at minute -1?",
    "What was the score at minute 150?",
    "What was the score at 10:75?",
])
def test_invalid_historical_time_is_unsupported(question):
    result = ask_match(MATCH, question)

    assert result["supported"] is False
    assert result["evidence_event_ids"] == []
    assert result["generation_mode"] == "deterministic"
