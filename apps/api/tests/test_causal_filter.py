"""Regression matrix from the supplied causal-filter review patch."""
import os
from unittest.mock import patch
import pytest
from vybe.director_agent import director_ask
from vybe.models import MatchDefinition
from vybe.questions import ask_match

MATCH = MatchDefinition.model_validate({
    "match_id": "t", "home_team": "Aurora", "away_team": "Harbor",
    "events": [{"id": "e1", "minute": 10, "team": "Aurora", "type": "goal", "player": "Maya"},
               {"id": "e2", "minute": 90, "type": "fulltime"}],
})
ENV = {"VYBE_FOUNDRY_MODEL_ENDPOINT": "https://x.openai.azure.com",
       "VYBE_FOUNDRY_MODEL_KEY": "k", "VYBE_FOUNDRY_MODEL_DEPLOYMENT": "d"}
CAUSAL = [
    "Why did Harbor lose?", "What caused the goal?", "What causes momentum shifts?", "Was it causal?",
    "What tactics did Harbor use?", "Was the tactical plan good?", "Which formations did they play?",
    "Explain the strategies", "What was Aurora's strategy?", "Which formation was used?",
]
FACTUAL = [
    "Who scored?", "What is the score?", "Show information about the goals",
    "Who scored because of a cross?", "Did Whyte score?",
]

@pytest.mark.parametrize("question", CAUSAL)
def test_causal_questions_declined_before_model_call(question):
    with patch.dict(os.environ, ENV, clear=True), patch(
        "vybe.director_agent._select_tool", return_value="get_match_state"
    ) as select:
        result = director_ask(MATCH, question, "analyst")
    select.assert_not_called()
    assert result["supported"] is False
    assert result["selected_tool"] is None
    assert result["evidence_event_ids"] == []

@pytest.mark.parametrize("question", FACTUAL)
def test_factual_questions_not_blocked_by_substrings(question):
    with patch.dict(os.environ, ENV, clear=True), patch(
        "vybe.director_agent._select_tool", return_value="get_match_state"
    ) as select:
        result = director_ask(MATCH, question, "analyst")
    select.assert_called_once()
    assert result["supported"] is True

@pytest.mark.parametrize("question", ["Why did Harbor lose?", "What caused it?", "Any momentum?"])
def test_deterministic_ask_declines_causal_wording(question):
    assert ask_match(MATCH, question)["supported"] is False
