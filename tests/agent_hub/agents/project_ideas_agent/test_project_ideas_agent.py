
from pathlib import Path
from typing import Any, Literal
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from agent_hub.agents.project_ideas_agent import (
    ProjectIdeasAgent,
    ProjectIdeasAgentOutput,
    ProjectIdeasAgentRequest,
)
from agent_hub.core import InterpretationRequest, InterpretationResult, Interpreter

REFERENCE_PATHS = {
    "game-concepts/beginner": (
        "game-concepts/beginner/"
        "air-hockey-pro-the-path-to-glory/README.pt-BR.md"
    ),
    "game-concepts/advanced": (
        "game-concepts/advanced/"
        "exoskeleton-sports-beyond-human-limits/README.pt-BR.md"
    ),
    "game-mechanics": "game-mechanics/dynamic-rival/README.pt-BR.md",
    "non-profit": (
        "non-profit/"
        "integration-and-adaptation-platform-for-immigrants-and-refugees/"
        "README.pt-BR.md"
    ),
    "services": (
        "services/"
        "institutional-onboarding-and-enterprise-architecture-training-agent/"
        "README.pt-BR.md"
    ),
}

CONTENT_PT = (
    "# Projeto de exemplo\n\n"
    "## Descrição\n\n"
    "Uma proposta de exemplo."
)

CONTENT_EN = (
    "# Example Project\n\n"
    "## Description\n\n"
    "An example proposal."
)


@pytest.fixture
def interpreter() -> AsyncMock:
    return AsyncMock(spec=Interpreter)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    path = tmp_path / "project-ideas"
    path.mkdir()

    for relative_path in REFERENCE_PATHS.values():
        reference = path / relative_path
        reference.parent.mkdir(parents=True, exist_ok=True)
        reference.write_text(
            "# Documento de referência\n\n"
            "## Seção\n\n"
            "Conteúdo.\n",
            encoding="utf-8",
        )

    return path


@pytest.fixture
def agent(
    interpreter: AsyncMock,
    repository: Path,
) -> ProjectIdeasAgent:
    return ProjectIdeasAgent(
        interpreter=interpreter,
        project_ideas_path=repository,
    )


def make_result(
    skill_name: str | None,
    parameters: dict[str, Any] | None = None,
    missing_inputs: list[str] | None = None,
    message: str | None = None,
) -> InterpretationResult:
    return InterpretationResult(
        skill_name=skill_name,
        parameters=parameters or {},
        missing_inputs=missing_inputs or [],
        message=message,
    )


def configure_success(
    interpreter: AsyncMock,
    category: str = "services",
    content_pt_br: str = CONTENT_PT,
    content_en: str = CONTENT_EN,
) -> None:
    async def interpret(
        request: InterpretationRequest,
    ) -> InterpretationResult:
        skill_name = request.skills[0].name

        if len(request.skills) > 1:
            return make_result(category)

        if skill_name == category:
            return make_result(
                category,
                {
                    "title": "Projeto de exemplo",
                    "content_pt_br": content_pt_br,
                },
            )

        if skill_name == "text-translate":
            return make_result(
                "text-translate",
                {"translated_text": content_en},
            )

        return make_result(skill_name)

    interpreter.interpret.side_effect = interpret


