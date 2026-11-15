
from pathlib import Path

from agent_hub.agents.git_agent import (
    GitAgent,
    GitAgentInput,
    GitAgentOutput,
)
from agent_hub.agents.git_agent.tools.git_pull.impl.git_pull import (
    GitPullInput,
    GitPullTool,
    RepositoryResult,
)
from agent_hub.core import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)


class FakeInterpreter(Interpreter):
    def __init__(self, result: InterpretationResult) -> None:
        self.result = result
        self.last_request: InterpretationRequest | None = None

    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        self.last_request = request
        return self.result


class FakeGitPullTool(GitPullTool):
    def __init__(
        self,
        results: list[RepositoryResult] | None = None,
    ) -> None:
        self.results = results or []
        self.last_input: GitPullInput | None = None
        self.execution_count = 0

    async def execute(
        self,
        input: GitPullInput,
    ) -> list[RepositoryResult]:
        self.last_input = input
        self.execution_count += 1
        return self.results


def create_interpreter(
    skill_name: str | None = "git-pull",
    parameters: dict[str, object] | None = None,
    missing_inputs: list[str] | None = None,
    message: str | None = None,
) -> FakeInterpreter:
    return FakeInterpreter(
        InterpretationResult(
            skill_name=skill_name,
            parameters=parameters or {},
            missing_inputs=missing_inputs or [],
            message=message,
        )
    )


def test_git_agent_loads_skills() -> None:
    agent = GitAgent()

    assert len(agent.skills) == 1
    assert agent.skills[0].name == "git-pull"


async def test_run_requests_missing_root_path() -> None:
    tool = FakeGitPullTool()
    agent = GitAgent(tool=tool)

    result = await agent.run(
        {"instruction": "Atualize meus repositórios."}
    )

    assert result.status == "needs_input"
    assert result.required_input == "root_path"
    assert tool.execution_count == 0


async def test_run_interprets_and_executes_git_pull(
    tmp_path: Path,
) -> None:
    interpreter = create_interpreter(
        parameters={"root_path": str(tmp_path)}
    )
    tool = FakeGitPullTool(
        results=[
            RepositoryResult(
                repository_path=str(tmp_path / "repo"),
                status="success",
                message="Already up to date.",
            )
        ]
    )

    agent = GitAgent(
        tool=tool,
        interpreter=interpreter,
    )

    result = await agent.run(
        {"instruction": "Atualize meus repositórios."}
    )

    assert result.status == "completed"
    assert result.total_repositories == 1
    assert result.successful_pulls == 1

    assert interpreter.last_request is not None
    assert interpreter.last_request.instruction == (
        "Atualize meus repositórios."
    )
    assert any(
        skill.name == "git-pull"
        for skill in interpreter.last_request.skills
    )

    assert tool.execution_count == 1
    assert tool.last_input is not None
    assert tool.last_input.root_path == tmp_path


async def test_run_uses_explicit_root_path(
    tmp_path: Path,
) -> None:
    interpreter = create_interpreter()
    tool = FakeGitPullTool()

    agent = GitAgent(
        tool=tool,
        interpreter=interpreter,
    )

    result = await agent.run(
        {
            "instruction": "Atualize meus repositórios.",
            "root_path": tmp_path,
        }
    )

    assert result.status == "completed"
    assert tool.last_input is not None
    assert tool.last_input.root_path == tmp_path


async def test_run_handles_missing_information() -> None:
    interpreter = create_interpreter(
        missing_inputs=["root_path"],
        message="Informe o diretório dos repositórios.",
    )
    tool = FakeGitPullTool()

    agent = GitAgent(
        tool=tool,
        interpreter=interpreter,
    )

    result = await agent.run(
        {"instruction": "Atualize meus repositórios."}
    )

    assert result.status == "needs_input"
    assert result.required_input == "root_path"
    assert result.message == "Informe o diretório dos repositórios."
    assert tool.execution_count == 0


async def test_run_handles_unknown_skill() -> None:
    interpreter = create_interpreter(
        skill_name=None,
        message="Nenhuma skill disponível atende à solicitação.",
    )
    tool = FakeGitPullTool()

    agent = GitAgent(
        tool=tool,
        interpreter=interpreter,
    )

    result = await agent.run(
        {"instruction": "Envie um e-mail."}
    )

    assert result.status == "unsupported"
    assert tool.execution_count == 0


async def test_run_returns_execution_summary(
    tmp_path: Path,
) -> None:
    tool = FakeGitPullTool(
        results=[
            RepositoryResult(
                repository_path=str(tmp_path / "repo1"),
                status="success",
                message="Already up to date.",
            ),
            RepositoryResult(
                repository_path=str(tmp_path / "repo2"),
                status="skipped",
                message="Repository has uncommitted changes.",
            ),
            RepositoryResult(
                repository_path=str(tmp_path / "repo3"),
                status="failed",
                message="Git pull failed.",
            ),
        ]
    )

    agent = GitAgent(tool=tool)

    result = await agent.run(
        GitAgentInput(root_path=tmp_path).model_dump()
        | {"instruction": "Atualize meus repositórios."}
    )

    assert isinstance(result, GitAgentOutput)
    assert result.status == "completed"
    assert result.total_repositories == 3
    assert result.successful_pulls == 1
    assert len(result.skipped_repositories) == 1
    assert len(result.failed_repositories) == 1


async def test_run_does_not_execute_when_skill_is_unknown() -> None:
    interpreter = create_interpreter(skill_name="unknown-skill")
    tool = FakeGitPullTool()

    agent = GitAgent(
        tool=tool,
        interpreter=interpreter,
    )

    await agent.run(
        {"instruction": "Faça alguma coisa."}
    )

    assert tool.execution_count == 0
