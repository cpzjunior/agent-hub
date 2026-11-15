from agent_hub.core.agent import Agent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        if agent.name in self._agents:
            raise ValueError(f"Agent already registered: {agent.name}")

        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent:
        try:
            return self._agents[name]
        except KeyError:
            raise KeyError(f"Agent not found: {name}") from None

    def list(self) -> list[Agent]:
        return list(self._agents.values())