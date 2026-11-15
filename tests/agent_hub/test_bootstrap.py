
from pathlib import Path
from typing import cast

import pytest

from agent_hub.agents.agent_builder import AgentBuilder
from agent_hub.agents.bookmark_agent import BookmarkAgent
from agent_hub.agents.git_agent import GitAgent
from agent_hub.agents.project_ideas_agent import ProjectIdeasAgent
from agent_hub.bootstrap import build_agent_registry
from agent_hub.core import (
    AgentRegistry,
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)


class StubInterpreter(Interpreter):
    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        raise NotImplementedError


@pytest.fixture
def interpreters() -> dict[str, Interpreter]:
    return {
        "git-agent": StubInterpreter(),
        "agent-builder": StubInterpreter(),
        "bookmark-agent": StubInterpreter(),
        "project-ideas-agent": StubInterpreter(),
    }


def test_build_agent_registry_registers_all_agents(
    interpreters: dict[str, Interpreter],
) -> None:
    registry = build_agent_registry(interpreters)

    assert isinstance(registry, AgentRegistry)

    agents = registry.list()

    assert len(agents) == 4

    assert isinstance(registry.get("git-agent"), GitAgent)
    assert isinstance(registry.get("agent-builder"), AgentBuilder)
    assert isinstance(registry.get("bookmark-agent"), BookmarkAgent)
    assert isinstance(
        registry.get("project-ideas-agent"),
        ProjectIdeasAgent,
    )


def test_build_agent_registry_injects_interpreters(
    interpreters: dict[str, Interpreter],
) -> None:
    registry = build_agent_registry(interpreters)

    git_agent = cast(GitAgent, registry.get("git-agent"))
    agent_builder = cast(AgentBuilder, registry.get("agent-builder"))
    bookmark_agent = cast(BookmarkAgent, registry.get("bookmark-agent"))
    project_ideas_agent = cast(
        ProjectIdeasAgent,
        registry.get("project-ideas-agent"),
    )

    assert git_agent._interpreter is interpreters["git-agent"]
    assert agent_builder._interpreter is interpreters["agent-builder"]
    assert bookmark_agent._interpreter is interpreters["bookmark-agent"]
    assert project_ideas_agent._interpreter is interpreters["project-ideas-agent"]


def test_build_agent_registry_configures_repository_paths(
    interpreters: dict[str, Interpreter],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import agent_hub.bootstrap as bootstrap

    bookmarks_path = tmp_path / "bookmarks"
    project_ideas_path = tmp_path / "project-ideas"

    monkeypatch.setattr(
        bootstrap,
        "BOOKMARKS_PATH",
        bookmarks_path,
    )
    monkeypatch.setattr(
        bootstrap,
        "PROJECT_IDEAS_PATH",
        project_ideas_path,
    )

    registry = build_agent_registry(interpreters)

    bookmark_agent = cast(
        BookmarkAgent,
        registry.get("bookmark-agent"),
    )
    project_ideas_agent = cast(
        ProjectIdeasAgent,
        registry.get("project-ideas-agent"),
    )

    assert bookmark_agent._bookmarks_path == bookmarks_path.resolve()
    assert project_ideas_agent._project_ideas_path == (
        project_ideas_path.resolve()
    )


def test_build_agent_registry_rejects_missing_interpreters() -> None:
    with pytest.raises(
        ValueError,
        match="Missing interpreters for agents",
    ):
        build_agent_registry({})
