"""Evidence traceability, persona consistency and endpoint regression."""
import pytest
from fastapi.testclient import TestClient

from vybe.insights import match_insights
from vybe.main import app
from vybe.models import MatchDefinition

MATCH = {
    "match_id": "insights", "home_team": "Aurora", "away_team": "Harbor",
    "events": [
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 60, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
}
client = TestClient(app)


@pytest.mark.parametrize("persona", ["young", "accessible", "analyst"])
def test_personas_share_facts_but_change_explanation(persona):
    result = match_insights(MatchDefinition.model_validate(MATCH), persona)
    assert result["score"] == {"home": 1, "away": 1}
    assert result["recap_evidence_event_ids"] == ["g1", "g2", "end"]
    assert [c["evidence_event_ids"] for c in result["insights"]] == [["g1"], ["g2"]]
    assert result["insights"][1]["impact"] == "equalizer"
    assert result["generation_mode"] == "deterministic"
    assert result["synthetic"] is True
    assert result["fulltime_confirmed"] is True


def test_persona_narratives_differ():
    match = MatchDefinition.model_validate(MATCH)
    assert len({match_insights(match, p)["insights"][0]["explanation"]
                for p in ("young", "accessible", "analyst")}) == 3


def test_no_fulltime_is_not_final():
    partial = {**MATCH, "events": MATCH["events"][:-1]}
    result = match_insights(MatchDefinition.model_validate(partial))
    assert result["fulltime_confirmed"] is False
    assert "so far" in result["recap"]
    assert "end" not in result["recap_evidence_event_ids"]


def test_no_goals_does_not_invent_moments():
    empty = {**MATCH, "events": [{"id": "end", "minute": 90, "type": "fulltime"}]}
    result = match_insights(MatchDefinition.model_validate(empty))
    assert result["insights"] == []
    assert result["score"] == {"home": 0, "away": 0}


def test_endpoint_validates_persona():
    assert client.post("/v1/matches/insights?persona=young", json=MATCH).status_code == 200
    assert client.post("/v1/matches/insights?persona=unknown", json=MATCH).status_code == 422


def test_agentic_ask_preserves_decline_for_unsupported_causality(monkeypatch):
    from vybe import director_agent
    monkeypatch.setattr(director_agent, "_configuration", lambda: ("https://example.openai.azure.com", "test", "model"))
    monkeypatch.setattr(director_agent, "_select_tool", lambda question, config: "get_key_moments")
    data = director_agent.director_ask(MatchDefinition.model_validate(MATCH), "Why did the coach change tactics?")
    assert data["supported"] is False
    assert data["generation_mode"] == "deterministic"
    assert data["selected_tool"] is None


def test_agentic_ask_evidence_on_valid_question(monkeypatch):
    from vybe import director_agent
    monkeypatch.setattr(director_agent, "_configuration", lambda: ("https://example.openai.azure.com", "test", "model"))
    monkeypatch.setattr(director_agent, "_select_tool", lambda question, config: "get_key_moments")
    data = director_agent.director_ask(MatchDefinition.model_validate(MATCH), "What were the turning points?")
    assert data["supported"] is True
    assert data["selected_tool"] == "get_key_moments"
    assert data["evidence_event_ids"] == ["g1", "g2"]
