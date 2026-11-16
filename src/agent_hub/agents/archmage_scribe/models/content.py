from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class CanonicalRelation(StrEnum):
    """Relationship between proposed content and established canon."""

    CONSISTENT = "consistent"
    COMPATIBLE_EXTENSION = "compatible_extension"
    TENSION = "tension"
    CONTRADICTION = "contradiction"
    UNKNOWN = "unknown"


class CreatedContent(BaseModel):
    """A proposed text produced during an Archmage Scribe session."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    content: str
    content_type: str | None = None
    fictional_author: str | None = None
    historical_context: str | None = None
    canonical_relation: CanonicalRelation = CanonicalRelation.UNKNOWN
    canonical_references: list[str] = Field(default_factory=list)