
from typing import Any, cast

from mcp.server import MCPServer

from agent_hub.agents.agent_builder.agent import AgentBuilderRequest
from agent_hub.agents.bookmark_agent.agent import BookmarkAgentRequest
from agent_hub.agents.git_agent.agent import GitAgentRequest
from agent_hub.agents.project_ideas_agent.agent import ProjectIdeasAgentRequest
from agent_hub.core.agent_registry import AgentRegistry


def create_mcp_server(registry: AgentRegistry) -> MCPServer:
    """Create an MCP server exposing the registered agents."""

    server = MCPServer("Agent Hub")

    git_agent = registry.get("git-agent")

    @server.tool(
        name="git_agent",
        description=git_agent.description,
    )
    async def run_git_agent(
        request: GitAgentRequest,
    ) -> dict[str, Any]:
        """Execute a Git operation in a repository."""
        result = await git_agent.run(request)
        return cast(dict[str, Any], result.model_dump(mode="json"))

    agent_builder = registry.get("agent-builder")

    @server.tool(
        name="agent_builder",
        description=agent_builder.description,
    )
    async def run_agent_builder(
        request: AgentBuilderRequest,
    ) -> dict[str, Any]:
        """Create or improve an agent, skill or tool."""
        result = await agent_builder.run(request)
        return cast(dict[str, Any], result.model_dump(mode="json"))

    bookmark_agent = registry.get("bookmark-agent")

    @server.tool(
        name="bookmark_agent",
        description=bookmark_agent.description,
    )
    async def run_bookmark_agent(
        request: BookmarkAgentRequest,
    ) -> dict[str, Any]:
        """Create, extract, describe or classify a bookmark."""
        result = await bookmark_agent.run(request)
        return cast(dict[str, Any], result.model_dump(mode="json"))

    project_ideas_agent = registry.get("project-ideas-agent")

    @server.tool(
        name="project_ideas_agent",
        description=project_ideas_agent.description,
    )
    async def run_project_ideas_agent(
        request: ProjectIdeasAgentRequest,
    ) -> dict[str, Any]:
        """Generate a project idea document."""
        result = await project_ideas_agent.run(request)
        return cast(dict[str, Any], result.model_dump(mode="json"))

    return server
