"""Offline integration tests for Match Director provider routing."""

from unittest.mock import patch

import pytest

from vybe.director_agent import director_ask
from vybe.models import MatchDefinition


MATCH = MatchDefinition.model_validate({
    "match_id": "integration-test",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


def test_ollama_provider_selects_read_only_tool(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "ollama")

    with patch(
        "vybe.director_ollama._select_tool",
        return_value="get_match_state",
    ) as selected:
        result = director_ask(MATCH, "What is the score?")

    selected.assert_called_once_with("What is the score?")
    assert result["generation_mode"] == "ollama_model_tool_call"
    assert result["selected_tool"] == "get_match_state"
    assert result["supported"] is True
    assert result["synthetic"] is True


def test_ollama_timeout_falls_back(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "ollama")

    with patch(
        "vybe.director_ollama._select_tool",
        side_effect=TimeoutError("timeout"),
    ):
        result = director_ask(MATCH, "Who scored?")

    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None
    assert result["evidence_event_ids"] == ["g1", "g2"]


def test_ollama_decline_preserves_fallback(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "ollama")

    with patch(
        "vybe.director_ollama._select_tool",
        return_value="decline_unsupported_question",
    ):
        result = director_ask(MATCH, "Who was the best player?")

    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None
    assert result["model_declined"] is True


def test_deterministic_provider_skips_model(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "deterministic")

    with patch("vybe.director_agent._select_tool") as foundry, patch(
        "vybe.director_ollama._select_tool"
    ) as ollama:
        result = director_ask(MATCH, "Who scored?")

    assert result["generation_mode"] == "deterministic"
    foundry.assert_not_called()
    ollama.assert_not_called()


def test_unknown_provider_falls_back(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "unknown")

    result = director_ask(MATCH, "Who scored?")

    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None


def test_foundry_provider_unchanged(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "foundry")

    with patch(
        "vybe.director_agent._configuration",
        return_value=("https://example.openai.azure.com", "test-key", "model"),
    ), patch(
        "vybe.director_agent._select_tool",
        return_value="get_match_state",
    ) as selected:
        result = director_ask(MATCH, "What is the score?")

    selected.assert_called_once()
    assert result["generation_mode"] == "foundry_model_tool_call"
    assert result["selected_tool"] == "get_match_state"


def test_temporal_question_skips_ollama(monkeypatch):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", "ollama")

    with patch("vybe.director_ollama._select_tool") as selected:
        result = director_ask(MATCH, "What was the halftime score?")

    selected.assert_not_called()
    assert result["generation_mode"] == "deterministic"
