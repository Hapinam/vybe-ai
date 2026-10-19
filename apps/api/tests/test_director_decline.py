"""The model must be able to decline unsupported questions with required tool calls."""
import io
import json
from unittest.mock import patch

from vybe.director_agent import DECLINE_TOOL, director_ask
from vybe.models import MatchDefinition

MATCH = MatchDefinition.model_validate({
    "match_id": "m", "home_team": "Aurora", "away_team": "Harbor",
    "events": [{"id": "g1", "minute": 10, "team": "Aurora", "type": "goal"},
               {"id": "g2", "minute": 80, "team": "Harbor", "type": "goal"},
               {"id": "end", "minute": 90, "type": "fulltime"}],
})
CONFIG = ("https://example.openai.azure.com", "fake-test-key", "gpt-test")


def reply(name, args="{}"):
    return io.BytesIO(json.dumps({"choices": [{"message": {"tool_calls": [
        {"type": "function", "function": {"name": name, "arguments": args}}]}}]}).encode())


def ask(question, model_reply):
    with patch("vybe.director_agent._configuration", return_value=CONFIG), \
            patch("vybe.director_agent.urllib.request.urlopen", return_value=model_reply) as urlopen, \
            patch("vybe.director_agent.call_director_tool") as run_tool:
        result = director_ask(MATCH, question)
    return result, urlopen, run_tool


def test_declined_off_topic_question_is_not_answered_with_the_score():
    result, urlopen, run_tool = ask("Tell me a joke", reply(DECLINE_TOOL))
    urlopen.assert_called_once()
    run_tool.assert_not_called()
    assert result["supported"] is False
    assert result["selected_tool"] is None
    assert result["evidence_event_ids"] == []
    assert result["generation_mode"] != "foundry_model_tool_call"
    assert "score" not in result["answer"].lower() or "cannot" in result["answer"].lower()


def test_decline_still_returns_a_keyword_supported_fact_when_one_applies():
    result, _, run_tool = ask("Who scored?", reply(DECLINE_TOOL))
    run_tool.assert_not_called()
    assert result["supported"] is True and result["selected_tool"] is None
    assert result["evidence_event_ids"] == ["g1", "g2"]


def test_decline_with_arguments_is_rejected_like_any_other_tool():
    result, _, run_tool = ask("Tell me a joke", reply(DECLINE_TOOL, '{"anything": 1}'))
    run_tool.assert_not_called()
    assert result["supported"] is False and result["selected_tool"] is None


def test_real_tools_still_work_and_are_marked_as_model_selected():
    with patch("vybe.director_agent._configuration", return_value=CONFIG), \
            patch("vybe.director_agent.urllib.request.urlopen", return_value=reply("get_match_state")):
        result = director_ask(MATCH, "What's the final score?")
    assert result["supported"] is True
    assert result["selected_tool"] == "get_match_state"
    assert result["generation_mode"] == "foundry_model_tool_call"
