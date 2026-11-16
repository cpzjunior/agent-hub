from collections.abc import Mapping
from pathlib import Path

from agent_hub.agents.agent_builder import AgentBuilder
from agent_hub.agents.bookmark_agent import BookmarkAgent
from agent_hub.agents.decision_architect import DecisionArchitect
from agent_hub.agents.git_agent import GitAgent
from agent_hub.agents.project_ideas_agent import ProjectIdeasAgent
from agent_hub.agents.writing_assistant import WritingAssistant
from agent_hub.core.agent_registry import AgentRegistry
from agent_hub.core.interpreter import Interpreter

REPOSITORIES_PATH = Path.home() / "source" / "repos"

BOOKMARKS_PATH = REPOSITORIES_PATH / "bookmarks"
PROJECT_IDEAS_PATH = REPOSITORIES_PATH / "project-ideas"

SHARED_SKILLS_PATH = Path(__file__).parent / "shared" / "skills"

AGENT_NAMES = {
    "git-agent",
    "agent-builder",
    "bookmark-agent",
    "project-ideas-agent",
    "decision-architect",
    "writing-assistant",
}


def build_agent_registry(
    interpreters: Mapping[str, Interpreter],
) -> AgentRegistry:
    """Create and register all available agents."""

    missing_interpreters = AGENT_NAMES - interpreters.keys()

    if missing_interpreters:
        missing = ", ".join(sorted(missing_interpreters))
        raise ValueError(
            f"Missing interpreters for agents: {missing}"
        )

    registry = AgentRegistry()

    registry.register(
        GitAgent(interpreter=interpreters["git-agent"])
    )

    registry.register(
        AgentBuilder(interpreter=interpreters["agent-builder"])
    )

    registry.register(
        BookmarkAgent(
            interpreter=interpreters["bookmark-agent"],
            bookmarks_path=BOOKMARKS_PATH,
        )
    )

    registry.register(
        ProjectIdeasAgent(
            interpreter=interpreters["project-ideas-agent"],
            project_ideas_path=PROJECT_IDEAS_PATH,
        )
    )

    registry.register(
        DecisionArchitect(
            interpreter=interpreters["decision-architect"]
        )
    )

    registry.register(
        WritingAssistant(
            interpreter=interpreters["writing-assistant"],
            agent_path=Path(__file__).parent / "agents" / "writing_assistant",
            shared_skills_path=SHARED_SKILLS_PATH,
        )
    )

    return registry
