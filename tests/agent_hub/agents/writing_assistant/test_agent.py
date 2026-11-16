from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from agent_hub.agents.writing_assistant import (
    WritingAssistant,
    WritingAssistantRequest,
)
from agent_hub.agents.writing_assistant.models.article import (
    ArticleArtifactType,
    ArticleLanguage,
    ArticleReviewStatus,
)
from agent_hub.agents.writing_assistant.models.session import (
    WritingSession,
)
from agent_hub.core import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)


class FakeInterpreter(Interpreter):
    def __init__(
        self,
        results: list[InterpretationResult],
    ) -> None:
        self.results = results
        self.requests: list[InterpretationRequest] = []

    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        self.requests.append(request)

        if not self.results:
            raise AssertionError("Unexpected interpreter invocation")

        return self.results.pop(0)


AgentFactory = Callable[
    [list[InterpretationResult]],
    tuple[WritingAssistant, FakeInterpreter],
]


@pytest.fixture
def agent_path(tmp_path: Path) -> Path:
    path = tmp_path / "writing_assistant"
    skills_path = path / "skills"

    skills = {
        "idea-explore": "Explore article ideas.",
        "article-name": "Define article title and subtitle.",
        "article-write": "Write the article.",
        "article-review": "Review the article.",
        "article-summary": "Summarize the article.",
        "article-ai-consolidate": "Consolidate the article for AI.",
    }

    for name, instructions in skills.items():
        skill_dir = skills_path / name
        skill_dir.mkdir(parents=True)

        (skill_dir / "SKILL.md").write_text(
            f"""---
name: {name}
description: {instructions}
---

{instructions}
""",
            encoding="utf-8",
        )

    workflow_dir = path / "workflows" / "article-writing"
    workflow_dir.mkdir(parents=True)

    (workflow_dir / "WORKFLOW.md").write_text(
        "Article writing workflow.",
        encoding="utf-8",
    )

    return path


@pytest.fixture
def shared_skills_path(tmp_path: Path) -> Path:
    path = tmp_path / "shared_skills"
    skill_dir = path / "text-translate"
    skill_dir.mkdir(parents=True)

    (skill_dir / "SKILL.md").write_text(
        """---
name: text-translate
description: Translate text between languages.
---

Translate the provided text.
""",
        encoding="utf-8",
    )

    return path


@pytest.fixture
def make_agent(
    agent_path: Path,
    shared_skills_path: Path,
) -> AgentFactory:
    def factory(
        results: list[InterpretationResult],
    ) -> tuple[WritingAssistant, FakeInterpreter]:
        interpreter = FakeInterpreter(results)

        agent = WritingAssistant(
            interpreter=interpreter,
            agent_path=agent_path,
            shared_skills_path=shared_skills_path,
        )

        return agent, interpreter

    return factory


def interpretation(
    skill_name: str | None = None,
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


def test_agent_loads_local_and_shared_skills(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent([])

    skill_names = {skill.name for skill in agent.skills}

    assert {
        "idea-explore",
        "article-name",
        "article-write",
        "article-review",
        "article-summary",
        "article-ai-consolidate",
        "text-translate",
    }.issubset(skill_names)


@pytest.mark.asyncio
async def test_agent_returns_needs_input_when_selection_requires_input(
    make_agent: AgentFactory,
) -> None:
    agent, interpreter = make_agent(
        [
            interpretation(
                missing_inputs=["article topic"],
                message="What topic should the article cover?",
            )
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Write an article.",
        )
    )

    assert result.status == "needs_input"
    assert result.required_input
    assert len(interpreter.requests) == 1


@pytest.mark.asyncio
async def test_agent_returns_unsupported_for_unknown_skill(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="unknown-skill")
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Perform an unsupported operation.",
        )
    )

    assert result.status == "unsupported"


@pytest.mark.asyncio
async def test_agent_executes_selected_skill(
    make_agent: AgentFactory,
) -> None:
    agent, interpreter = make_agent(
        [
            interpretation(skill_name="idea-explore"),
            interpretation(
                parameters={
                    "exploration_updates": {
                        "initial_idea": "Architecture as decision-making",
                        "thesis": "Architecture depends on context.",
                    }
                },
                message="The initial idea has been explored.",
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Explore the idea of architecture as decision-making.",
        )
    )

    assert result.status == "completed"
    assert result.skill_name == "idea-explore"
    assert result.session.exploration.initial_idea == (
        "Architecture as decision-making"
    )
    assert result.session.exploration.thesis == (
        "Architecture depends on context."
    )
    assert len(interpreter.requests) == 2


@pytest.mark.asyncio
async def test_agent_preserves_existing_session(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="idea-explore"),
            interpretation(
                parameters={
                    "exploration_updates": {
                        "arguments": ["New argument"],
                    }
                }
            ),
        ]
    )

    session = WritingSession()
    session.exploration.arguments = ["Existing argument"]

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Add another argument.",
            session=session,
        )
    )

    assert result.session.id == session.id
    assert result.session.exploration.arguments == [
        "Existing argument",
        "New argument",
    ]


