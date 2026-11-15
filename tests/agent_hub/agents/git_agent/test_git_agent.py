
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from agent_hub.agents.git_agent.agent import (
    GitAgent,
    GitAgentRequest,
)
from agent_hub.agents.git_agent.tools.git_cli import (
    GitCliInput,
    GitCliOutput,
    GitCliTool,
    GitOperation,
)
from agent_hub.core.interpreter import InterpretationResult


@pytest.fixture
def interpreter() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def tool() -> AsyncMock:
    mock = AsyncMock(spec=GitCliTool)
    mock.execute.return_value = GitCliOutput(
        operation=GitOperation.STATUS,
        return_code=0,
        stdout="",
        stderr="",
    )
    return mock


@pytest.fixture
def agent(
    interpreter: AsyncMock,
    tool: AsyncMock,
) -> GitAgent:
    return GitAgent(
        tool=tool,
        interpreter=interpreter,
    )


def interpretation(
    operation: str = "status",
    parameters: dict[str, object] | None = None,
    missing_inputs: list[str] | None = None,
    message: str | None = None,
    skill_name: str | None = "git-operations",
) -> InterpretationResult:
    return InterpretationResult(
        skill_name=skill_name,
        parameters={
            "operation": operation,
            **(parameters or {}),
        },
        missing_inputs=missing_inputs or [],
        message=message,
    )


@pytest.mark.asyncio
async def test_status_instruction_executes_git_status(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation()

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.STATUS,
        return_code=0,
        stdout="## main",
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Mostre o status do repositório",
            root_path=tmp_path,
        )
    )

    assert result.status == "completed"
    assert result.result is not None
    assert result.result.operation == GitOperation.STATUS

    tool.execute.assert_awaited_once()

    executed_input = tool.execute.await_args.args[0]
    assert isinstance(executed_input, GitCliInput)
    assert executed_input.operation == GitOperation.STATUS
    assert executed_input.root_path == tmp_path


@pytest.mark.asyncio
async def test_branch_create_instruction_executes_branch_creation(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        operation="branch_create",
        parameters={"branch_name": "feature/test"},
    )

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.BRANCH_CREATE,
        return_code=0,
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Crie a branch feature/test",
            root_path=tmp_path,
        )
    )

    assert result.status == "completed"

    executed_input = tool.execute.await_args.args[0]
    assert executed_input.operation == GitOperation.BRANCH_CREATE
    assert executed_input.branch_name == "feature/test"


@pytest.mark.asyncio
async def test_missing_root_path_returns_needs_input(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
) -> None:
    interpreter.interpret.return_value = interpretation(
        missing_inputs=["root_path"],
        message="Informe o diretório do repositório.",
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Mostre o status do repositório",
        )
    )

    assert result.status == "needs_input"
    assert result.required_input == "root_path"
    tool.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_root_path_from_request_has_priority(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "request"
    interpreted_path = tmp_path / "interpreted"

    interpreter.interpret.return_value = interpretation(
        parameters={"root_path": str(interpreted_path)},
    )

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.STATUS,
        return_code=0,
    )

    await agent.run(
        GitAgentRequest(
            instruction="Mostre o status",
            root_path=request_path,
        )
    )

    executed_input = tool.execute.await_args.args[0]
    assert executed_input.root_path == request_path


@pytest.mark.asyncio
async def test_unrecognized_skill_returns_unsupported(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        skill_name=None,
        message="Não encontrei uma operação compatível.",
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Faça algo não suportado",
            root_path=tmp_path,
        )
    )

    assert result.status == "unsupported"
    assert result.message == "Não encontrei uma operação compatível."
    tool.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_commit_without_confirmation_returns_needs_input(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        operation="commit",
        parameters={"commit_message": "Test commit"},
    )

    tool.execute.side_effect = ValueError(
        "Operation 'commit' requires confirmation."
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Faça um commit com a mensagem Test commit",
            root_path=tmp_path,
        )
    )

    assert result.status == "needs_input"
    assert "requires confirmation" in result.message

    executed_input = tool.execute.await_args.args[0]
    assert executed_input.operation == GitOperation.COMMIT
    assert executed_input.confirmed is False


@pytest.mark.asyncio
async def test_commit_with_confirmation_executes_operation(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        operation="commit",
        parameters={
            "commit_message": "Test commit",
            "confirmed": True,
        },
    )

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.COMMIT,
        return_code=0,
        stdout="Commit created",
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Faça um commit",
            root_path=tmp_path,
            confirmed=True,
        )
    )

    assert result.status == "completed"

    executed_input = tool.execute.await_args.args[0]
    assert executed_input.operation == GitOperation.COMMIT
    assert executed_input.confirmed is True


@pytest.mark.asyncio
async def test_llm_cannot_authorize_operation(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        operation="push",
        parameters={"confirmed": True},
    )

    tool.execute.side_effect = ValueError(
        "Operation 'push' requires confirmation."
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Faça push",
            root_path=tmp_path,
            confirmed=False,
        )
    )

    assert result.status == "needs_input"

    executed_input = tool.execute.await_args.args[0]
    assert executed_input.confirmed is False


@pytest.mark.asyncio
async def test_invalid_operation_parameters_return_needs_input(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation(
        operation="branch_create",
    )

    tool.execute.side_effect = ValueError(
        "Operation 'branch_create' requires branch_name."
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Crie uma branch",
            root_path=tmp_path,
        )
    )

    assert result.status == "needs_input"
    assert "requires branch_name" in result.message
    tool.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_git_execution_failure_returns_failed(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation()

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.STATUS,
        return_code=128,
        stderr="fatal: not a git repository",
    )

    result = await agent.run(
        GitAgentRequest(
            instruction="Mostre o status",
            root_path=tmp_path,
        )
    )

    assert result.status == "failed"
    assert result.message == "fatal: not a git repository"


@pytest.mark.asyncio
async def test_interpreter_receives_loaded_skills(
    agent: GitAgent,
    interpreter: AsyncMock,
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    interpreter.interpret.return_value = interpretation()

    tool.execute.return_value = GitCliOutput(
        operation=GitOperation.STATUS,
        return_code=0,
    )

    await agent.run(
        GitAgentRequest(
            instruction="Mostre o status",
            root_path=tmp_path,
        )
    )

    interpreter_request = interpreter.interpret.await_args.args[0]

    assert interpreter_request.instruction == "Mostre o status"
    assert interpreter_request.skills
    assert any(
        skill.name == "git-operations"
        for skill in interpreter_request.skills
    )


@pytest.mark.asyncio
async def test_agent_without_interpreter_returns_needs_input(
    tool: AsyncMock,
    tmp_path: Path,
) -> None:
    agent = GitAgent(tool=tool)

    result = await agent.run(
        GitAgentRequest(
            instruction="Mostre o status",
            root_path=tmp_path,
        )
    )

    assert result.status == "needs_input"
    assert result.required_input == "interpreter"
    tool.execute.assert_not_awaited()
