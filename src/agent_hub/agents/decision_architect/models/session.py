
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from agent_hub.agents.decision_architect.models.decision import Decision


class EventType(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    INFORMATION_ADDED = "information_added"
    ALTERNATIVE_ADDED = "alternative_added"
    ALTERNATIVE_SELECTED = "alternative_selected"
    STATUS_CHANGED = "status_changed"
    REVIEWED = "reviewed"


class DecisionEvent(BaseModel):
    """Records a relevant event in the evolution of a decision."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: EventType
    target: str | None = None
    description: str
    rationale: str | None = None
    source: str = "user"


class DecisionSession(BaseModel):
    """In-memory working session for a Decision Architect interaction."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    id: str = Field(default_factory=lambda: str(uuid4()))
    decision: Decision = Field(default_factory=Decision)
    events: list[DecisionEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def record_event(self, event: DecisionEvent) -> None:
        self.events.append(event)
        self.updated_at = datetime.now(UTC)
