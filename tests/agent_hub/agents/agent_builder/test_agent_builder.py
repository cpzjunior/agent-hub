
from unittest.mock import AsyncMock

import pytest

from agent_hub.agents.agent_builder import (
    AgentBuilder,
    AgentBuilderRequest,
)
from agent_hub.core import (
    InterpretationResult,
    Interpreter,
)


@pytest.fixture
def interpreter() -> AsyncMock:
    return AsyncMock(spec=Interpreter)


@pytest.fixture
def agent(interpreter: AsyncMock) -> AgentBuilder:
    return AgentBuilder(interpreter=interpreter)


def interpretation(
    skill_name: str | None = "agent-manage",
    parameters: dict[str, object] | None = None,
    missing_inputs: list[str] | None = None,
    message: str | None = None,
) -> InterpretationResult:
    return InterpretationResult(
        skill_name=skill_name,
        parameters=parameters or {},
        missing_inputs=missing_inputs or [],
        message=message,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("skill_name", "artifact_path"),
    [
        ("agent-manage", "agents/example_agent/agent.py"),
        ("skill-manage", "agents/example_agent/skills/example/SKILL.md"),
        ("tool-manage", "agents/example_agent/tools/example.py"),
    ],
)
async def test_create_artifact(
    agent: AgentBuilder,
    interpreter: AsyncMock,
    skill_name: str,
    artifact_path: str,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name=skill_name,
        parameters={
            "artifacts": [
                {
                    "path": artifact_path,
                    "content": "Generated content",
                    "action": "create",
                }
            ],
            "tests_relevant": True,
            "tests_rationale": "The artifact contains executable logic.",
        },
        message="Artifact generated.",
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction=f"Create a new {skill_name} artifact."
        )
    )

    assert result.status == "proposed"
    assert result.skill_name == skill_name
    assert len(result.artifacts) == 1
    assert result.artifacts[0].path == artifact_path
    assert result.artifacts[0].content == "Generated content"
    assert result.artifacts[0].action == "create"
    assert result.tests_relevant is True

    interpreter.interpret.assert_awaited_once()


@pytest.mark.asyncio
async def test_improve_skill(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name="skill-manage",
        parameters={
            "artifacts": [
                {
                    "path": "agents/example/skills/example/SKILL.md",
                    "content": "Improved skill content",
                    "action": "update",
                }
            ],
            "tests_relevant": False,
            "tests_rationale": (
                "Skill instructions do not require automated tests."
            ),
        },
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Improve the existing example skill."
        )
    )

    assert result.status == "proposed"
    assert result.artifacts[0].action == "update"
    assert result.tests_relevant is False
    assert result.tests_rationale is not None


@pytest.mark.asyncio
async def test_unsupported_skill(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name=None,
        message="No supported skill matches the request.",
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Perform an unsupported operation."
        )
    )

    assert result.status == "unsupported"
    assert result.artifacts == []


@pytest.mark.asyncio
async def test_missing_inputs(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name="agent-manage",
        missing_inputs=["agent_name"],
        message="An agent name is required.",
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "needs_input"
    assert result.required_input == "agent_name"
    assert result.artifacts == []


@pytest.mark.asyncio
async def test_invalid_artifact_path(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name="agent-manage",
        parameters={
            "artifacts": [
                {
                    "path": "../outside.py",
                    "content": "Invalid content",
                    "action": "create",
                }
            ],
        },
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "failed"
    assert "Invalid generated artifacts" in result.message


@pytest.mark.asyncio
async def test_absolute_artifact_path_is_rejected(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name="agent-manage",
        parameters={
            "artifacts": [
                {
                    "path": "/tmp/outside.py",
                    "content": "Invalid content",
                    "action": "create",
                }
            ],
        },
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "failed"


@pytest.mark.asyncio
async def test_duplicate_artifact_paths_are_rejected(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    artifact = {
        "path": "agents/example/agent.py",
        "content": "Generated content",
        "action": "create",
    }

    interpreter.interpret.return_value = interpretation(
        skill_name="agent-manage",
        parameters={
            "artifacts": [artifact, artifact],
        },
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "failed"
    assert "duplicate paths" in result.message


@pytest.mark.asyncio
async def test_agent_without_interpreter() -> None:
    agent = AgentBuilder()

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "needs_input"
    assert result.required_input == "interpreter"


@pytest.mark.asyncio
async def test_interpreter_receives_loaded_skills(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name=None,
    )

    await agent.run(
        AgentBuilderRequest(
            instruction="Create something."
        )
    )

    interpreter.interpret.assert_awaited_once()

    request = interpreter.interpret.await_args.args[0]

    skill_names = {
        skill.name for skill in request.skills
    }

    assert skill_names == {
        "agent-manage",
        "skill-manage",
        "tool-manage",
    }


@pytest.mark.asyncio
async def test_invalid_artifact_structure_is_rejected(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name="agent-manage",
        parameters={
            "artifacts": [
                {
                    "path": "agents/example/agent.py",
                    "action": "create",
                }
            ],
        },
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "failed"
    assert "Invalid generated artifacts" in result.message


@pytest.mark.asyncio
async def test_interpreter_exception_returns_failed(
    agent: AgentBuilder,
    interpreter: AsyncMock,
) -> None:
    interpreter.interpret.side_effect = RuntimeError(
        "Provider unavailable."
    )

    result = await agent.run(
        AgentBuilderRequest(
            instruction="Create an agent."
        )
    )

    assert result.status == "failed"
    assert "Interpreter execution failed" in result.message
    assert "Provider unavailable" in result.message
