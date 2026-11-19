"""Grounded penalty shootout Director routing tests."""

import pytest

from vybe.director_agent import director_ask
from vybe.models import MatchDefinition


@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_shootout_winner_uses_deterministic_evidence(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(provider):
        def reject(*args, **kwargs):
            provider_calls.append(provider)
            raise AssertionError(f"Unexpected {provider} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "shootout-routing",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {
                "id": f"p{i}",
                "order": i,
                "team": "Aurora" if i % 2 else "Harbor",
                "outcome": "scored" if i % 2 else "missed",
            }
            for i in range(1, 7)
        ],
    })

    response = director_ask(match, "Who won the penalty shootout?")

    assert provider_calls == [], f"Unexpected provider calls: {provider_calls}"
    assert response["supported"] is True
    assert response["generation_mode"] == "deterministic"
    assert "Aurora" in response["answer"]
    assert "3" in response["answer"]
    assert "0" in response["answer"]
    assert response["evidence_event_ids"] == [
        "p1", "p2", "p3", "p4", "p5", "p6"
    ]



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_incomplete_shootout_does_not_claim_winner(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "incomplete-shootout",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
            {"id": "p2", "order": 2, "team": "Harbor", "outcome": "saved"},
        ],
    })

    response = director_ask(match, "Who won the penalty shootout?")

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert "1" in response["answer"]
    assert "0" in response["answer"]
    assert "winner is not yet established" in response["answer"]
    assert response["evidence_event_ids"] == ["p1", "p2"]



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_specific_penalty_kick_has_precise_evidence(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "specific-kick",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
            {"id": "p2", "order": 2, "team": "Harbor", "outcome": "saved"},
        ],
    })

    response = director_ask(match, "What happened on penalty kick 2?")

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is True
    assert "Harbor" in response["answer"]
    assert "saved" in response["answer"].lower()
    assert response["evidence_event_ids"] == ["p2"]



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_unrecorded_penalty_kick_is_declined(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "missing-kick",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
            {"id": "p2", "order": 2, "team": "Harbor", "outcome": "saved"},
        ],
    })

    response = director_ask(match, "What happened on penalty kick 99?")

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert "not recorded" in response["answer"].lower()
    assert response["evidence_event_ids"] == []



@pytest.mark.parametrize(
    "question",
    [
        "What happened on the penalty kick in the first half?",
        "Was the penalty kick scored during regular time?",
        "Who took the penalty kick at minute 35?",
    ],
)
def test_regular_penalty_is_not_shootout_question(question):
    from vybe.questions import is_shootout_question

    assert is_shootout_question(question) is False



@pytest.mark.parametrize(
    "question",
    [
        "Who scored the penalty kick?",
        "Was the penalty saved?",
        "What happened with the penalty?",
        "Who took the penalty?",
    ],
)
def test_ambiguous_penalty_question_is_not_assumed_shootout(question):
    from vybe.questions import is_shootout_question

    assert is_shootout_question(question) is False



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_ambiguous_penalty_question_does_not_invent_answer(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "ambiguous-penalty",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "regular",
    })

    response = director_ask(match, "Who scored the penalty kick?")

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert response["evidence_event_ids"] == []



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_unrelated_goal_does_not_prove_penalty(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "unrelated-goal",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "match_format": "regular",
        "events": [
            {
                "id": "e1",
                "minute": 25,
                "second": 0,
                "team": "Aurora",
                "type": "goal",
            }
        ],
    })

    response = director_ask(match, "Who scored the penalty kick?")

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert response["evidence_event_ids"] == []



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_timed_goal_does_not_prove_penalty(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "timed-penalty",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "match_format": "regular",
        "events": [
            {
                "id": "e1",
                "minute": 25,
                "second": 0,
                "team": "Aurora",
                "type": "goal",
            }
        ],
    })

    response = director_ask(
        match,
        "Who scored the penalty kick at minute 25?",
    )

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert response["evidence_event_ids"] == []



@pytest.mark.parametrize(
    "question",
    [
        "How many penalties were awarded during regular time?",
        "Were there any penalties in the first half?",
        "Which team received more penalties during the match?",
    ],
)
def test_regular_match_penalties_are_not_shootout(question):
    from vybe.questions import is_shootout_question

    assert is_shootout_question(question) is False



@pytest.mark.parametrize(
    "provider", ["ollama", "foundry", "deterministic"]
)
def test_shootout_saved_kicks_count(monkeypatch, provider):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    provider_calls = []

    def forbidden_provider_call(name):
        def reject(*args, **kwargs):
            provider_calls.append(name)
            raise AssertionError(f"Unexpected {name} call")
        return reject

    monkeypatch.setattr(
        "vybe.director_ollama._select_tool",
        forbidden_provider_call("ollama"),
    )
    monkeypatch.setattr(
        "vybe.director_agent._select_tool",
        forbidden_provider_call("foundry"),
    )

    match = MatchDefinition.model_validate({
        "match_id": "saved-kicks-count",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {"id": "p1", "order": 1, "team": "Aurora", "outcome": "saved"},
            {"id": "p2", "order": 2, "team": "Harbor", "outcome": "scored"},
            {"id": "p3", "order": 3, "team": "Aurora", "outcome": "missed"},
            {"id": "p4", "order": 4, "team": "Harbor", "outcome": "saved"},
        ],
    })

    response = director_ask(
        match,
        "How many penalties were saved in the shootout?",
    )

    assert provider_calls == []
    assert response["generation_mode"] == "deterministic"
    assert response["supported"] is False
    assert "so far" in response["answer"].lower()
    assert "2" in response["answer"]
    assert "saved" in response["answer"].lower()
    assert response["evidence_event_ids"] == ["p1", "p4"]



@pytest.mark.parametrize("provider", ["ollama", "foundry", "deterministic"])
@pytest.mark.parametrize("completed", [False, True])
def test_shootout_zero_saved_kicks_completeness(monkeypatch, provider, completed):
    monkeypatch.setenv("VYBE_DIRECTOR_PROVIDER", provider)

    match = MatchDefinition.model_validate({
        "match_id": "zero-saves",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {
                "id": f"p{i}",
                "order": i,
                "team": "Aurora" if i % 2 else "Harbor",
                "outcome": "scored" if i % 2 else "missed",
            }
            for i in range(1, 7 if completed else 3)
        ],
    })

    response = director_ask(
        match, "How many penalties were saved in the shootout?"
    )

    assert response["generation_mode"] == "deterministic"
    assert "0" in response["answer"]
    assert response["evidence_event_ids"] == []

    if completed:
        assert response["supported"] is True
    else:
        assert "so far" in response["answer"].lower()
        assert response["supported"] is False
