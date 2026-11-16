from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ArticleLanguage(StrEnum):
    PT_BR = "pt-BR"
    EN = "en"
    ES = "es"
    IT = "it"


class ArticleArtifactType(StrEnum):
    SUMMARY = "summary"
    TRANSLATION = "translation"
    AI_CONSOLIDATION = "ai-consolidation"


class ArticleModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    id: UUID = Field(default_factory=uuid4)
    language: ArticleLanguage = ArticleLanguage.PT_BR
    title: str | None = None
    subtitle: str | None = None
    thesis: str | None = None
    content: str = ""
    tags: list[str] = Field(default_factory=list)


class ArticleArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    type: ArticleArtifactType
    language: ArticleLanguage
    content: str
    source_revision: int | None = None


class ArticleReviewStatus(StrEnum):
    READY = "ready"
    READY_WITH_MINOR_CHANGES = "ready_with_minor_changes"
    NEEDS_REVISION = "needs_revision"
    NOT_READY = "not_ready"


class ArticleReview(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    status: ArticleReviewStatus
    strengths: list[str] = Field(default_factory=list)
    substantive_issues: list[str] = Field(default_factory=list)
    missing_arguments: list[str] = Field(default_factory=list)
    editorial_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
