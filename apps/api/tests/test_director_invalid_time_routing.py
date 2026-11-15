"""Prevent invalid historical time requests from reaching an LLM."""

from unittest.mock import patch

import pytest

from vybe.director_agent import director_ask
from vybe.models import MatchDefinition


MATCH = MatchDefinition.model_validate({
    "match_id": "invalid-provider-time",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


@pytest.mark.parametrize("provider", ["foundry", "ollama"])
@pytest.mark.parametrize("question", [
    "What was the score at minute -1?",
    "What was the score at minute 150?",
    "What was the score at 10:75?",
])
def test_invalid_time_never_reaches_provider(monkeypatch, provider, question):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    with patch("vybe.director_agent._select_tool") as foundry, patch(
        "vybe.director_ollama._select_tool"
    ) as ollama:
        result = director_ask(MATCH, question)

    assert result["supported"] is False
    assert result["evidence_event_ids"] == []
    assert result["selected_tool"] is None
    assert result["generation_mode"] == "deterministic"

    foundry.assert_not_called()
    ollama.assert_not_called()
