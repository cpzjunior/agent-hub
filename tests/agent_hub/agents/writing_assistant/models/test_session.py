
from datetime import UTC, datetime

from agent_hub.agents.writing_assistant.models.article import (
    ArticleArtifact,
    ArticleArtifactType,
    ArticleLanguage,
    ArticleReview,
    ArticleReviewStatus,
)
from agent_hub.agents.writing_assistant.models.session import (
    ArticleExploration,
    ArticleRevision,
    DiscussionMessage,
    WritingSession,
)


def test_discussion_message_defaults_timestamp() -> None:
    message = DiscussionMessage(
        role="user",
        content="Quero escrever sobre arquitetura.",
    )

    assert message.role == "user"
    assert message.content == "Quero escrever sobre arquitetura."
    assert message.timestamp.tzinfo is not None


def test_discussion_message_accepts_explicit_timestamp() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    message = DiscussionMessage(
        role="assistant",
        content="Vamos explorar a ideia.",
        timestamp=timestamp,
    )

    assert message.timestamp == timestamp


def test_article_exploration_defaults() -> None:
    exploration = ArticleExploration()

    assert exploration.initial_idea is None
    assert exploration.thesis is None
    assert exploration.arguments == []
    assert exploration.counterarguments == []
    assert exploration.implications == []
    assert exploration.open_questions == []


def test_article_exploration_accepts_content() -> None:
    exploration = ArticleExploration(
        initial_idea="Arquitetura como decisão",
        thesis="Arquitetura depende do contexto.",
        arguments=["Argumento 1"],
        counterarguments=["Contraponto 1"],
        implications=["Implicação 1"],
        open_questions=["Questão 1"],
    )

    assert exploration.initial_idea == "Arquitetura como decisão"
    assert exploration.thesis == "Arquitetura depende do contexto."
    assert exploration.arguments == ["Argumento 1"]
    assert exploration.counterarguments == ["Contraponto 1"]
    assert exploration.implications == ["Implicação 1"]
    assert exploration.open_questions == ["Questão 1"]


def test_article_revision_defaults_timestamp() -> None:
    revision = ArticleRevision(
        number=1,
        content="Primeira versão.",
    )

    assert revision.number == 1
    assert revision.content == "Primeira versão."
    assert revision.title is None
    assert revision.subtitle is None
    assert revision.reason is None
    assert revision.created_at.tzinfo is not None


def test_article_revision_accepts_complete_data() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)

    revision = ArticleRevision(
        number=2,
        title="Novo título",
        subtitle="Novo subtítulo",
        content="Conteúdo revisado.",
        reason="Reestruturação do argumento.",
        created_at=timestamp,
    )

    assert revision.number == 2
    assert revision.title == "Novo título"
    assert revision.subtitle == "Novo subtítulo"
    assert revision.content == "Conteúdo revisado."
    assert revision.reason == "Reestruturação do argumento."
    assert revision.created_at == timestamp


def test_writing_session_defaults() -> None:
    session = WritingSession()

    assert session.id is not None
    assert session.article is not None
    assert session.exploration is not None
    assert session.discussion == []
    assert session.revisions == []
    assert session.artifacts == []
    assert session.last_review is None
    assert session.created_at.tzinfo is not None
    assert session.updated_at.tzinfo is not None


def test_writing_session_accepts_related_data() -> None:
    artifact = ArticleArtifact(
        type=ArticleArtifactType.SUMMARY,
        language=ArticleLanguage.PT_BR,
        content="Resumo.",
        source_revision=1,
    )
    review = ArticleReview(
        status=ArticleReviewStatus.READY,
        strengths=["Argumentação consistente"],
    )

    session = WritingSession(
        discussion=[
            DiscussionMessage(
                role="user",
                content="Minha ideia inicial.",
            )
        ],
        exploration=ArticleExploration(
            thesis="Uma tese.",
            arguments=["Argumento."],
        ),
        revisions=[
            ArticleRevision(
                number=1,
                content="Primeira versão.",
            )
        ],
        artifacts=[artifact],
        last_review=review,
    )

    assert len(session.discussion) == 1
    assert session.exploration.thesis == "Uma tese."
    assert len(session.revisions) == 1
    assert session.artifacts[0].content == "Resumo."
    assert session.last_review is not None
    assert session.last_review.status == ArticleReviewStatus.READY


def test_writing_session_generates_independent_defaults() -> None:
    first = WritingSession()
    second = WritingSession()

    assert first.id != second.id
    assert first.article.id != second.article.id

    first.discussion.append(
        DiscussionMessage(role="user", content="Mensagem.")
    )

    assert second.discussion == []


def test_writing_session_supports_serialization_round_trip() -> None:
    session = WritingSession(
        discussion=[
            DiscussionMessage(
                role="user",
                content="Ideia inicial.",
            )
        ],
        revisions=[
            ArticleRevision(
                number=1,
                content="Primeira versão.",
            )
        ],
    )

    serialized = session.model_dump(mode="json")
    restored = WritingSession.model_validate(serialized)

    assert restored.id == session.id
    assert restored.article.id == session.article.id
    assert restored.discussion[0].content == "Ideia inicial."
    assert restored.revisions[0].content == "Primeira versão."
