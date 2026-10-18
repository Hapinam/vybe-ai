"""Contract tests for future agent tool calls; no Azure dependency."""
import pytest
from fastapi.testclient import TestClient

from vybe.director_tools import TOOL_NAMES, call_director_tool
from vybe.main import app
from vybe.models import MatchDefinition

MATCH = MatchDefinition.model_validate({
    "match_id": "director-fixture", "home_team": "Aurora", "away_team": "Harbor",
    "events": [
        {"id": "start", "minute": 0, "type": "kickoff"},
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 20, "team": "Harbor", "type": "goal"},
        {"id": "shot", "minute": 30, "team": "Harbor", "type": "shot"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})


def test_allowlisted_tools_are_read_only_and_evidence_grounded():
    assert len(TOOL_NAMES) == 3
    state = call_director_tool("get_match_state", MATCH)
    assert state["score"] == {"home": 1, "away": 1}
    assert state["fulltime_confirmed"] is True
    assert state["evidence_event_ids"] == ["g1", "g2", "end"]
    moments = call_director_tool("get_key_moments", MATCH)
    assert [m["impact"] for m in moments["moments"]] == ["took_lead", "equalizer"]
    assert [m["evidence_event_ids"] for m in moments["moments"]] == [["g1"], ["g2"]]
    assert moments["tactical_causation_supported"] is False
    stats = call_director_tool("get_match_statistics", MATCH)
    assert stats["shots"] == {"home": 1, "away": 2}
    assert stats["evidence_event_ids"] == ["g1", "g2", "shot"]
    assert "no possession" in stats["limitations"]


def test_unsupported_tool_is_rejected():
    with pytest.raises(ValueError, match="Unsupported director tool"):
        call_director_tool("__import__", MATCH)


def test_tool_calls_do_not_mutate_input():
    before = MATCH.model_dump()
    for name in TOOL_NAMES:
        call_director_tool(name, MATCH)
    assert MATCH.model_dump() == before


def test_missing_fulltime_not_mislabeled_final():
    match = MatchDefinition.model_validate({**MATCH.model_dump(), "events": [
        e.model_dump() for e in MATCH.events if e.id != "end"
    ]})
    assert call_director_tool("get_match_state", match)["fulltime_confirmed"] is False


def test_existing_ask_contract_remains_available():
    response = TestClient(app).post("/v1/matches/ask", json={
        "match": MATCH.model_dump(mode="json"), "question": "Who scored?"
    })
    assert response.status_code == 200
    assert response.json()["generation_mode"] == "deterministic"
