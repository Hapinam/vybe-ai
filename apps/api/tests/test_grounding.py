"""Security regression tests for AI response grounding."""
import json
from unittest.mock import patch

import pytest

from vybe.ai import _verified_style, narrate_goal
from vybe.models import MatchDefinition

MATCH = MatchDefinition.model_validate({
    "match_id": "test",
    "home_team": "Aurora",
    "away_team": "Harbor",
    "events": [
        {"id": "e1", "minute": 0, "type": "kickoff"},
        {"id": "e2", "minute": 87, "second": 24, "team": "Aurora", "type": "goal"},
    ],
})
ENV = {
    "VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
    "VYBE_AZURE_OPENAI_KEY": "fake-test-key",
    "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo",
}


@pytest.mark.parametrize("candidate", [
    '{"style":"excited","narrative":"A stunning bicycle kick!"}',
    '{"style":"tactical"}',
    '{"style":"calm"}',
    '{"style":1}',
    'The striker scored after a perfect cross',
    '["excited"]',
    '{"style":"excited"} extra text',
    '{"style":"excited","style":"friendly"}',
])
def test_invalid_response_does_not_become_commentary(candidate):
    with patch.dict("os.environ", ENV, clear=True), patch("vybe.ai._generate", return_value=candidate):
        result = narrate_goal(MATCH, "e2", "young")
    # Duplicate JSON keys are currently parsed by json.loads; never allow
    # extra factual text to be accepted as model-authored commentary.
    assert "bicycle" not in result["narrative"]
    assert "cross" not in result["narrative"]
    assert result["score"] == {"home": 1, "away": 0}
    assert result["evidence_event_ids"] == ["e2"]


@pytest.mark.parametrize("persona,style", [
    ("young", "excited"),
    ("young", "friendly"),
    ("accessible", "clear"),
    ("accessible", "calm"),
    ("analyst", "concise"),
    ("analyst", "neutral"),
])
def test_allowed_style_renders_only_verified_facts(persona, style):
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps({"style": style})
    ):
        result = narrate_goal(MATCH, "e2", persona)
    assert result["generation_mode"] == "azure_ai"
    assert "Aurora" in result["narrative"]
    assert "Harbor" in result["narrative"]
    assert result["score"] == {"home": 1, "away": 0}
    assert result["synthetic"] is True


def test_unconfigured_is_free_and_deterministic():
    with patch.dict("os.environ", {}, clear=True), patch("vybe.ai._generate") as generate:
        result = narrate_goal(MATCH, "e2")
    generate.assert_not_called()
    assert result["generation_mode"] == "deterministic"


def test_invalid_persona_rejected_before_model():
    with patch.dict("os.environ", ENV, clear=True):
        with pytest.raises(ValueError):
            narrate_goal(MATCH, "e2", "unsupported")


def test_model_failure_falls_back():
    with patch.dict("os.environ", ENV, clear=True), patch("vybe.ai._generate", side_effect=OSError("offline")):
        result = narrate_goal(MATCH, "e2")
    assert result["generation_mode"] == "deterministic"
