"""Evidence-validated narration tests; no Azure account required."""
import json
from unittest.mock import patch

from vybe.ai import narrate_goal, _verified_facts
from vybe.models import MatchDefinition


def match():
    return MatchDefinition.model_validate({
        "match_id": "test", "home_team": "Aurora", "away_team": "Harbor",
        "events": [{"id": "goal-1", "minute": 12, "team": "Aurora", "type": "goal"}],
    })


ENV = {"VYBE_AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
       "VYBE_AZURE_OPENAI_KEY": "fake",
       "VYBE_AZURE_OPENAI_DEPLOYMENT": "demo"}


def generated(facts, keys=("goal", "score")):
    return json.dumps({"segments": [{"fact_id": key, "text": facts[key]} for key in keys]})


def test_no_credentials_uses_deterministic_narrative():
    with patch.dict("os.environ", {}, clear=True):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "deterministic"
    assert result["synthetic"] is True
    assert result["evidence_event_ids"] == ["goal-1"]


def test_valid_verified_model_segments():
    _, facts = _verified_facts(match(), "goal-1", "young")
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=generated(facts, ("score", "goal", "context"))
    ):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "azure_ai"
    assert result["narrative"] == " ".join([facts["score"], facts["goal"], facts["context"]])
    assert result["selected_fact_ids"] == ["context", "goal", "score"]
    assert result["evidence_event_ids"] == ["goal-1"]


def test_generated_text_without_score_is_rejected():
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value="Aurora scored an incredible goal!"
    ):
        result = narrate_goal(match(), "goal-1", "analyst")
    assert result["generation_mode"] == "deterministic"


def test_provider_failure_falls_back():
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", side_effect=OSError("offline")
    ):
        assert narrate_goal(match(), "goal-1")["generation_mode"] == "deterministic"


def test_provider_timeout_preserves_verified_facts():
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", side_effect=TimeoutError("timed out")
    ):
        result = narrate_goal(match(), "goal-1", "accessible")
    assert result["generation_mode"] == "deterministic"
    assert result["score"] == {"home": 1, "away": 0}
    assert result["evidence_event_ids"] == ["goal-1"]


def test_invalid_provider_style_preserves_verified_facts():
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value='{"style":"invented"}'
    ):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "deterministic"
    assert result["score"] == {"home": 1, "away": 0}


def test_hallucinated_segment_rejected():
    _, facts = _verified_facts(match(), "goal-1", "young")
    payload = json.loads(generated(facts))
    payload["segments"][0]["text"] += " It was a bicycle kick."
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps(payload)
    ):
        assert narrate_goal(match(), "goal-1")["generation_mode"] == "deterministic"


def test_duplicate_evidence_rejected():
    _, facts = _verified_facts(match(), "goal-1", "young")
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=generated(facts, ("goal", "goal", "score"))
    ):
        assert narrate_goal(match(), "goal-1")["generation_mode"] == "deterministic"


def test_unknown_evidence_rejected():
    _, facts = _verified_facts(match(), "goal-1", "young")
    payload = json.loads(generated(facts))
    payload["segments"][0]["fact_id"] = "invented"
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps(payload)
    ):
        assert narrate_goal(match(), "goal-1")["generation_mode"] == "deterministic"


def test_duplicate_json_keys_rejected():
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value='{"segments":[],"segments":[]}'
    ):
        assert narrate_goal(match(), "goal-1")["generation_mode"] == "deterministic"


def test_persona_framing_is_accepted_only_with_verified_facts():
    _, facts = _verified_facts(match(), "goal-1", "young")
    payload = json.loads(generated(facts))
    payload["opening"] = "What a moment!"
    payload["closing"] = "Keep watching!"
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps(payload)
    ):
        result = narrate_goal(match(), "goal-1", "young")
    assert result["generation_mode"] == "azure_ai"
    assert result["narrative"].startswith("What a moment! ")
    assert result["narrative"].endswith(" Keep watching!")
    assert result["evidence_event_ids"] == ["goal-1"]


def test_unapproved_framing_is_rejected():
    _, facts = _verified_facts(match(), "goal-1", "young")
    payload = json.loads(generated(facts))
    payload["opening"] = "Aurora scored a bicycle kick!"
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps(payload)
    ):
        assert narrate_goal(match(), "goal-1", "young")["generation_mode"] == "deterministic"


def test_cross_persona_framing_is_rejected():
    _, facts = _verified_facts(match(), "goal-1", "analyst")
    payload = json.loads(generated(facts))
    payload["opening"] = "What a moment!"
    with patch.dict("os.environ", ENV, clear=True), patch(
        "vybe.ai._generate", return_value=json.dumps(payload)
    ):
        assert narrate_goal(match(), "goal-1", "analyst")["generation_mode"] == "deterministic"
