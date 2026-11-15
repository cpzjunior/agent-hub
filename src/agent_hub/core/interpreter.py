from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from agent_hub.core.skill import Skill


class InterpretationRequest(BaseModel):
    instruction: str
    skills: list[Skill]


class InterpretationResult(BaseModel):
    skill_name: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    missing_inputs: list[str] = Field(default_factory=list)
    message: str | None = None


class Interpreter(ABC):
    """Base contract for natural language interpreters."""

    @abstractmethod
    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        """Interpret a user instruction using available skills."""
        raise NotImplementedError