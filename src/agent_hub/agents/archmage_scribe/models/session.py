from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from agent_hub.agents.archmage_scribe.models.content import CreatedContent


class DiscussionMessage(BaseModel):
    """A user or assistant contribution to the current working discussion."""

    model_config = ConfigDict(extra="forbid")

    role: str
    content: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class ArchmageScribeSession(BaseModel):
    """Working context for an iterative worldbuilding or writing task."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4)
    initial_idea: str | None = None
    concepts: list[str] = Field(default_factory=list)
    established_definitions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    discussion: list[DiscussionMessage] = Field(default_factory=list)
    contents: list[CreatedContent] = Field(default_factory=list)
    canonical_references: list[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )