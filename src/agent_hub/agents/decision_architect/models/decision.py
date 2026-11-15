from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DecisionStatus(StrEnum):
    OPEN = "open"
    EXPLORING = "exploring"
    DECIDED = "decided"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class InformationClassification(StrEnum):
    FACT = "fact"
    HYPOTHESIS = "hypothesis"
    ASSUMPTION = "assumption"
    UNKNOWN = "unknown"


class InformationSource(StrEnum):
    USER = "user"
    EXTERNAL_EVIDENCE = "external_evidence"
    AGENT_INFERENCE = "agent_inference"
    UNSPECIFIED = "unspecified"


class DecisionModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class Domain(DecisionModel):
    description: str | None = None
    boundaries: list[str] = Field(default_factory=list)
    elements: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)


class EvidenceItem(DecisionModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    statement: str
    classification: InformationClassification
    source: InformationSource = InformationSource.UNSPECIFIED
    confidence: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = None


class Objective(DecisionModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    priority: int | None = Field(default=None, ge=1)
    success_criteria: list[str] = Field(default_factory=list)


class Risk(DecisionModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    likelihood: Literal["low", "medium", "high", "unknown"] = "unknown"
    impact: Literal["low", "medium", "high", "unknown"] = "unknown"
    response: str | None = None


class Alternative(DecisionModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str | None = None
    advantages: list[str] = Field(default_factory=list)
    disadvantages: list[str] = Field(default_factory=list)
    status: Literal["candidate", "selected", "rejected", "deferred"] = "candidate"


class Consequence(DecisionModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    nature: Literal["direct", "indirect"] = "direct"
    affected_parties: list[str] = Field(default_factory=list)
    time_horizon: str | None = None
    reversibility: Literal[
        "reversible",
        "partially_reversible",
        "irreversible",
        "unknown",
    ] = "unknown"


class Decision(DecisionModel):
    """Current, evolving representation of a single decision."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str | None = None
    description: str | None = None
    status: DecisionStatus = DecisionStatus.OPEN

    domain: Domain = Field(default_factory=Domain)
    context: str | None = None
    stakeholders: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    objectives: list[Objective] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list)
    consequences: list[Consequence] = Field(default_factory=list)

    evolution_notes: list[str] = Field(default_factory=list)
    related_decisions: dict[str, list[str]] = Field(default_factory=dict)
