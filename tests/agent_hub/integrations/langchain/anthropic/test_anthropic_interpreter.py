
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from agent_hub.core.interpreter import (
    InterpretationRequest,
    InterpretationResult,
)
from agent_hub.core.skill import Skill
from agent_hub.integrations.langchain.anthropic import (
    AnthropicInterpreter,
    AnthropicSettings,
)


@pytest.fixture
def skill() -> Skill:
    return Skill(
        name="git-pull",
        description="Pull changes from a Git repository.",
        instructions="Execute git pull in the specified repository.",
        path=Path("skills/git-pull"),
    )


@pytest.fixture
def interpretation_result() -> InterpretationResult:
    return InterpretationResult(
        skill_name="git-pull",
        parameters={"root_path": "/tmp/repository"},
        missing_inputs=[],
        message="Git pull requested.",
    )


@pytest.mark.asyncio
async def test_interpret_returns_structured_result(
    skill: Skill,
    interpretation_result: InterpretationResult,
) -> None:
    chain = AsyncMock()
    chain.ainvoke.return_value = interpretation_result

    interpreter = AnthropicInterpreter(chain=chain)

    request = InterpretationRequest(
        instruction="Pull the latest changes from my repository.",
        skills=[skill],
    )

    result = await interpreter.interpret(request)

    assert result == interpretation_result
    chain.ainvoke.assert_awaited_once()

    payload = chain.ainvoke.call_args.args[0]

    assert payload["instruction"] == request.instruction
    assert "git-pull" in payload["skills"]


@pytest.mark.asyncio
async def test_interpret_with_no_available_skills() -> None:
    chain = AsyncMock()
    chain.ainvoke.return_value = InterpretationResult(
        skill_name=None,
        parameters={},
        missing_inputs=[],
        message="No matching skill found.",
    )

    interpreter = AnthropicInterpreter(chain=chain)

    request = InterpretationRequest(
        instruction="Do something unrelated.",
        skills=[],
    )

    result = await interpreter.interpret(request)

    assert result.skill_name is None
    assert result.parameters == {}


def test_interpreter_requires_api_key_without_chain() -> None:
    settings = AnthropicSettings(api_key=None)

    with pytest.raises(
        ValueError,
        match="Anthropic API key is required",
    ):
        AnthropicInterpreter(settings=settings)
