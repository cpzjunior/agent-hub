from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from agent_hub.agents.writing_assistant.models.article import (
    ArticleArtifact,
    ArticleModel,
    ArticleReview,
)


class DiscussionMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    content: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class ArticleExploration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    initial_idea: str | None = None
    thesis: str | None = None
    arguments: list[str] = Field(default_factory=list)
    counterarguments: list[str] = Field(default_factory=list)
    implications: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)


class ArticleRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    number: int
    title: str | None = None
    subtitle: str | None = None
    content: str
    reason: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class WritingSession(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4)
    article: ArticleModel = Field(default_factory=ArticleModel)
    exploration: ArticleExploration = Field(
        default_factory=ArticleExploration
    )
    discussion: list[DiscussionMessage] = Field(default_factory=list)
    revisions: list[ArticleRevision] = Field(default_factory=list)
    artifacts: list[ArticleArtifact] = Field(default_factory=list)
    last_review: ArticleReview | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
