"""Contracts for match format and penalty shootout data."""

import pytest
from pydantic import ValidationError

from vybe.models import MatchDefinition


def base_match(**overrides):
    data = {
        "match_id": "shootout-contract",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
    }
    data.update(overrides)
    return data


def test_legacy_match_remains_valid():
    match = MatchDefinition.model_validate(base_match())
    assert match.events == []
    assert match.match_format.value == "unknown"
    assert match.penalty_shootout == []


def test_extra_time_format_is_explicit():
    match = MatchDefinition.model_validate(
        base_match(match_format="extra_time")
    )
    assert match.match_format.value == "extra_time"


def test_shootout_kicks_have_order_and_outcome():
    match = MatchDefinition.model_validate(
        base_match(
            match_format="extra_time",
            penalty_shootout=[
                {
                    "id": "p1",
                    "order": 1,
                    "team": "Aurora",
                    "outcome": "scored",
                },
                {
                    "id": "p2",
                    "order": 2,
                    "team": "Harbor",
                    "outcome": "saved",
                },
            ],
        )
    )

    assert len(match.penalty_shootout) == 2
    assert match.penalty_shootout[0].order == 1
    assert match.penalty_shootout[1].outcome.value == "saved"


def test_duplicate_shootout_order_is_rejected():
    with pytest.raises(ValidationError):
        MatchDefinition.model_validate(
            base_match(
                match_format="extra_time",
                penalty_shootout=[
                    {
                        "id": "p1",
                        "order": 1,
                        "team": "Aurora",
                        "outcome": "scored",
                    },
                    {
                        "id": "p2",
                        "order": 1,
                        "team": "Harbor",
                        "outcome": "missed",
                    },
                ],
            )
        )



def test_shootout_order_must_be_contiguous():
    with pytest.raises(ValidationError):
        MatchDefinition.model_validate(
            base_match(
                match_format="extra_time",
                penalty_shootout=[
                    {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
                    {"id": "p3", "order": 3, "team": "Harbor", "outcome": "missed"},
                ],
            )
        )


def test_shootout_rejects_unknown_team():
    with pytest.raises(ValidationError):
        MatchDefinition.model_validate(
            base_match(
                match_format="extra_time",
                penalty_shootout=[
                    {"id": "p1", "order": 1, "team": "Other", "outcome": "scored"},
                ],
            )
        )


def test_shootout_rejects_id_shared_with_match_event():
    with pytest.raises(ValidationError):
        MatchDefinition.model_validate(
            base_match(
                match_format="extra_time",
                events=[
                    {"id": "p1", "minute": 10, "team": "Aurora", "type": "goal"},
                ],
                penalty_shootout=[
                    {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
                ],
            )
        )



def test_shootout_rejects_consecutive_kicks_by_same_team():
    with pytest.raises(ValidationError):
        MatchDefinition.model_validate(
            base_match(
                match_format="extra_time",
                penalty_shootout=[
                    {"id": "p1", "order": 1, "team": "Aurora", "outcome": "scored"},
                    {"id": "p2", "order": 2, "team": "Aurora", "outcome": "saved"},
                ],
            )
        )


def test_away_team_can_take_first_shootout_kick():
    match = MatchDefinition.model_validate(
        base_match(
            match_format="extra_time",
            penalty_shootout=[
                {"id": "p1", "order": 1, "team": "Harbor", "outcome": "scored"},
                {"id": "p2", "order": 2, "team": "Aurora", "outcome": "missed"},
            ],
        )
    )

    assert [kick.team for kick in match.penalty_shootout] == [
        "Harbor", "Aurora"
    ]
