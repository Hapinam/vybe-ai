"""Contract and grounding checks for Ask the Match."""
from fastapi.testclient import TestClient
from vybe.main import app

client = TestClient(app)
MATCH = {
    "match_id": "synthetic-1", "home_team": "Aurora", "away_team": "Harbor",
    "events": [
        {"id": "start", "minute": 0, "type": "kickoff"},
        {"id": "g1", "minute": 12, "team": "Aurora", "player": "Alex", "type": "goal"},
        {"id": "half", "minute": 45, "type": "halftime"},
        {"id": "g2", "minute": 65, "team": "Harbor", "type": "goal"},
        {"id": "shot", "minute": 83, "team": "Aurora", "type": "shot"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
}


def ask(question, match=MATCH):
    return client.post("/v1/matches/ask", json={"match": match, "question": question})


def test_scorers_are_evidence_linked():
    response = ask("Who scored?")
    assert response.status_code == 200
    data = response.json()
    assert data["evidence_event_ids"] == ["g1", "g2"]
    assert "Alex" in data["answer"]
    assert "Unspecified player" in data["answer"]
    assert data["generation_mode"] == "deterministic"


def test_halftime_score_uses_marker():
    data = ask("What was the halftime score?").json()
    assert "1–0" in data["answer"]
    assert data["evidence_event_ids"] == ["g1", "half"]


def test_final_score_and_evidence():
    data = ask("What was the final score?").json()
    assert "1–1" in data["answer"]
    assert data["evidence_event_ids"] == ["g1", "g2", "end"]


def test_last_15_minutes():
    data = ask("What happened in the last 15 minutes?").json()
    assert data["evidence_event_ids"] == ["shot", "end"]
    assert "1 shot" in data["answer"]


def test_no_tactical_hallucination():
    data = ask("Why did momentum change?").json()
    assert data["supported"] is False
    assert data["evidence_event_ids"] == []
    assert "not xG" in data["answer"]


def test_unknown_question_declined():
    data = ask("Who was the referee?").json()
    assert data["supported"] is False
    assert data["evidence_event_ids"] == []


def test_missing_halftime_marker_declined():
    data = ask("Halftime score?", {**MATCH, "events": [e for e in MATCH["events"] if e["id"] != "half"]}).json()
    assert data["supported"] is False


def test_missing_fulltime_marker_declined():
    data = ask("Final score?", {**MATCH, "events": [e for e in MATCH["events"] if e["id"] != "end"]}).json()
    assert data["supported"] is False


def test_invalid_question_and_match_rejected():
    assert ask("").status_code == 422
    assert ask("a" * 301).status_code == 422
    assert ask("Who scored?", {**MATCH, "home_team": "Harbor"}).status_code == 422


def test_custom_match_is_not_hardcoded():
    custom = {
        "match_id": "other", "home_team": "North", "away_team": "South",
        "events": [{"id": "z", "minute": 1, "team": "South", "type": "goal"},
                   {"id": "f", "minute": 90, "type": "fulltime"}],
    }
    data = ask("Final score?", custom).json()
    assert "North 0–1 South" in data["answer"]
    assert data["evidence_event_ids"] == ["z", "f"]


def test_derived_causal_questions_are_declined():
    from vybe.director_agent import _UNSUPPORTED_CAUSAL
    from vybe.models import MatchDefinition
    match = MatchDefinition.model_validate({
        "match_id": "m", "home_team": "Aurora", "away_team": "Harbor", "events": []
    })
    for question in (
        "What tactics did they use?", "Which tactical setup?",
        "Explain the strategies", "Which formations?",
        "Was it causal?", "What caused it?",
    ):
        assert ask_match(match, question)["supported"] is False, question
