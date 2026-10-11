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


class MatchEvent(BaseModel):
    id: str = Field(min_length=1, pattern=r"\\S")
    minute: int = Field(ge=0, le=130)
    second: int = Field(default=0, ge=0, le=59)
    team: str | None = None
    player: str | None = None
    type: EventType

    @model_validator(mode="after")
    def require_team_for_play(self):
        if self.type in {EventType.pass_completed, EventType.shot, EventType.goal} and not self.team:
            raise ValueError("team is required for on-field actions")
        return self


class MatchDefinition(BaseModel):
    match_id: str = Field(min_length=1, pattern=r"\\S")
    home_team: str = Field(min_length=1, pattern=r"\\S")
    away_team: str = Field(min_length=1, pattern=r"\\S")
    events: list[MatchEvent]

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
        return self
