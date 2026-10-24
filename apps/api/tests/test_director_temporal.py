"""Regression tests: time-scoped answers must not be replaced by whole-match model tools."""
from unittest.mock import patch

import pytest

from vybe.director_agent import director_ask
from vybe.models import MatchDefinition
from vybe.questions import ask_match, is_temporal_question


MATCH = MatchDefinition.model_validate({
    "match_id": "temporal", "home_team": "Aurora FC", "away_team": "Harbor United",
    "events": [
        {"id": "kick", "minute": 0, "type": "kickoff"},
        {"id": "g1", "minute": 12, "team": "Aurora FC", "type": "goal"},
        {"id": "g2", "minute": 24, "team": "Harbor United", "type": "goal"},
        {"id": "half", "minute": 45, "type": "halftime"},
        {"id": "g3", "minute": 55, "team": "Harbor United", "type": "goal"},
        {"id": "late-pass", "minute": 80, "team": "Aurora FC", "type": "pass_completed"},
        {"id": "g4", "minute": 87, "team": "Aurora FC", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


@pytest.mark.parametrize("question,expected,evidence", [
    ("What was the halftime score?", "Aurora FC 1–1 Harbor United", ["g1", "g2", "half"]),
    ("What happened in the last 15 minutes?", "1 goal", ["late-pass", "g4", "end"]),
    ("Score at half-time?", "Aurora FC 1–1 Harbor United", ["g1", "g2", "half"]),
])
def test_temporal_questions_keep_precise_fallback_without_model(question, expected, evidence):
    with patch("vybe.director_agent._configuration") as config, patch(
        "vybe.director_agent._select_tool"
    ) as select_tool:
        result = director_ask(MATCH, question)
    config.assert_not_called()
    select_tool.assert_not_called()
    assert expected in result["answer"]
    assert result["evidence_event_ids"] == evidence
    assert result["selected_tool"] is None
    assert result["generation_mode"] == "deterministic"
    assert result["supported"] is True


def test_missing_halftime_marker_cannot_be_overridden_by_model():
    without_half = MatchDefinition.model_validate({
        **MATCH.model_dump(mode="json"),
        "events": [e.model_dump(mode="json") for e in MATCH.events if e.id != "half"],
    })
    with patch("vybe.director_agent._configuration") as config:
        result = director_ask(without_half, "What was the halftime score?")
    config.assert_not_called()
    assert result["supported"] is False
    assert result["evidence_event_ids"] == []
    assert "missing" in result["answer"]


@pytest.mark.parametrize("question", [
    "What was the halftime score?", "What happened in the last 15 minutes?",
    "What was the final score?", "Who scored?", "What were the turning points?",
])
def test_temporal_detection_only_matches_supported_time_windows(question):
    expected = question in ("What was the halftime score?", "What happened in the last 15 minutes?")
    assert is_temporal_question(question) is expected


def test_director_matches_existing_deterministic_answer():
    for question in ("What was the halftime score?", "What happened in the last 15 minutes?"):
        assert director_ask(MATCH, question)["answer"] == ask_match(MATCH, question)["answer"]
