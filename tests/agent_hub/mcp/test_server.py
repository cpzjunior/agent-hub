
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest
from mcp import Client

from agent_hub.agents.agent_builder.agent import AgentBuilderRequest
from agent_hub.agents.bookmark_agent.agent import BookmarkAgentRequest
from agent_hub.agents.git_agent.agent import GitAgentRequest
from agent_hub.agents.project_ideas_agent.agent import ProjectIdeasAgentRequest
from agent_hub.core import Agent, AgentRegistry
from agent_hub.mcp.server import create_mcp_server


class StubResult:
    def model_dump(self, *, mode: str) -> dict[str, Any]:
        return {"status": "completed", "message": "Test result"}


@pytest.fixture
def agents() -> dict[str, Mock]:
    definitions = {
        "git-agent": "Git agent description",
        "agent-builder": "Agent builder description",
        "bookmark-agent": "Bookmark agent description",
        "project-ideas-agent": "Project ideas agent description",
    }

    result = {}

    for name, description in definitions.items():
        agent = Mock()
        agent.name = name
        agent.description = description
        agent.run = AsyncMock(return_value=StubResult())
        result[name] = agent

    return result


@pytest.fixture
def server(agents: dict[str, Mock]) -> Any:
    registry = AgentRegistry()

    for agent in agents.values():
        registry.register(cast(Agent, agent))

    return create_mcp_server(registry)


@pytest.mark.asyncio
async def test_server_registers_all_agent_tools(server: Any) -> None:
    async with Client(server) as client:
        result = await client.list_tools()

    tool_names = {tool.name for tool in result.tools}

    assert tool_names == {
        "git_agent",
        "agent_builder",
        "bookmark_agent",
        "project_ideas_agent",
    }


@pytest.mark.asyncio
async def test_server_exposes_agent_descriptions(
    server: Any,
    agents: dict[str, Mock],
) -> None:
    async with Client(server) as client:
        result = await client.list_tools()

    tools = {tool.name: tool for tool in result.tools}

    assert tools["git_agent"].description == agents["git-agent"].description
    assert tools["agent_builder"].description == agents["agent-builder"].description
    assert tools["bookmark_agent"].description == agents["bookmark-agent"].description
    assert (
        tools["project_ideas_agent"].description
        == agents["project-ideas-agent"].description
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_name", "arguments", "agent_name", "request_type"),
    [
        (
            "git_agent",
            {"request": {"instruction": "Show repository status"}},
            "git-agent",
            GitAgentRequest,
        ),
        (
            "agent_builder",
            {"request": {"instruction": "Create a new agent"}},
            "agent-builder",
            AgentBuilderRequest,
        ),
        (
            "bookmark_agent",
            {"request": {"url": "https://example.com"}},
            "bookmark-agent",
            BookmarkAgentRequest,
        ),
        (
            "project_ideas_agent",
            {"request": {"instruction": "Create a project idea"}},
            "project-ideas-agent",
            ProjectIdeasAgentRequest,
        ),
    ],
)
async def test_tool_delegates_execution_to_agent(
    server: Any,
    agents: dict[str, Mock],
    tool_name: str,
    arguments: dict[str, Any],
    agent_name: str,
    request_type: type,
) -> None:
    async with Client(server) as client:
        result = await client.call_tool(tool_name, arguments)

    assert result.is_error is False
    assert result.structured_content == {
        "status": "completed",
        "message": "Test result",
    }

    agent = agents[agent_name]
    agent.run.assert_awaited_once()

    request = agent.run.await_args.args[0]
    assert isinstance(request, request_type)
