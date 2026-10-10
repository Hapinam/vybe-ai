"""Regression tests: deterministic scores, evidence and persona consistency."""

from fastapi.testclient import TestClient
from vybe.main import app

client = TestClient(app)

MATCH = {
    "match_id": "demo-87",
    "home_team": "Team A",
    "away_team": "Team B",
    "events": [
        {"id": "e1", "minute": 0, "type": "kickoff"},
        {"id": "e2", "minute": 12, "team": "Team A", "type": "goal"},
        {"id": "e3", "minute": 25, "team": "Team B", "type": "goal"},
        {"id": "e4", "minute": 55, "team": "Team B", "type": "goal"},
        {"id": "e5", "minute": 73, "team": "Team A", "type": "goal"},
        {"id": "e6", "minute": 87, "second": 24, "team": "Team A", "type": "shot"},
    ],
}


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_replay_score():
    response = client.post("/v1/matches/replay", json=MATCH)
    assert response.status_code == 200
    state = response.json()["state"]
    assert (state["home_score"], state["away_score"]) == (2, 2)
    assert state["shots_home"] == 1


def test_partial_replay():
    state = client.post("/v1/matches/replay?through_event=3", json=MATCH).json()["state"]
    assert (state["home_score"], state["away_score"]) == (1, 1)


def test_personas_same_facts():
    results = [
        client.post(f"/v1/matches/explain/e5?persona={persona}", json=MATCH).json()
        for persona in ("young", "accessible", "analyst")
    ]
    assert all(result["score"] == {"home": 2, "away": 2} for result in results)
    assert all(result["evidence_event_ids"] == ["e5"] for result in results)
    assert len({result["narrative"] for result in results}) == 3


def test_reject_unknown_team():
    broken = {**MATCH, "events": [{"id": "bad", "minute": 3, "team": "Other", "type": "goal"}]}
    assert client.post("/v1/matches/replay", json=broken).status_code == 422


def test_reject_duplicate_event_ids():
    broken = {**MATCH, "events": [MATCH["events"][0], MATCH["events"][0]]}
    assert client.post("/v1/matches/replay", json=broken).status_code == 422


def test_reject_non_goal_explanation():
    assert client.post("/v1/matches/explain/e6", json=MATCH).status_code == 422
