"""Regression cases for provider failures and malformed completions."""
import http.client
import io
import json
import logging
import urllib.error
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from vybe.ai import narrate_goal, _validate_segments, _verified_facts
from vybe.main import app
from vybe.models import MatchDefinition

SECRET="sk-test-secret-123"
ENV={"VYBE_AZURE_OPENAI_ENDPOINT":"https://test.openai.azure.com",
     "VYBE_AZURE_OPENAI_KEY":SECRET,"VYBE_AZURE_OPENAI_DEPLOYMENT":"demo"}
MATCH={"match_id":"t","home_team":"Aurora","away_team":"Harbor",
       "events":[{"id":"goal-1","minute":12,"team":"Aurora","type":"goal"}]}
def match(): return MatchDefinition.model_validate(MATCH)
def completion(content): return {"choices":[{"message":{"content":content}}]}
def azure_replies(payload):
    return patch("vybe.ai.urllib.request.urlopen",return_value=io.BytesIO(json.dumps(payload).encode()))
def assert_fallback(result):
    assert result["generation_mode"]=="deterministic"
    assert result["score"]=={"home":1,"away":0}
    assert result["evidence_event_ids"]==["goal-1"]

@pytest.mark.parametrize("payload",[completion(None),completion(""),completion("   "),
    completion(["not","text"]),{"choices":[{"message":{}}]},{"choices":[]},
    {"choices":None},{},[]])
def test_bad_completion_falls_back(payload,caplog):
    with patch.dict("os.environ",ENV,clear=True),azure_replies(payload):
        assert_fallback(narrate_goal(match(),"goal-1"))
    assert any(r.levelno==logging.WARNING for r in caplog.records)

@pytest.mark.parametrize("failure",[urllib.error.URLError("offline"),
    urllib.error.HTTPError("https://x",429,"Too Many Requests",{},None),
    TimeoutError("timeout"),ConnectionResetError("reset"),
    http.client.IncompleteRead(b"partial"),http.client.RemoteDisconnected("closed")])
def test_network_failure_falls_back_without_logging_secrets(failure,caplog):
    with patch.dict("os.environ",ENV,clear=True),patch("vybe.ai.urllib.request.urlopen",side_effect=failure):
        assert_fallback(narrate_goal(match(),"goal-1"))
    assert SECRET not in caplog.text

def test_null_completion_http_api_responds_200():
    with patch.dict("os.environ",ENV,clear=True),azure_replies(completion(None)):
        response=TestClient(app).post("/v1/matches/narrate/goal-1",json=MATCH)
    assert response.status_code==200
    assert_fallback(response.json())

def test_unexpected_bug_has_traceback_and_fallback(caplog):
    with patch.dict("os.environ",ENV,clear=True),patch("vybe.ai._generate",return_value="{}"),patch("vybe.ai._validate_segments",side_effect=AttributeError("bug")):
        assert_fallback(narrate_goal(match(),"goal-1"))
    assert any(r.levelno==logging.ERROR and r.exc_info for r in caplog.records)

def test_invalid_configuration_never_sends_request(caplog):
    with patch.dict("os.environ",{**ENV,"VYBE_AZURE_OPENAI_ENDPOINT":"http://bad.example"},clear=True),patch("vybe.ai.urllib.request.urlopen") as send:
        assert_fallback(narrate_goal(match(),"goal-1"))
    send.assert_not_called()
    assert any(r.levelno==logging.ERROR for r in caplog.records)
    assert SECRET not in caplog.text

@pytest.mark.parametrize("value",[None,0,False,[],{},["text"]])
@pytest.mark.parametrize("field",["opening","closing"])
def test_framing_must_be_string(field,value):
    _,facts=_verified_facts(match(),"goal-1","young")
    payload={"segments":[{"fact_id":k,"text":facts[k]} for k in ("goal","score")],field:value}
    with pytest.raises(ValueError):
        _validate_segments(json.dumps(payload),facts,"young")

def test_invalid_caller_input_still_raises():
    with patch.dict("os.environ",ENV,clear=True),patch("vybe.ai.urllib.request.urlopen") as send:
        with pytest.raises(ValueError):
            narrate_goal(match(),"missing")
        with pytest.raises(ValueError):
            narrate_goal(match(),"goal-1","invalid")
    send.assert_not_called()
