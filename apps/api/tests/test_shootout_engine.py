"""Deterministic penalty shootout scoring tests."""

import pytest

from vybe.models import MatchDefinition
from vybe.shootout import evaluate_shootout


def match_with_kicks(kicks):
    return MatchDefinition.model_validate({
        "match_id": "shootout-engine",
        "home_team": "Aurora",
        "away_team": "Harbor",
        "events": [],
        "match_format": "extra_time",
        "penalty_shootout": [
            {
                "id": f"p{i}",
                "order": i,
                "team": "Aurora" if i % 2 else "Harbor",
                "outcome": outcome,
            }
            for i, outcome in enumerate(kicks, start=1)
        ],
    })


def test_shootout_still_in_progress():
    result = evaluate_shootout(
        match_with_kicks(["scored", "missed"])
    )
    assert result.home_score == 1
    assert result.away_score == 0
    assert result.winner is None
    assert result.status == "in_progress"


def test_shootout_early_clinch():
    result = evaluate_shootout(
        match_with_kicks([
            "scored", "missed",
            "scored", "missed",
            "scored", "missed",
        ])
    )
    assert result.home_score == 3
    assert result.away_score == 0
    assert result.winner == "Aurora"
    assert result.status == "completed"


def test_shootout_sudden_death():
    result = evaluate_shootout(
        match_with_kicks([
            "scored", "scored",
            "scored", "scored",
            "scored", "scored",
            "scored", "scored",
            "scored", "scored",
            "scored", "missed",
        ])
    )
    assert result.home_score == 6
    assert result.away_score == 5
    assert result.winner == "Aurora"
    assert result.status == "completed"


def test_single_kick_does_not_establish_winner():
    result = evaluate_shootout(
        match_with_kicks(["scored"])
    )
    assert result.home_score == 1
    assert result.away_score == 0
    assert result.winner is None
    assert result.status == "in_progress"



def test_rejects_kicks_after_early_clinch():
    match = match_with_kicks([
        "scored", "missed",
        "scored", "missed",
        "scored", "missed",
        "scored",
    ])

    with pytest.raises(ValueError, match="after shootout completion"):
        evaluate_shootout(match)


def test_rejects_kicks_after_sudden_death():
    match = match_with_kicks([
        "scored", "scored",
        "scored", "scored",
        "scored", "scored",
        "scored", "scored",
        "scored", "scored",
        "scored", "missed",
        "scored",
    ])

    with pytest.raises(ValueError, match="after shootout completion"):
        evaluate_shootout(match)



def test_shootout_can_continue_beyond_30_kicks():
    # Both teams score 20 kicks each: still tied after 40 kicks.
    match = match_with_kicks(["scored"] * 40)

    result = evaluate_shootout(match)

    assert result.home_score == 20
    assert result.away_score == 20
    assert result.winner is None
    assert result.status == "in_progress"



def test_long_shootout_decided_at_kick_42():
    result = evaluate_shootout(
        match_with_kicks(["scored"] * 40 + ["scored", "missed"])
    )

    assert result.home_score == 21
    assert result.away_score == 20
    assert result.winner == "Aurora"
    assert result.status == "completed"


def test_away_team_starts_and_wins():
    match = match_with_kicks([
        "scored", "missed",
        "scored", "missed",
        "scored", "missed",
    ])

    # Reverse the participating teams' roles in the kick sequence.
    for kick in match.penalty_shootout:
        kick.team = (
            "Harbor" if kick.team == "Aurora" else "Aurora"
        )

    result = evaluate_shootout(match)

    assert result.home_score == 0
    assert result.away_score == 3
    assert result.winner == "Harbor"
    assert result.status == "completed"


def test_sudden_death_odd_kick_is_not_a_win():
    result = evaluate_shootout(
        match_with_kicks(["scored"] * 11)
    )

    assert result.home_score == 6
    assert result.away_score == 5
    assert result.winner is None
    assert result.status == "in_progress"
