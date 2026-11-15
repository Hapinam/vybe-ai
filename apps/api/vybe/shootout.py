"""Deterministic football penalty shootout evaluation."""

from dataclasses import dataclass

from vybe.models import MatchDefinition, PenaltyOutcome


@dataclass(frozen=True)
class ShootoutResult:
    home_score: int
    away_score: int
    winner: str | None
    status: str


def evaluate_shootout(match: MatchDefinition) -> ShootoutResult:
    """Evaluate recorded kicks without predicting future outcomes."""

    kicks = sorted(match.penalty_shootout, key=lambda kick: kick.order)

    home_score = 0
    away_score = 0
    home_taken = 0
    away_taken = 0

    for index, kick in enumerate(kicks):
        scored = kick.outcome == PenaltyOutcome.scored

        if kick.team == match.home_team:
            home_taken += 1
            if scored:
                home_score += 1
        else:
            away_taken += 1
            if scored:
                away_score += 1

        home_remaining = max(0, 5 - home_taken)
        away_remaining = max(0, 5 - away_taken)

        # A team wins early if the opponent cannot catch up.
        if home_taken <= 5 and away_taken <= 5 and home_score > away_score + away_remaining:
            if index != len(kicks) - 1:
                raise ValueError("kick recorded after shootout completion")
            return ShootoutResult(
                home_score, away_score, match.home_team, "completed"
            )

        if home_taken <= 5 and away_taken <= 5 and away_score > home_score + home_remaining:
            if index != len(kicks) - 1:
                raise ValueError("kick recorded after shootout completion")
            return ShootoutResult(
                home_score, away_score, match.away_team, "completed"
            )

        # After five attempts each, sudden death is decided
        # only after both teams have taken the same number of kicks.
        if (
            home_taken >= 5
            and away_taken >= 5
            and home_taken == away_taken
            and home_score != away_score
        ):
            winner = (
                match.home_team
                if home_score > away_score
                else match.away_team
            )
            if index != len(kicks) - 1:
                raise ValueError("kick recorded after shootout completion")
            return ShootoutResult(
                home_score, away_score, winner, "completed"
            )

    return ShootoutResult(
        home_score, away_score, None, "in_progress"
    )
