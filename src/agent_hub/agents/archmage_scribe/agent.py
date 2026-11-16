import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agent_hub.agents.archmage_scribe.models.content import CreatedContent
from agent_hub.agents.archmage_scribe.models.session import (
    ArchmageScribeSession,
    DiscussionMessage,
)
from agent_hub.core.agent import Agent
from agent_hub.core.interpreter import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)
from agent_hub.core.skill import Skill, SkillLoader


class ArchmageScribeRequest(BaseModel):
    """Input contract for the Archmage Scribe."""

    model_config = ConfigDict(extra="forbid")

    instruction: str
    session: ArchmageScribeSession | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Instruction cannot be empty.")

        return value


class ArchmageScribeOutput(BaseModel):
    """Output contract returned after each agent execution."""

    status: Literal[
        "completed",
        "needs_input",
        "unsupported",
        "failed",
    ]
    message: str
    session: ArchmageScribeSession
    skill_name: str | None = None
    interpretation: InterpretationResult | None = None
    required_input: list[str] = Field(default_factory=list)


class ArchmageScribeAgent(Agent):
    """Explore fantasy-world concepts and write canon-aware in-world texts."""

    name = "archmage-scribe"
    description = (
        "Explore and develop fantasy-world concepts, preserve consistency "
        "with a local canon repository, and write in-world fantasy texts."
    )

    SESSION_FIELDS = {
        "initial_idea",
        "concepts",
        "established_definitions",
        "open_questions",
        "contents",
        "canonical_references",
    }

    STOP_WORDS = {
        "para", "com", "uma", "uns", "que", "como", "sobre", "entre",
        "mais", "das", "dos", "por", "pela", "pelo", "nas", "nos",
        "this", "that", "with", "from", "the", "and", "for", "are",
    }

    def __init__(
        self,
        interpreter: Interpreter,
        content_path: Path,
        agent_path: Path | None = None,
    ) -> None:
        self.interpreter = interpreter
        self.content_path = content_path.expanduser().resolve()
        self.agent_path = agent_path or Path(__file__).parent

        self._skills = SkillLoader(
            self.agent_path / "skills"
        ).load_all()

        workflow_path = (
            self.agent_path
            / "workflows"
            / "worldbuilding"
            / "WORKFLOW.md"
        )

        self.workflow = (
            workflow_path.read_text(encoding="utf-8")
            if workflow_path.is_file()
            else ""
        )

    @property
    def skills(self) -> list[Skill]:
        return self._skills

    @property
    def input_schema(self) -> type[ArchmageScribeRequest]:
        return ArchmageScribeRequest

    @property
    def output_schema(self) -> type[ArchmageScribeOutput]:
        return ArchmageScribeOutput

    async def run(
        self,
        input: ArchmageScribeRequest | dict[str, Any],
    ) -> ArchmageScribeOutput:
        request = ArchmageScribeRequest.model_validate(input)
        session = request.session or ArchmageScribeSession()

        session.discussion.append(
            DiscussionMessage(
                role="user",
                content=request.instruction,
            )
        )

        try:
            canon_context, references = self._retrieve_canon(
                request.instruction
            )

            selection = await self.interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_selection_instruction(
                        request.instruction,
                        session,
                        canon_context,
                    ),
                    skills=self._skills,
                )
            )

            if selection.missing_inputs:
                return self._result(
                    "needs_input",
                    selection.message or "Additional information is required.",
                    session,
                    selection.skill_name,
                    selection,
                    selection.missing_inputs,
                )

            if not selection.skill_name:
                return self._result(
                    "unsupported",
                    selection.message or "No suitable skill was identified.",
                    session,
                    interpretation=selection,
                )

            skill = next(
                (
                    item
                    for item in self._skills
                    if item.name == selection.skill_name
                ),
                None,
            )

            if skill is None:
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
                        skill,
                        canon_context,
                        references,
                    ),
                    skills=[skill],
                )
            )

            if execution.missing_inputs:
                return self._result(
                    "needs_input",
                    execution.message or "Additional information is required.",
                    session,
                    skill.name,
                    execution,
                    execution.missing_inputs,
                )

            if (
                execution.skill_name is not None
                and execution.skill_name != skill.name
            ):
                return self._result(
                    "failed",
                    "Interpreter returned an unexpected skill.",
                    session,
                    skill.name,
                    execution,
                )

            self._apply_updates(session, execution.parameters)

            session.canonical_references = list(
                dict.fromkeys(
                    session.canonical_references + references
                )
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
                skill.name,
                execution,
            )

        except Exception as exc:
            session.updated_at = self._now()

            return self._result(
                "failed",
                f"Archmage Scribe execution failed: {exc}",
                session,
            )

    def _retrieve_canon(
        self,
        instruction: str,
    ) -> tuple[str, list[str]]:
        """Retrieve a small set of Portuguese canonical documents."""

        if not self.content_path.is_dir():
            raise FileNotFoundError(
                f"Canon repository not found: {self.content_path}"
            )

        terms = {
            term.lower()
            for term in re.findall(
                r"[\wÀ-ÿ-]{3,}",
                instruction,
            )
            if term.lower() not in self.STOP_WORDS
        }

        candidates = sorted(
            self.content_path.rglob("README.pt-BR.md")
        )

        scored: list[tuple[int, str, str]] = []

        for path in candidates:
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue

            relative = path.relative_to(
                self.content_path
            ).as_posix()

            searchable = f"{relative}\n{content}".lower()

            score = sum(
                searchable.count(term)
                for term in terms
            )

            if relative == "README.pt-BR.md":
                score += 2

            scored.append(
                (score, relative, content)
            )

        scored.sort(
            key=lambda item: (-item[0], item[1])
        )

        selected = [
            item
            for item in scored
            if item[0] > 0
        ][:5]

        if not selected and scored:
            selected = scored[:1]

        excerpts: list[str] = []
        references: list[str] = []

        for _, relative, content in selected:
            references.append(relative)

            excerpts.append(
                f"### Canonical source: {relative}\n"
                f"{content[:16000]}"
            )

        return "\n\n".join(excerpts), references

    def _build_selection_instruction(
        self,
        instruction: str,
        session: ArchmageScribeSession,
        canon_context: str,
    ) -> str:
        return f"""
Select exactly one skill. Do not execute it during this step.
The workflow is iterative; neither skill is a mandatory prerequisite for the other.

Workflow:
{self.workflow}

Current session:
{session.model_dump_json(indent=2)}

Relevant canonical material retrieved from the local repository:
{canon_context or "No relevant canonical document was retrieved."}

User instruction:
{instruction}

Choose idea-explore for developing, debating, or reconciling world concepts.
Choose fantasy-write for drafting an in-world text or narrative.
Do not request information already present in the session or canonical material.
If the request is outside these capabilities, leave skill_name empty.
""".strip()

    def _build_execution_instruction(
        self,
        instruction: str,
        session: ArchmageScribeSession,
        skill: Skill,
        canon_context: str,
        references: list[str],
    ) -> str:
        return f"""
Execute the selected skill according to its instructions.

Selected skill: {skill.name}

Skill instructions:
{skill.instructions}

User instruction:
{instruction}

Current session:
{session.model_dump_json(indent=2)}

Relevant canonical material:
{canon_context or "No relevant canonical document was retrieved."}

Canonical references retrieved:
{references}

Return parameters using only these optional fields:
- initial_idea: string
- concepts: list of new concepts
- established_definitions: list of definitions
- open_questions: list of unresolved questions
- contents: list of objects with title, content, content_type, fictional_author,
  historical_context, canonical_relation, canonical_references

Rules:
1. Treat the local repository as the source of truth for established canon.
2. README.ai.md files may aid discovery but are not authoritative over
   Portuguese canonical documents.
3. Distinguish objective facts of the fictional world from what an in-world
   author knows, believes, infers, or regards as disputed.
4. Never write from an omniscient external perspective when producing an
   in-world document. Respect its fictional author, period, audience, and purpose.
5. Asterion Valerius is the reference voice for scholarly treatises:
   erudite, measured, precise, didactic, and confident without artificial
   pomposity. This voice is not mandatory for legends, chronicles, personal
   accounts, or texts attributed to other authors.
6. Identify canon conflicts; do not silently resolve them or alter established
   canon. Classify new content as consistent, compatible_extension, tension,
   contradiction, or unknown.
7. Do not modify repository files. Return proposed content in the session only.
8. Preserve existing session information; append new list items rather than
   replacing previous items.
9. Do not invent citations to canonical documents. Use only retrieved references.
10. Return only fields that actually require changes.
""".strip()

    def _apply_updates(
        self,
        session: ArchmageScribeSession,
        updates: dict[str, Any],
    ) -> None:
        unexpected = set(updates) - self.SESSION_FIELDS

        if unexpected:
            raise ValueError(
                f"Unexpected execution parameters: {sorted(unexpected)}"
            )

        if "initial_idea" in updates:
            session.initial_idea = updates["initial_idea"]

        for field in (
            "concepts",
            "established_definitions",
            "open_questions",
            "canonical_references",
        ):
            if field in updates:
                current = getattr(session, field)
                additions = updates[field]

                setattr(
                    session,
                    field,
                    list(dict.fromkeys(current + additions)),
                )

        if "contents" in updates:
            new_contents = [
                item
                if isinstance(item, CreatedContent)
                else CreatedContent.model_validate(item)
                for item in updates["contents"]
            ]

            session.contents.extend(new_contents)

        session.updated_at = self._now()

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
        session: ArchmageScribeSession,
        skill_name: str | None = None,
        interpretation: InterpretationResult | None = None,
        required_input: list[str] | None = None,
    ) -> ArchmageScribeOutput:
        return ArchmageScribeOutput(
            status=status,
            message=message,
            session=session,
            skill_name=skill_name,
            interpretation=interpretation,
            required_input=required_input or [],
        )