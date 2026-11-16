from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from agent_hub.agents.writing_assistant.models.article import (
    ArticleArtifact,
    ArticleModel,
    ArticleReview,
)
from agent_hub.agents.writing_assistant.models.session import (
    ArticleRevision,
    DiscussionMessage,
    WritingSession,
)
from agent_hub.core.agent import Agent
from agent_hub.core.interpreter import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)
from agent_hub.core.skill import Skill, SkillLoader


class WritingAssistantRequest(BaseModel):
    instruction: str
    session: WritingSession | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Instruction cannot be empty.")
        return value


class WritingAssistantOutput(BaseModel):
    status: Literal[
        "completed",
        "needs_input",
        "unsupported",
        "failed",
    ]
    message: str
    session: WritingSession
    skill_name: str | None = None
    interpretation: InterpretationResult | None = None
    required_input: list[str] = Field(default_factory=list)


class WritingAssistant(Agent):
    name = "writing-assistant"
    description = (
        "Explore ideas, write, review, summarize, and translate "
        "articles while preserving the author's editorial voice."
    )

    IMMUTABLE_ARTICLE_FIELDS = {"id", "language"}
    ALLOWED_ARTICLE_FIELDS = {
        "title",
        "subtitle",
        "thesis",
        "content",
        "tags",
    }

    def __init__(
        self,
        interpreter: Interpreter,
        agent_path: Path | None = None,
        shared_skills_path: Path | None = None,
    ) -> None:
        self.interpreter = interpreter

        self.agent_path = (
            agent_path
            if agent_path is not None
            else Path(__file__).parent
        )

        self.shared_skills_path = shared_skills_path

        self._skills = self._load_skills()

        workflow_path = (
            self.agent_path
            / "workflows"
            / "article-writing"
            / "WORKFLOW.md"
        )

        self.workflow = (
            workflow_path.read_text(encoding="utf-8")
            if workflow_path.exists()
            else ""
        )

    def _load_skills(self) -> list[Skill]:
        skills = SkillLoader(
            self.agent_path / "skills"
        ).load_all()

        if self.shared_skills_path is not None:
            shared_skill = SkillLoader(
                self.shared_skills_path
            ).load("text-translate")

            skills.append(shared_skill)

        return skills

    @property
    def skills(self) -> list[Skill]:
        return self._skills

    @property
    def input_schema(self) -> type[WritingAssistantRequest]:
        return WritingAssistantRequest

    @property
    def output_schema(self) -> type[WritingAssistantOutput]:
        return WritingAssistantOutput

    async def run(
        self,
        input: WritingAssistantRequest | dict[str, Any],
    ) -> WritingAssistantOutput:
        request = WritingAssistantRequest.model_validate(input)

        session = request.session or WritingSession()

        if not self._skills:
            return self._result(
                "failed",
                "No skills are available.",
                session,
            )

        user_message = DiscussionMessage(
            role="user",
            content=request.instruction,
        )
        session.discussion.append(user_message)

        try:
            selection = await self.interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_selection_instruction(
                        request.instruction,
                        session,
                    ),
                    skills=self._skills,
                )
            )

            if selection.missing_inputs:
                session.updated_at = self._now()
                return self._result(
                    "needs_input",
                    selection.message or "Additional information is required.",
                    session,
                    selection.skill_name,
                    selection,
                    selection.missing_inputs,
                )

            if not selection.skill_name:
                session.updated_at = self._now()
                return self._result(
                    "unsupported",
                    selection.message or "No suitable skill was identified.",
                    session,
                    interpretation=selection,
                )

            selected_skill = next(
                (
                    skill
                    for skill in self._skills
                    if skill.name == selection.skill_name
                ),
                None,
            )

            if selected_skill is None:
                session.updated_at = self._now()
                return self._result(
                    "unsupported",
                    f"Unknown skill: {selection.skill_name}",
                    session,
                    selection.skill_name,
                    selection,
                )

            execution = await self.interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_execution_instruction(
                        request.instruction,
                        session,
                        selected_skill,
                    ),
                    skills=[selected_skill],
                )
            )

            if execution.missing_inputs:
                session.updated_at = self._now()
                return self._result(
                    "needs_input",
                    execution.message or "Additional information is required.",
                    session,
                    selected_skill.name,
                    execution,
                    execution.missing_inputs,
                )

            if (
                execution.skill_name is not None
                and execution.skill_name != selected_skill.name
            ):
                session.updated_at = self._now()
                return self._result(
                    "failed",
                    "Interpreter returned an unexpected skill.",
                    session,
                    selected_skill.name,
                    execution,
                )

            self._apply_updates(
                session,
                execution.parameters,
            )

            if execution.message:
                session.discussion.append(
                    DiscussionMessage(
                        role="assistant",
                        content=execution.message,
                    )
                )

            session.updated_at = self._now()

            return self._result(
                "completed",
                execution.message or "Operation completed.",
                session,
                selected_skill.name,
                execution,
            )

        except Exception as exc:
            session.updated_at = self._now()
            return self._result(
                "failed",
                f"Writing Assistant execution failed: {exc}",
                session,
            )

    def _build_selection_instruction(
        self,
        instruction: str,
        session: WritingSession,
    ) -> str:
        return f"""
You are the skill coordinator of the Writing Assistant.

Select exactly one skill that best addresses the user's current request.

Do not execute the skill during selection.

Use the workflow and current session to understand the context.

The workflow is not a mandatory sequence. The user may request any
activity independently or return to an earlier stage.

Available workflow:
{self.workflow}

Current session:
{session.model_dump_json(indent=2)}

User instruction:
{instruction}

Consider:
- Current article and its language.
- Existing exploration and discussion.
- Previous revisions.
- Existing artifacts.
- Whether the user requests exploration, naming, writing,
  review, summary, translation, or AI consolidation.

Return the selected skill name.

If essential information is missing, use missing_inputs.
Do not ask for information already available in the session.
""".strip()

    def _build_execution_instruction(
        self,
        instruction: str,
        session: WritingSession,
        skill: Skill,
    ) -> str:
        return f"""
Execute the selected skill according to its instructions.

Selected skill:
{skill.name}

Skill instructions:
{skill.instructions}

User instruction:
{instruction}

Current session:
{session.model_dump_json(indent=2)}

Return structured parameters using only the following fields:

- article_updates: object containing only article fields to update.
- exploration_updates: object containing only exploration fields to update.
- artifacts: list of derived ArticleArtifact objects.
- review: structured ArticleReview object or null.
- revision_reason: optional explanation for an article revision.

Rules:

1. Preserve the author's ideas, opinions, and intended meaning.
2. Do not invent facts, references, or personal experiences.
3. Do not modify fields unrelated to the user's request.
4. Do not modify article id or language.
5. Use article_updates only when the skill is authorized to change
   the canonical article.
6. Review-only operations must not modify the article.
7. Summary, translation, and AI consolidation must be returned
   as artifacts, not as canonical article updates.
8. Article review must populate the review field.
9. Exploration must update exploration_updates.
10. Return only fields that actually require changes.
11. Preserve previous session information.
12. If essential information is missing, use missing_inputs.
13. Do not include explanatory prose inside structured fields
    unless required by their schema.
14. Do not create an article revision for changes to derived artifacts.
""".strip()

    def _apply_updates(
        self,
        session: WritingSession,
        updates: dict[str, Any],
    ) -> None:
        allowed_parameters = {
            "article_updates",
            "exploration_updates",
            "artifacts",
            "review",
            "revision_reason",
        }

        unexpected = set(updates) - allowed_parameters

        if unexpected:
            raise ValueError(
                f"Unexpected execution parameters: {sorted(unexpected)}"
            )

        article_updates = updates.get("article_updates") or {}

        if article_updates:
            self._validate_article_updates(article_updates)

            previous_article = session.article.model_dump()

            updated_article = self._deep_merge(
                previous_article,
                article_updates,
            )

            session.article = ArticleModel.model_validate(
                updated_article
            )

            if session.article.model_dump() != previous_article:
                revision = ArticleRevision(
                    number=len(session.revisions) + 1,
                    title=session.article.title,
                    subtitle=session.article.subtitle,
                    content=session.article.content,
                    reason=updates.get("revision_reason"),
                )
                session.revisions.append(revision)

        exploration_updates = updates.get("exploration_updates") or {}

        if exploration_updates:
            current_exploration = session.exploration.model_dump()

            updated_exploration = self._deep_merge(
                current_exploration,
                exploration_updates,
            )

            for key, value in exploration_updates.items():
                if (
                    isinstance(current_exploration.get(key), list)
                    and isinstance(value, list)
                ):
                    updated_exploration[key] = (
                        current_exploration[key] + value
                    )

            session.exploration = type(
                session.exploration
            ).model_validate(updated_exploration)

        review_data = updates.get("review")

        if review_data is not None:
            session.last_review = ArticleReview.model_validate(
                review_data
            )

        artifacts = updates.get("artifacts") or []

        for artifact_data in artifacts:
            artifact_data = dict(artifact_data)

            if artifact_data.get("source_revision") is None:
                artifact_data["source_revision"] = len(
                    session.revisions
                )

            artifact = ArticleArtifact.model_validate(
                artifact_data
            )

            session.artifacts.append(artifact)

    def _validate_article_updates(
        self,
        updates: dict[str, Any],
    ) -> None:
        invalid_fields = (
            self.IMMUTABLE_ARTICLE_FIELDS.intersection(updates)
        )

        if invalid_fields:
            raise ValueError(
                "Cannot update immutable article fields: "
                f"{sorted(invalid_fields)}"
            )

        unknown_fields = set(updates) - self.ALLOWED_ARTICLE_FIELDS

        if unknown_fields:
            raise ValueError(
                f"Unknown article fields: {sorted(unknown_fields)}"
            )

    @classmethod
    def _deep_merge(
        cls,
        current: dict[str, Any],
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        result = deepcopy(current)

        for key, value in updates.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = cls._deep_merge(
                    result[key],
                    value,
                )
            else:
                result[key] = value

        return result

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _result(
        status: Literal[
            "completed",
            "needs_input",
            "unsupported",
            "failed",
        ],
        message: str,
        session: WritingSession,
        skill_name: str | None = None,
        interpretation: InterpretationResult | None = None,
        required_input: list[str] | None = None,
    ) -> WritingAssistantOutput:
        return WritingAssistantOutput(
            status=status,
            message=message,
            session=session,
            skill_name=skill_name,
            interpretation=interpretation,
            required_input=required_input or [],
        )
