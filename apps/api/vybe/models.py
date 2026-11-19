"""Validated contracts for synthetic football match events."""

from enum import Enum
from pydantic import BaseModel, Field, model_validator


class EventType(str, Enum):
    kickoff = "kickoff"
    pass_completed = "pass_completed"
    shot = "shot"
    goal = "goal"
    halftime = "halftime"
    fulltime = "fulltime"


class MatchFormat(str, Enum):
    unknown = "unknown"
    regular = "regular"
    extra_time = "extra_time"


class PenaltyOutcome(str, Enum):
    scored = "scored"
    saved = "saved"
    missed = "missed"


class PenaltyKick(BaseModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"\S")
    order: int = Field(ge=1)
    team: str = Field(min_length=1, max_length=100, pattern=r"\S")
    outcome: PenaltyOutcome


class MatchEvent(BaseModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"\S")
    minute: int = Field(ge=0, le=130)
    second: int = Field(default=0, ge=0, le=59)
    team: str | None = Field(default=None, max_length=100)
    player: str | None = Field(default=None, max_length=100)
    type: EventType

    @model_validator(mode="after")
    def require_team_for_play(self):
        if self.type in {EventType.pass_completed, EventType.shot, EventType.goal} and not self.team:
            raise ValueError("team is required for on-field actions")
        return self


class MatchDefinition(BaseModel):
    match_id: str = Field(min_length=1, max_length=80, pattern=r"\S")
    home_team: str = Field(min_length=1, max_length=100, pattern=r"\S")
    away_team: str = Field(min_length=1, max_length=100, pattern=r"\S")
    events: list[MatchEvent] = Field(max_length=500)
    match_format: MatchFormat = MatchFormat.unknown
    penalty_shootout: list[PenaltyKick] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_events(self):
        if self.home_team == self.away_team:
            raise ValueError("home and away teams must differ")
        ids = [event.id for event in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("event IDs must be unique")
        for event in self.events:
            if event.team is not None and event.team not in {self.home_team, self.away_team}:
                raise ValueError(f"unknown team in event {event.id}")

        kicks = self.penalty_shootout
        orders = [kick.order for kick in kicks]
        kick_ids = [kick.id for kick in kicks]

        if len(orders) != len(set(orders)):
            raise ValueError("penalty kick orders must be unique")
        if sorted(orders) != list(range(1, len(orders) + 1)):
            raise ValueError("penalty kick orders must be contiguous starting at 1")
        if len(kick_ids) != len(set(kick_ids)):
            raise ValueError("penalty kick IDs must be unique")
        if set(kick_ids) & set(ids):
            raise ValueError("penalty kick IDs must not overlap match event IDs")
        if any(kick.team not in {self.home_team, self.away_team} for kick in kicks):
            raise ValueError("unknown team in penalty shootout")

        ordered_kicks = sorted(kicks, key=lambda kick: kick.order)
        for previous, current in zip(ordered_kicks, ordered_kicks[1:]):
            if previous.team == current.team:
                raise ValueError("penalty shootout teams must alternate")
        if kicks and self.match_format != MatchFormat.extra_time:
            raise ValueError("penalty shootout requires extra_time match format")
        return self