@pytest.mark.asyncio
async def test_agent_writes_article_and_creates_revision(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="article-write"),
            interpretation(
                parameters={
                    "article_updates": {
                        "title": "Architecture and Context",
                        "subtitle": "Understanding architectural decisions",
                        "thesis": "Architecture is contextual.",
                        "content": "Article body.",
                    },
                    "revision_reason": "Initial article draft.",
                }
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Write the article.",
        )
    )

    assert result.status == "completed"
    assert result.session.article.title == "Architecture and Context"
    assert result.session.article.content == "Article body."
    assert len(result.session.revisions) == 1
    assert result.session.revisions[0].number == 1


@pytest.mark.asyncio
async def test_agent_review_does_not_modify_article(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="article-review"),
            interpretation(
                parameters={
                    "review": {
                        "status": "needs_revision",
                        "strengths": ["Clear thesis"],
                        "substantive_issues": ["Weak argument"],
                        "missing_arguments": [],
                        "editorial_issues": [],
                        "recommendations": ["Strengthen the argument"],
                    }
                }
            ),
        ]
    )

    session = WritingSession()
    session.article.title = "Original title"
    session.article.content = "Original content"

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Review the article critically.",
            session=session,
        )
    )

    assert result.status == "completed"
    assert result.session.article.title == "Original title"
    assert result.session.article.content == "Original content"
    assert result.session.revisions == []
    assert result.session.last_review is not None
    assert (
        result.session.last_review.status
        == ArticleReviewStatus.NEEDS_REVISION
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("skill_name", "artifact_type", "language"),
    [
        (
            "article-summary",
            ArticleArtifactType.SUMMARY,
            ArticleLanguage.PT_BR,
        ),
        (
            "text-translate",
            ArticleArtifactType.TRANSLATION,
            ArticleLanguage.EN,
        ),
        (
            "article-ai-consolidate",
            ArticleArtifactType.AI_CONSOLIDATION,
            ArticleLanguage.EN,
        ),
    ],
)
async def test_agent_creates_artifacts(
    make_agent: AgentFactory,
    skill_name: str,
    artifact_type: ArticleArtifactType,
    language: ArticleLanguage,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name=skill_name),
            interpretation(
                parameters={
                    "artifacts": [
                        {
                            "type": artifact_type.value,
                            "language": language.value,
                            "content": "Generated artifact.",
                        }
                    ]
                }
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction=f"Execute {skill_name}.",
        )
    )

    assert result.status == "completed"
    assert len(result.session.artifacts) == 1

    artifact = result.session.artifacts[0]

    assert artifact.type == artifact_type
    assert artifact.language == language
    assert artifact.content == "Generated artifact."


@pytest.mark.asyncio
async def test_agent_rejects_immutable_article_fields(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="article-write"),
            interpretation(
                parameters={
                    "article_updates": {
                        "id": "00000000-0000-0000-0000-000000000000",
                    }
                }
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Rewrite the article.",
        )
    )

    assert result.status == "failed"


@pytest.mark.asyncio
async def test_agent_rejects_unknown_article_fields(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="article-write"),
            interpretation(
                parameters={
                    "article_updates": {
                        "unknown_field": "Invalid value",
                    }
                }
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Rewrite the article.",
        )
    )

    assert result.status == "failed"


@pytest.mark.asyncio
async def test_agent_records_discussion_messages(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="idea-explore"),
            interpretation(
                parameters={
                    "exploration_updates": {
                        "initial_idea": "Initial idea",
                    }
                },
                message="Exploration completed.",
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Explore an idea.",
        )
    )

    assert len(result.session.discussion) == 2
    assert result.session.discussion[0].role == "user"
    assert result.session.discussion[1].role == "assistant"


@pytest.mark.asyncio
async def test_agent_updates_session_timestamp(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="idea-explore"),
            interpretation(
                parameters={
                    "exploration_updates": {
                        "initial_idea": "New idea",
                    }
                }
            ),
        ]
    )

    session = WritingSession()
    previous_timestamp = session.updated_at

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Explore an idea.",
            session=session,
        )
    )

    assert result.session.updated_at >= previous_timestamp


@pytest.mark.asyncio
async def test_agent_returns_execution_message(
    make_agent: AgentFactory,
) -> None:
    agent, _ = make_agent(
        [
            interpretation(skill_name="idea-explore"),
            interpretation(
                message="The idea has been explored.",
            ),
        ]
    )

    result = await agent.run(
        WritingAssistantRequest(
            instruction="Explore an idea.",
        )
    )

    assert result.message == "The idea has been explored."
