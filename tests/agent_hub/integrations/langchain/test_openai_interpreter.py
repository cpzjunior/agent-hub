from pathlib import Path
from unittest.mock import AsyncMock, Mock

from agent_hub.core import (
    InterpretationRequest,
    InterpretationResult,
    Skill,
)
from agent_hub.integrations.langchain import (
    OpenAIInterpreter,
    OpenAISettings,
)


def create_skill() -> Skill:
    return Skill(
        name="git-pull",
        description="Pull updates from Git repositories.",
        instructions="Use git-pull with root_path.",
        path=Path("skills/git-pull/SKILL.md"),
    )


def create_interpreter(
    expected: InterpretationResult,
) -> tuple[OpenAIInterpreter, Mock]:
    chain = Mock(
        ainvoke=AsyncMock(return_value=expected)
    )

    interpreter = OpenAIInterpreter(
        settings=OpenAISettings(),
        chain=chain,
    )

    return interpreter, chain


def test_interpreter_initialization() -> None:
    chain = Mock()
    chain.ainvoke = AsyncMock()

    interpreter = OpenAIInterpreter(
        settings=OpenAISettings(),
        chain=chain,
    )

    assert interpreter is not None


def test_interpreter_initialization_without_api_key() -> None:
    chain = Mock()
    chain.ainvoke = AsyncMock()

    interpreter = OpenAIInterpreter(chain=chain)

    assert interpreter is not None


async def test_interpreter_returns_structured_result() -> None:
    expected = InterpretationResult(
        skill_name="git-pull",
        parameters={"root_path": "C:/repositories"},
    )

    interpreter, chain = create_interpreter(expected)

    request = InterpretationRequest(
        instruction="Atualize os repositórios em C:/repositories.",
        skills=[create_skill()],
    )

    result = await interpreter.interpret(request)

    assert result == expected
    chain.ainvoke.assert_awaited_once()


async def test_interpreter_handles_missing_information() -> None:
    expected = InterpretationResult(
        skill_name="git-pull",
        missing_inputs=["root_path"],
        message="Informe o diretório dos repositórios.",
    )

    interpreter, chain = create_interpreter(expected)

    request = InterpretationRequest(
        instruction="Atualize meus repositórios.",
        skills=[create_skill()],
    )

    result = await interpreter.interpret(request)

    assert result.skill_name == "git-pull"
    assert result.missing_inputs == ["root_path"]
    chain.ainvoke.assert_awaited_once()


async def test_interpreter_handles_unknown_skill() -> None:
    expected = InterpretationResult(
        message="Nenhuma skill disponível atende à solicitação."
    )

    interpreter, chain = create_interpreter(expected)

    request = InterpretationRequest(
        instruction="Envie um e-mail.",
        skills=[create_skill()],
    )

    result = await interpreter.interpret(request)

    assert result.skill_name is None
    chain.ainvoke.assert_awaited_once()
