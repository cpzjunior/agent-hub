from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Base contract for all Agent Hub agents."""

    name: str
    description: str

    @abstractmethod
    async def run(self, input: Any) -> Any:
        """Execute the agent and return its result."""
        raise NotImplementedError
