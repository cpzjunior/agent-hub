
import pytest
from pydantic import ValidationError

from agent_hub.agents.writing_assistant.models.article import (
    ArticleArtifact,
    ArticleArtifactType,
    ArticleLanguage,
    ArticleModel,
    ArticleReview,
    ArticleReviewStatus,
)


def test_article_model_defaults() -> None:
    article = ArticleModel()

    assert article.language == ArticleLanguage.PT_BR
    assert article.title is None
    assert article.subtitle is None
    assert article.thesis is None
    assert article.content == ""
    assert article.tags == []
    assert article.id is not None


def test_article_model_accepts_content() -> None:
    article = ArticleModel(
        language=ArticleLanguage.PT_BR,
        title="Arquitetura de software",
        subtitle="Decisões e contexto",
        thesis="Arquitetura é um processo de decisão.",
        content="Conteúdo do artigo.",
        tags=["arquitetura", "software"],
    )

    assert article.title == "Arquitetura de software"
    assert article.subtitle == "Decisões e contexto"
    assert article.thesis == "Arquitetura é um processo de decisão."
    assert article.content == "Conteúdo do artigo."
    assert article.tags == ["arquitetura", "software"]


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("pt-BR", ArticleLanguage.PT_BR),
        ("en", ArticleLanguage.EN),
        ("es", ArticleLanguage.ES),
        ("it", ArticleLanguage.IT),
    ],
)
def test_article_model_accepts_supported_languages(
    language: str,
    expected: ArticleLanguage,
) -> None:
    article = ArticleModel.model_validate({"language": language})

    assert article.language == expected


def test_article_model_rejects_unsupported_language() -> None:
    with pytest.raises(ValidationError):
        ArticleModel.model_validate({"language": "fr"})


def test_article_model_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ArticleModel.model_validate({"unknown_field": "value"})


def test_article_artifact_accepts_valid_data() -> None:
    artifact = ArticleArtifact(
        type=ArticleArtifactType.SUMMARY,
        language=ArticleLanguage.PT_BR,
        content="Resumo do artigo.",
        source_revision=1,
    )

    assert artifact.type == ArticleArtifactType.SUMMARY
    assert artifact.language == ArticleLanguage.PT_BR
    assert artifact.content == "Resumo do artigo."
    assert artifact.source_revision == 1


@pytest.mark.parametrize(
    "artifact_type",
    [
        ArticleArtifactType.SUMMARY,
        ArticleArtifactType.TRANSLATION,
        ArticleArtifactType.AI_CONSOLIDATION,
    ],
)
def test_article_artifact_accepts_supported_types(
    artifact_type: ArticleArtifactType,
) -> None:
    artifact = ArticleArtifact(
        type=artifact_type,
        language=ArticleLanguage.EN,
        content="Artifact content.",
    )

    assert artifact.type == artifact_type


def test_article_artifact_source_revision_is_optional() -> None:
    artifact = ArticleArtifact(
        type=ArticleArtifactType.SUMMARY,
        language=ArticleLanguage.PT_BR,
        content="Resumo.",
    )

    assert artifact.source_revision is None


def test_article_artifact_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        ArticleArtifact.model_validate(
            {
                "type": "invalid",
                "language": ArticleLanguage.PT_BR,
                "content": "Conteúdo.",
            }
        )


def test_article_review_accepts_valid_data() -> None:
    review = ArticleReview(
        status=ArticleReviewStatus.READY,
        strengths=["Tese clara"],
        substantive_issues=[],
        missing_arguments=[],
        editorial_issues=[],
        recommendations=["Publicar"],
    )

    assert review.status == ArticleReviewStatus.READY
    assert review.strengths == ["Tese clara"]
    assert review.recommendations == ["Publicar"]


@pytest.mark.parametrize(
    "status",
    [
        ArticleReviewStatus.READY,
        ArticleReviewStatus.READY_WITH_MINOR_CHANGES,
        ArticleReviewStatus.NEEDS_REVISION,
        ArticleReviewStatus.NOT_READY,
    ],
)
def test_article_review_accepts_supported_statuses(
    status: ArticleReviewStatus,
) -> None:
    review = ArticleReview(status=status)

    assert review.status == status


def test_article_review_defaults_lists_to_empty() -> None:
    review = ArticleReview(status=ArticleReviewStatus.READY)

    assert review.strengths == []
    assert review.substantive_issues == []
    assert review.missing_arguments == []
    assert review.editorial_issues == []
    assert review.recommendations == []


def test_article_review_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ArticleReview.model_validate({"status": "invalid"})


def test_article_review_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ArticleReview.model_validate(
            {
                "status": ArticleReviewStatus.READY,
                "unknown_field": "value",
            }
        )