class TestProjectIdeasAgent:

    def test_agent_metadata_and_loaded_skills(
        self,
        agent: ProjectIdeasAgent,
    ) -> None:
        skill_names = {skill.name for skill in agent.skills}

        assert agent.name == "project-ideas-agent"
        assert {
            "game-concepts",
            "game-mechanics",
            "non-profit",
            "services",
            "text-translate",
        }.issubset(skill_names)

        assert agent.input_schema is ProjectIdeasAgentRequest
        assert agent.output_schema is ProjectIdeasAgentOutput

    def test_request_rejects_empty_instruction(self) -> None:
        with pytest.raises(ValidationError):
            ProjectIdeasAgentRequest(instruction="  ")

    @pytest.mark.asyncio
    async def test_missing_interpreter(
        self,
        repository: Path,
    ) -> None:
        agent = ProjectIdeasAgent(project_ideas_path=repository)

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "needs_input"
        assert response.required_input == "interpreter"

    @pytest.mark.asyncio
    async def test_missing_repository_path(
        self,
        interpreter: AsyncMock,
    ) -> None:
        agent = ProjectIdeasAgent(interpreter=interpreter)

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "needs_input"
        assert response.required_input == "project_ideas_path"
        interpreter.interpret.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_repository_does_not_exist(
        self,
        interpreter: AsyncMock,
        tmp_path: Path,
    ) -> None:
        agent = ProjectIdeasAgent(
            interpreter=interpreter,
            project_ideas_path=tmp_path / "missing",
        )

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "not found" in response.message.lower()
        interpreter.interpret.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_unsupported_category(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.return_value = make_result(
            "unknown-category",
            message="No supported category matches this request.",
        )

        response = await agent.run(
            ProjectIdeasAgentRequest(instruction="Write a poem.")
        )

        assert response.status == "unsupported"
        assert "no supported category" in response.message.lower()
        assert interpreter.interpret.await_count == 1

    @pytest.mark.asyncio
    async def test_category_selection_missing_inputs(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.return_value = make_result(
            "services",
            missing_inputs=["target audience"],
            message="Please provide the target audience.",
        )

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "needs_input"
        assert response.required_input == "target audience"
        assert response.message == "Please provide the target audience."

    @pytest.mark.asyncio
    async def test_game_concept_requires_variant(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.return_value = make_result("game-concepts")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a racing game."
            )
        )

        assert response.status == "needs_input"
        assert response.category == "game-concepts"
        assert response.required_input == (
            "template_variant (beginner or advanced)"
        )
        assert interpreter.interpret.await_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("variant", "reference_key"),
        [
            ("beginner", "game-concepts/beginner"),
            ("advanced", "game-concepts/advanced"),
        ],
    )
    async def test_game_concept_variants(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
        variant: Literal["beginner", "advanced"],
        reference_key: str,
    ) -> None:
        configure_success(interpreter, category="game-concepts")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a game concept.",
                template_variant=variant,
            )
        )

        assert response.status == "completed"
        assert response.category == "game-concepts"
        assert response.template_variant == variant
        assert response.reference_path == REFERENCE_PATHS[reference_key]
        assert response.content_pt_br == CONTENT_PT
        assert response.content_en == CONTENT_EN
        assert interpreter.interpret.await_count == 3

    @pytest.mark.asyncio
    async def test_variant_is_invalid_for_non_game_category(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.return_value = make_result("services")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform.",
                template_variant="beginner",
            )
        )

        assert response.status == "failed"
        assert "only valid" in response.message.lower()
        assert response.category == "services"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "category",
        ["game-mechanics", "non-profit", "services"],
    )
    async def test_non_game_categories(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
        category: str,
    ) -> None:
        configure_success(interpreter, category=category)

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction=f"Create an idea for {category}."
            )
        )

        assert response.status == "completed"
        assert response.category == category
        assert response.template_variant is None
        assert response.reference_path == REFERENCE_PATHS[category]
        assert response.content_pt_br == CONTENT_PT
        assert response.content_en == CONTENT_EN
        assert interpreter.interpret.await_count == 3

    @pytest.mark.asyncio
    async def test_reference_document_missing(
        self,
        interpreter: AsyncMock,
        tmp_path: Path,
    ) -> None:
        repository = tmp_path / "empty-project-ideas"
        repository.mkdir()

        agent = ProjectIdeasAgent(
            interpreter=interpreter,
            project_ideas_path=repository,
        )

        interpreter.interpret.return_value = make_result("services")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "reference document not found" in response.message.lower()
        assert response.reference_path == REFERENCE_PATHS["services"]

    @pytest.mark.asyncio
    async def test_generation_requests_missing_inputs(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        async def interpret(
            request: InterpretationRequest,
        ) -> InterpretationResult:
            if len(request.skills) > 1:
                return make_result("services")

            return make_result(
                "services",
                missing_inputs=["problem to solve"],
                message="Describe the problem.",
            )

        interpreter.interpret.side_effect = interpret

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "needs_input"
        assert response.required_input == "problem to solve"
        assert interpreter.interpret.await_count == 2

    @pytest.mark.asyncio
    async def test_generation_returns_wrong_skill(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        async def interpret(
            request: InterpretationRequest,
        ) -> InterpretationResult:
            if len(request.skills) > 1:
                return make_result("services")

            return make_result("unexpected-skill")

        interpreter.interpret.side_effect = interpret

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "unsupported"
        assert "did not execute" in response.message.lower()

    @pytest.mark.asyncio
    async def test_generation_returns_empty_portuguese_content(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_success(interpreter, content_pt_br="")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "complete markdown document" in response.message.lower()
        assert interpreter.interpret.await_count == 2

    @pytest.mark.asyncio
    async def test_missing_translation_skill(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_success(interpreter)
        agent._skills.pop("text-translate")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "text-translate" in response.message
        assert response.content_pt_br == CONTENT_PT
        assert interpreter.interpret.await_count == 2

    @pytest.mark.asyncio
    async def test_translation_returns_wrong_skill(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        async def interpret(
            request: InterpretationRequest,
        ) -> InterpretationResult:
            skill = request.skills[0].name

            if len(request.skills) > 1:
                return make_result("services")

            if skill == "services":
                return make_result(
                    "services",
                    {
                        "title": "Projeto",
                        "content_pt_br": CONTENT_PT,
                    },
                )

            return make_result("unexpected-translation-skill")

        interpreter.interpret.side_effect = interpret

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "unsupported"
        assert "text-translate" in response.message
        assert response.content_pt_br == CONTENT_PT

    @pytest.mark.asyncio
    async def test_translation_returns_empty_content(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_success(interpreter, content_en="")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "empty document" in response.message.lower()
        assert response.content_pt_br == CONTENT_PT

    @pytest.mark.asyncio
    async def test_translation_missing_inputs(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        async def interpret(
            request: InterpretationRequest,
        ) -> InterpretationResult:
            skill = request.skills[0].name

            if len(request.skills) > 1:
                return make_result("services")

            if skill == "services":
                return make_result(
                    "services",
                    {
                        "title": "Projeto",
                        "content_pt_br": CONTENT_PT,
                    },
                )

            return make_result(
                "text-translate",
                missing_inputs=["target language"],
                message="Target language is required.",
            )

        interpreter.interpret.side_effect = interpret

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "target language" in response.message.lower()
        assert response.content_pt_br == CONTENT_PT

    @pytest.mark.asyncio
    async def test_interpreter_exception(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        interpreter.interpret.side_effect = RuntimeError("LLM unavailable")

        response = await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        assert response.status == "failed"
        assert "llm unavailable" in response.message.lower()

    @pytest.mark.asyncio
    async def test_translation_receives_full_markdown(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_success(interpreter)

        await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        translation_request = interpreter.interpret.await_args_list[2].args[0]

        assert [skill.name for skill in translation_request.skills] == [
            "text-translate"
        ]
        assert CONTENT_PT in translation_request.instruction
        assert "Brazilian Portuguese" in translation_request.instruction
        assert "English" in translation_request.instruction

    @pytest.mark.asyncio
    async def test_generation_receives_reference_content(
        self,
        agent: ProjectIdeasAgent,
        interpreter: AsyncMock,
    ) -> None:
        configure_success(interpreter)

        await agent.run(
            ProjectIdeasAgentRequest(
                instruction="Create a service platform."
            )
        )

        generation_request = interpreter.interpret.await_args_list[1].args[0]

        assert [skill.name for skill in generation_request.skills] == [
            "services"
        ]
        assert "Reference document (Brazilian Portuguese)" in (
            generation_request.instruction
        )
        assert "Documento de referência" in generation_request.instruction
        assert REFERENCE_PATHS["services"] in generation_request.instruction
