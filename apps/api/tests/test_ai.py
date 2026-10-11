"""AI narration must work without paid cloud credentials."""
from unittest.mock import patch

from vybe.ai import narrate_goal
from vybe.models import MatchDefinition


def match():
    return MatchDefinition.model_validate({
        "match_id": "test",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [{"id": "goal-1", "minute": 12, "team": "Aurora", "type": "goal"}],
    })


def test_no_credentials_uses_deterministic_narrative():
    with patch.dict("os.environ", {}, clear=True):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "deterministic"
    assert result["synthetic"] is True
    assert result["evidence_event_ids"] == ["goal-1"]


def test_generated_text_without_score_is_rejected():
    env = {"VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
           "VYBE_AZURE_OPENAI_KEY": "fake",
           "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo"}
    with patch.dict("os.environ", env, clear=True), patch("vybe.ai._generate", return_value="Aurora scored an incredible goal!"):
        result = narrate_goal(match(), "goal-1", "analyst")
    assert result["generation_mode"] == "deterministic"


def test_provider_failure_falls_back():
    env = {"VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
           "VYBE_AZURE_OPENAI_KEY": "fake",
           "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo"}
    with patch.dict("os.environ", env, clear=True), patch("vybe.ai._generate", side_effect=OSError("offline")):
        result = narrate_goal(match(), "goal-1")
    assert result["generation_mode"] == "deterministic"


def test_provider_timeout_preserves_verified_facts():
    env = {"VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
           "VYBE_AZURE_OPENAI_KEY": "fake",
           "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo"}
    with patch.dict("os.environ", env, clear=True), patch("vybe.ai._generate", side_effect=TimeoutError("timed out")):
        result = narrate_goal(match(), "goal-1", "accessible")
    assert result["generation_mode"] == "deterministic"
    assert result["score"] == {"home": 1, "away": 0}
    assert result["evidence_event_ids"] == ["goal-1"]
    assert result["synthetic"] is True


def test_invalid_provider_style_preserves_verified_facts():
    env = {"VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
           "VYBE_AZURE_OPENAI_KEY": "fake",
           "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo"}
    with patch.dict("os.environ", env, clear=True), patch("vybe.ai._generate", return_value='{"style":"invented"}'):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "deterministic"
    assert result["score"] == {"home": 1, "away": 0}
    assert result["evidence_event_ids"] == ["goal-1"]
