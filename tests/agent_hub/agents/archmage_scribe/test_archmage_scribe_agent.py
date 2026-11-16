from pathlib import Path

import pytest

from agent_hub.agents.archmage_scribe import (
    ArchmageScribeAgent,
    ArchmageScribeRequest,
)
from agent_hub.agents.archmage_scribe.models.content import (
    CanonicalRelation,
)
from agent_hub.agents.archmage_scribe.models.session import (
    ArchmageScribeSession,
)
from agent_hub.core import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)


class FakeInterpreter(Interpreter):
    def __init__(
        self,
        results: list[InterpretationResult | Exception],
    ) -> None:
        self.results = results
        self.requests: list[InterpretationRequest] = []

    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        self.requests.append(request)

        result = self.results.pop(0)

        if isinstance(result, Exception):
            raise result

        return result


@pytest.fixture
def agent_paths(tmp_path: Path) -> tuple[Path, Path]:
    agent_path = tmp_path / "agent"
    skills_path = agent_path / "skills"

    skills = {
        "idea-explore": (
            "Explore and develop concepts for the fictional universe."
        ),
        "fantasy-write": (
            "Write immersive texts grounded in the fictional universe."
        ),
    }

    for name, description in skills.items():
        skill_path = skills_path / name
        skill_path.mkdir(parents=True)

        (skill_path / "SKILL.md").write_text(
            f"""---
name: {name}
description: {description}
---

# {name}

Instructions for {name}.
""",
            encoding="utf-8",
        )

    workflow_path = (
        agent_path / "workflows" / "worldbuilding"
    )
    workflow_path.mkdir(parents=True)

    (workflow_path / "WORKFLOW.md").write_text(
        "# Worldbuilding workflow",
        encoding="utf-8",
    )

    content_path = tmp_path / "universum-arcanum"
    content_path.mkdir()

    (content_path / "README.pt-BR.md").write_text(
        "# Universum Arcanum\n\n"
        "Arcania is a domain of the Logos. "
        "Magic is the discipline of transforming reality.",
        encoding="utf-8",
    )

    return agent_path, content_path


def create_agent(
    agent_paths: tuple[Path, Path],
    results: list[InterpretationResult | Exception],
) -> tuple[ArchmageScribeAgent, FakeInterpreter]:
    agent_path, content_path = agent_paths
    interpreter = FakeInterpreter(results)

    agent = ArchmageScribeAgent(
        interpreter=interpreter,
        content_path=content_path,
        agent_path=agent_path,
    )

    return agent, interpreter


