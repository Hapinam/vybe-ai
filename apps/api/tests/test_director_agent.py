"""Mocked Foundry-hosted model tool selection; no cloud calls or credentials."""
import io
import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from vybe.director_agent import director_ask
from vybe.main import app
from vybe.models import MatchDefinition

MATCH = MatchDefinition.model_validate({
    "match_id": "m", "home_team": "Aurora", "away_team": "Harbor",
    "events": [
        {"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
        {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
        {"id": "end", "minute": 90, "type": "fulltime"},
    ],
})
CONFIG = ("https://example.openai.azure.com", "fake-test-key", "gpt-test")


def reply(name, args="{}"):
    return io.BytesIO(json.dumps({"choices": [{"message": {"tool_calls": [
        {"type": "function", "function": {"name": name, "arguments": args}}
    ]}}]}).encode())


def test_no_configuration_preserves_deterministic_fallback(monkeypatch):
    for key in ("VYBE_FOUNDRY_MODEL_ENDPOINT", "VYBE_FOUNDRY_MODEL_KEY", "VYBE_FOUNDRY_MODEL_DEPLOYMENT"):
        monkeypatch.delenv(key, raising=False)
    result = director_ask(MATCH, "Who scored?")
    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None
    assert result["evidence_event_ids"] == ["g1", "g2"]


def test_real_tool_call_envelope_mocked():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=reply("get_key_moments")
    ) as urlopen:
        result = director_ask(MATCH, "What were the turning points?")
    assert result["generation_mode"] == "foundry_model_tool_call"
    assert result["selected_tool"] == "get_key_moments"
    assert result["evidence_event_ids"] == ["g1", "g2"]
    assert "equalizer" in result["answer"]
    request = urlopen.call_args.args[0]
    payload = json.loads(request.data)
    assert payload["tool_choice"] == "required"
    assert len(payload["tools"]) == 4
    assert "fake-test-key" not in request.data.decode()


def test_unknown_tool_refused_and_fallback():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=reply("run_shell")
    ):
        result = director_ask(MATCH, "Who scored?")
    assert result["generation_mode"] == "deterministic"
    assert result["selected_tool"] is None


def test_arguments_rejected():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=reply("get_match_state", '{"command":"rm"}')
    ):
        assert director_ask(MATCH, "Who scored?")["generation_mode"] == "deterministic"


def test_timeout_falls_back():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", side_effect=TimeoutError("timeout")
    ):
        assert director_ask(MATCH, "Who scored?")["generation_mode"] == "deterministic"


def test_malformed_response_falls_back():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=io.BytesIO(b'{"choices": []}')
    ):
        assert director_ask(MATCH, "Who scored?")["generation_mode"] == "deterministic"


def test_http_contract_and_validation():
    client = TestClient(app)
    payload = {"match": MATCH.model_dump(mode="json"), "question": "Who scored?", "persona": "young"}
    response = client.post("/v1/matches/director/ask", json=payload)
    assert response.status_code == 200
    assert response.json()["synthetic"] is True
    assert client.post("/v1/matches/director/ask", json={**payload, "persona": "invalid"}).status_code == 422


def test_foundry_request_contract_is_explicit_and_secret_stays_in_header():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=reply("get_match_state")
    ) as urlopen:
        result = director_ask(MATCH, "What is the score?")
    assert result["generation_mode"] == "foundry_model_tool_call"
    request = urlopen.call_args.args[0]
    assert request.full_url == (
        "https://example.openai.azure.com/openai/deployments/gpt-test/"
        "chat/completions?api-version=2024-10-21"
    )
    assert request.get_method() == "POST"
    assert request.get_header("Api-key") == "fake-test-key"
    assert urlopen.call_args.kwargs["timeout"] == 6
    payload = json.loads(request.data)
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 100
    assert payload["tool_choice"] == "required"
    assert {tool["function"]["name"] for tool in payload["tools"]} == {
        "get_match_state", "get_key_moments", "get_match_statistics", "decline_unsupported_question"
    }
    assert all(tool["function"]["parameters"]["additionalProperties"] is False
               for tool in payload["tools"])
    assert "fake-test-key" not in request.data.decode()


def test_unsupported_causal_variants_declined_before_model_call():
    from unittest.mock import patch
    variants = (
        "What tactics did Harbor use?", "Was their play tactical?",
        "Which formations did they play?", "Explain the strategies",
        "Was it a causal effect?", "What caused the defeat?",
    )
    with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
        "vybe.director_agent.urllib.request.urlopen", return_value=reply("get_match_state")
    ) as urlopen:
        for question in variants:
            result = director_ask(MATCH, question)
            assert result["supported"] is False, question
            assert result["generation_mode"] == "deterministic", question
            assert result["selected_tool"] is None, question
    urlopen.assert_not_called()


def test_unrelated_substrings_do_not_trigger_causal_decline():
    from unittest.mock import patch
    for question in ("Who is Whyte?", "What information is recorded?", "Because of whom?"):
        with patch("vybe.director_agent._configuration", return_value=CONFIG), patch(
            "vybe.director_agent.urllib.request.urlopen", return_value=reply("get_match_state")
        ) as urlopen:
            result = director_ask(MATCH, question)
            assert result["generation_mode"] == "foundry_model_tool_call", question
            urlopen.assert_called_once()