def test_agent_initializes_and_loads_skills(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(agent_paths, [])

    assert agent.name == "archmage-scribe"
    assert agent.description
    assert agent.content_path == agent_paths[1].resolve()

    assert {skill.name for skill in agent.skills} == {
        "idea-explore",
        "fantasy-write",
    }

    assert agent.input_schema is ArchmageScribeRequest
    assert agent.workflow == "# Worldbuilding workflow"


@pytest.mark.asyncio
async def test_agent_executes_idea_explore(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(
                skill_name="idea-explore",
            ),
            InterpretationResult(
                skill_name="idea-explore",
                parameters={
                    "initial_idea": "Uma escola arcana em Arcania.",
                    "concepts": [
                        "A escola preserva conhecimentos arcanos."
                    ],
                    "open_questions": [
                        "Qual sua relação com as Famílias Arcanas?"
                    ],
                },
                message="A ideia foi desenvolvida.",
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Explore a ideia de uma escola arcana."}
    )

    assert result.status == "completed"
    assert result.skill_name == "idea-explore"

    assert result.session.initial_idea == (
        "Uma escola arcana em Arcania."
    )
    assert len(result.session.concepts) == 1
    assert len(result.session.open_questions) == 1

    assert len(interpreter.requests) == 2
    assert {
        skill.name
        for skill in interpreter.requests[0].skills
    } == {
        "idea-explore",
        "fantasy-write",
    }

    assert interpreter.requests[1].skills[0].name == "idea-explore"


@pytest.mark.asyncio
async def test_agent_executes_fantasy_write(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(
                skill_name="fantasy-write",
            ),
            InterpretationResult(
                skill_name="fantasy-write",
                parameters={
                    "contents": [
                        {
                            "title": "Tratado sobre Arcania",
                            "content": "Arcania é um domínio do Logos.",
                            "content_type": "treatise",
                            "fictional_author": "Asterion Valerius",
                            "historical_context": (
                                "1380 da Quarta Era"
                            ),
                            "canonical_relation": "consistent",
                            "canonical_references": [
                                "README.pt-BR.md"
                            ],
                        }
                    ]
                },
                message="O tratado foi elaborado.",
            ),
        ],
    )

    result = await agent.run(
        {
            "instruction": (
                "Escreva um breve tratado sobre Arcania "
                "na voz de Asterion Valerius."
            )
        }
    )

    assert result.status == "completed"
    assert result.skill_name == "fantasy-write"
    assert len(result.session.contents) == 1

    content = result.session.contents[0]

    assert content.title == "Tratado sobre Arcania"
    assert content.fictional_author == "Asterion Valerius"
    assert content.canonical_relation == CanonicalRelation.CONSISTENT
    assert content.canonical_references == ["README.pt-BR.md"]

    assert interpreter.requests[1].skills[0].name == "fantasy-write"


@pytest.mark.asyncio
async def test_agent_preserves_session_between_executions(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(
        agent_paths,
        [
            InterpretationResult(skill_name="idea-explore"),
            InterpretationResult(
                skill_name="idea-explore",
                parameters={
                    "concepts": ["Primeiro conceito."]
                },
            ),
        ],
    )

    first_result = await agent.run(
        {"instruction": "Explore uma ideia."}
    )

    second_agent, _ = create_agent(
        agent_paths,
        [
            InterpretationResult(skill_name="idea-explore"),
            InterpretationResult(
                skill_name="idea-explore",
                parameters={
                    "concepts": [
                        "Primeiro conceito.",
                        "Segundo conceito.",
                    ]
                },
            ),
        ],
    )

    second_result = await second_agent.run(
        {
            "instruction": "Continue a exploração.",
            "session": first_result.session,
        }
    )

    assert second_result.session.id == first_result.session.id
    assert second_result.session.concepts == [
        "Primeiro conceito.",
        "Segundo conceito.",
    ]

    assert len(second_result.session.discussion) == 2


@pytest.mark.asyncio
async def test_agent_returns_needs_input_when_selection_requires_information(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(
                skill_name="fantasy-write",
                missing_inputs=["historical_period"],
                message="Informe o período histórico.",
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Escreva uma crônica."}
    )

    assert result.status == "needs_input"
    assert result.required_input == ["historical_period"]
    assert result.message == "Informe o período histórico."
    assert len(interpreter.requests) == 1


@pytest.mark.asyncio
async def test_agent_returns_needs_input_during_skill_execution(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(skill_name="fantasy-write"),
            InterpretationResult(
                skill_name="fantasy-write",
                missing_inputs=["fictional_author"],
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Escreva um tratado."}
    )

    assert result.status == "needs_input"
    assert result.required_input == ["fictional_author"]
    assert len(interpreter.requests) == 2


@pytest.mark.asyncio
async def test_agent_returns_unsupported_when_no_skill_is_selected(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(
                message="A solicitação não é suportada."
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Calcule a cotação do dólar."}
    )

    assert result.status == "unsupported"
    assert result.message == "A solicitação não é suportada."
    assert len(interpreter.requests) == 1


@pytest.mark.asyncio
async def test_agent_returns_unsupported_for_unknown_skill(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(
        agent_paths,
        [
            InterpretationResult(
                skill_name="unknown-skill",
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Explore uma ideia."}
    )

    assert result.status == "unsupported"
    assert result.message == "Unknown skill: unknown-skill"


@pytest.mark.asyncio
async def test_agent_retrieves_canonical_documents(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, interpreter = create_agent(
        agent_paths,
        [
            InterpretationResult(skill_name="idea-explore"),
            InterpretationResult(
                skill_name="idea-explore",
                parameters={
                    "concepts": ["Conceito relacionado a Arcania."]
                },
            ),
        ],
    )

    result = await agent.run(
        {"instruction": "Explore Arcania e sua relação com a magia."}
    )

    assert result.status == "completed"
    assert "README.pt-BR.md" in result.session.canonical_references

    selection_instruction = interpreter.requests[0].instruction

    assert "Arcania" in selection_instruction
    assert "Magic is the discipline" in selection_instruction


@pytest.mark.asyncio
async def test_agent_deduplicates_session_updates(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(
        agent_paths,
        [
            InterpretationResult(skill_name="idea-explore"),
            InterpretationResult(
                skill_name="idea-explore",
                parameters={
                    "concepts": [
                        "Conceito existente.",
                        "Novo conceito.",
                    ],
                    "open_questions": [
                        "Questão existente."
                    ],
                },
            ),
        ],
    )

    session = ArchmageScribeSession(
        concepts=["Conceito existente."],
        open_questions=["Questão existente."],
    )

    result = await agent.run(
        {
            "instruction": "Continue a exploração.",
            "session": session,
        }
    )

    assert result.session.concepts == [
        "Conceito existente.",
        "Novo conceito.",
    ]
    assert result.session.open_questions == [
        "Questão existente."
    ]


def test_agent_rejects_unexpected_session_parameters(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(agent_paths, [])

    session = ArchmageScribeSession()

    with pytest.raises(
        ValueError,
        match="Unexpected execution parameters",
    ):
        agent._apply_updates(
            session,
            {"unexpected_field": "value"},
        )


@pytest.mark.asyncio
async def test_agent_returns_failed_when_interpreter_raises(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(
        agent_paths,
        [
            RuntimeError("Interpreter unavailable"),
        ],
    )

    result = await agent.run(
        {"instruction": "Explore uma ideia."}
    )

    assert result.status == "failed"
    assert "Interpreter unavailable" in result.message


@pytest.mark.asyncio
async def test_agent_returns_failed_when_canon_repository_is_missing(
    tmp_path: Path,
) -> None:
    agent_path = tmp_path / "agent"
    skills_path = agent_path / "skills"

    for name in ("idea-explore", "fantasy-write"):
        skill_path = skills_path / name
        skill_path.mkdir(parents=True)

        (skill_path / "SKILL.md").write_text(
            f"""---
name: {name}
description: Test skill.
---

# Instructions
""",
            encoding="utf-8",
        )

    interpreter = FakeInterpreter([])

    agent = ArchmageScribeAgent(
        interpreter=interpreter,
        content_path=tmp_path / "missing-repository",
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Explore uma ideia."}
    )

    assert result.status == "failed"
    assert "Canon repository not found" in result.message
    assert not interpreter.requests


def test_agent_rejects_empty_instruction(
    agent_paths: tuple[Path, Path],
) -> None:
    agent, _ = create_agent(agent_paths, [])

    with pytest.raises(ValueError):
        ArchmageScribeRequest(instruction="   ")