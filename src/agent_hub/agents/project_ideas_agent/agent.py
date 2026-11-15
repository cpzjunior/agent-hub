from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from agent_hub.core import (
    Agent,
    InterpretationRequest,
    Interpreter,
    Skill,
    SkillLoader,
)

ProjectCategory = Literal[
    "game-concepts",
    "game-mechanics",
    "non-profit",
    "services",
]
GameConceptVariant = Literal["beginner", "advanced"]


class ProjectIdeasAgentRequest(BaseModel):
    instruction: str
    template_variant: GameConceptVariant | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Instruction cannot be empty.")
        return value


class ProjectIdeasAgentOutput(BaseModel):
    status: Literal["completed", "needs_input", "unsupported", "failed"]
    message: str
    category: ProjectCategory | None = None
    template_variant: GameConceptVariant | None = None
    title: str | None = None
    content_pt_br: str | None = None
    content_en: str | None = None
    reference_path: str | None = None
    required_input: str | None = None
    validation_notes: list[str] = Field(default_factory=list)


class ProjectIdeasAgent(Agent):
    """Generate project idea documents using repository examples as references."""

    name = "project-ideas-agent"
    description = (
        "Creates project idea documents in Brazilian Portuguese and English "
        "using the category-specific structure of the project-ideas repository."
    )

    _REFERENCE_PATHS: dict[str, str] = {
        "game-concepts/beginner": (
            "game-concepts/beginner/"
            "air-hockey-pro-the-path-to-glory/README.pt-BR.md"
        ),
        "game-concepts/advanced": (
            "game-concepts/advanced/"
            "exoskeleton-sports-beyond-human-limits/README.pt-BR.md"
        ),
        "game-mechanics": (
            "game-mechanics/dynamic-rival/README.pt-BR.md"
        ),
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

    _SKILL_TO_CATEGORY: dict[str, ProjectCategory] = {
        "game-concepts": "game-concepts",
        "game-mechanics": "game-mechanics",
        "non-profit": "non-profit",
        "services": "services",
    }

    def __init__(
        self,
        interpreter: Interpreter | None = None,
        project_ideas_path: Path | str | None = None,
    ) -> None:
        self._interpreter = interpreter
        self._project_ideas_path = (
            Path(project_ideas_path).expanduser().resolve()
            if project_ideas_path is not None
            else None
        )

        skills_directory = Path(__file__).parent / "skills"
        shared_skills_directory = (
            Path(__file__).parents[2] / "shared" / "skills"
        )

        agent_skills = SkillLoader(skills_directory).load_all()
        shared_skills = SkillLoader(shared_skills_directory).load_all()
        self._skills = {
            skill.name: skill
            for skill in agent_skills + shared_skills
        }

    @property
    def input_schema(self) -> type[BaseModel]:
        return ProjectIdeasAgentRequest

    @property
    def output_schema(self) -> type[BaseModel]:
        return ProjectIdeasAgentOutput

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills.values())

    async def run(
        self,
        input: BaseModel | dict[str, Any],
    ) -> ProjectIdeasAgentOutput:
        try:
            request = ProjectIdeasAgentRequest.model_validate(input)

            if self._interpreter is None:
                return self._needs_input("interpreter")

            if self._project_ideas_path is None:
                return self._needs_input("project_ideas_path")

            if not self._project_ideas_path.is_dir():
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message=(
                        "Project ideas repository not found: "
                        f"{self._project_ideas_path}"
                    ),
                )

            category_result = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_selection_instruction(request),
                    skills=[
                        self._skills[name]
                        for name in self._SKILL_TO_CATEGORY
                    ],
                )
            )

            if category_result.missing_inputs:
                return ProjectIdeasAgentOutput(
                    status="needs_input",
                    message=(
                        category_result.message
                        or "Additional information is required."
                    ),
                    required_input=", ".join(category_result.missing_inputs),
                )

            skill_name = category_result.skill_name
            if skill_name not in self._SKILL_TO_CATEGORY:
                return ProjectIdeasAgentOutput(
                    status="unsupported",
                    message=(
                        category_result.message
                        or "The request does not match a supported category."
                    ),
                )

            category = self._SKILL_TO_CATEGORY[skill_name]
            variant = request.template_variant

            if category == "game-concepts" and variant is None:
                return ProjectIdeasAgentOutput(
                    status="needs_input",
                    message=(
                        "Game concepts have beginner and advanced formats. "
                        "Specify which format should be used."
                    ),
                    category=category,
                    required_input="template_variant (beginner or advanced)",
                )

            if category != "game-concepts" and variant is not None:
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message=(
                        "The template_variant field is only valid "
                        "for the game-concepts category."
                    ),
                    category=category,
                )

            reference_key = (
                f"game-concepts/{variant}"
                if category == "game-concepts"
                else category
            )
            reference_relative_path = self._REFERENCE_PATHS[reference_key]
            reference_path = self._project_ideas_path / reference_relative_path

            if not reference_path.is_file():
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message=f"Reference document not found: {reference_path}",
                    category=category,
                    template_variant=variant,
                    reference_path=reference_relative_path,
                )

            reference_content = reference_path.read_text(encoding="utf-8")
            generation_result = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_generation_instruction(
                        request=request,
                        category=category,
                        variant=variant,
                        reference_path=reference_relative_path,
                        reference_content=reference_content,
                    ),
                    skills=[self._skills[skill_name]],
                )
            )

            if generation_result.missing_inputs:
                return ProjectIdeasAgentOutput(
                    status="needs_input",
                    message=(
                        generation_result.message
                        or "Additional information is required to write the idea."
                    ),
                    category=category,
                    template_variant=variant,
                    reference_path=reference_relative_path,
                    required_input=", ".join(generation_result.missing_inputs),
                )

            if generation_result.skill_name != skill_name:
                return ProjectIdeasAgentOutput(
                    status="unsupported",
                    message=(
                        "The interpreter did not execute the selected "
                        f"category skill '{skill_name}'."
                    ),
                    category=category,
                    template_variant=variant,
                    reference_path=reference_relative_path,
                )

            content_pt_br = self._required_string(
                generation_result.parameters,
                "content_pt_br",
            )
            title = self._optional_string(
                generation_result.parameters,
                "title",
            )

            if not content_pt_br:
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message=(
                        "The category skill did not return "
                        "the complete Markdown document in Portuguese."
                    ),
                    category=category,
                    template_variant=variant,
                    title=title,
                    reference_path=reference_relative_path,
                )

            translation_skill = self._skills.get("text-translate")
            if translation_skill is None:
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message="Shared skill 'text-translate' was not found.",
                    category=category,
                    template_variant=variant,
                    title=title,
                    content_pt_br=content_pt_br,
                    reference_path=reference_relative_path,
                )

            translation_result = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=(
                        "Translate the complete Markdown document below "
                        "from Brazilian Portuguese to English. Preserve its "
                        "structure, headings, lists, tables, links, code and "
                        "meaning. Do not summarize or add content.\n\n"
                        f"{content_pt_br}"
                    ),
                    skills=[translation_skill],
                )
            )

            if translation_result.missing_inputs:
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message=(
                        translation_result.message
                        or "The translation skill could not complete the document."
                    ),
                    category=category,
                    template_variant=variant,
                    title=title,
                    content_pt_br=content_pt_br,
                    reference_path=reference_relative_path,
                )

            if translation_result.skill_name != "text-translate":
                return ProjectIdeasAgentOutput(
                    status="unsupported",
                    message=(
                        "The interpreter did not execute the shared "
                        "'text-translate' skill."
                    ),
                    category=category,
                    template_variant=variant,
                    title=title,
                    content_pt_br=content_pt_br,
                    reference_path=reference_relative_path,
                )

            content_en = self._required_string(
                translation_result.parameters,
                "translated_text",
            )
            if not content_en:
                return ProjectIdeasAgentOutput(
                    status="failed",
                    message="The translation skill returned an empty document.",
                    category=category,
                    template_variant=variant,
                    title=title,
                    content_pt_br=content_pt_br,
                    reference_path=reference_relative_path,
                )

            return ProjectIdeasAgentOutput(
                status="completed",
                message="Project idea generated in Portuguese and English.",
                category=category,
                template_variant=variant,
                title=title,
                content_pt_br=content_pt_br,
                content_en=content_en,
                reference_path=reference_relative_path,
            )

        except (OSError, ValueError) as error:
            return ProjectIdeasAgentOutput(
                status="failed",
                message=f"Project idea generation failed: {error}",
            )
        except Exception as error:
            return ProjectIdeasAgentOutput(
                status="failed",
                message=f"Project idea generation failed: {error}",
            )

    @staticmethod
    def _build_selection_instruction(
        request: ProjectIdeasAgentRequest,
    ) -> str:
        return (
            "Select exactly one category skill for the user's project idea. "
            "Use the category whose purpose best matches the request. "
            "Available categories are game-concepts, game-mechanics, "
            "non-profit and services. Do not generate the document yet. "
            "If the category is game-concepts, a beginner or advanced "
            "variant is also required; if it cannot be determined from "
            "the user's instruction or request fields, report it as "
            "missing input rather than guessing.\n\n"
            f"User instruction: {request.instruction}\n"
            f"Requested game-concept variant: {request.template_variant or 'not specified'}"
        )

    @staticmethod
    def _build_generation_instruction(
        request: ProjectIdeasAgentRequest,
        category: ProjectCategory,
        variant: GameConceptVariant | None,
        reference_path: str,
        reference_content: str,
    ) -> str:
        return (
            "Generate a new project idea document in Brazilian Portuguese. "
            "Follow the selected category skill and use the supplied "
            "repository document only as a structural and level-of-detail "
            "reference. Do not copy its subject matter or wording. "
            "Preserve the section structure appropriate to the category. "
            "Return the complete Markdown document in the parameter "
            "'content_pt_br' and its title in 'title'.\n\n"
            f"Category: {category}\n"
            f"Variant: {variant or 'not applicable'}\n"
            f"Reference path: {reference_path}\n"
            f"User request: {request.instruction}\n\n"
            "Reference document (Brazilian Portuguese):\n"
            f"{reference_content}"
        )

    @staticmethod
    def _required_string(parameters: dict[str, Any], key: str) -> str | None:
        value = parameters.get(key)
        if not isinstance(value, str):
            return None
        value = value.strip()
        return value or None

    @classmethod
    def _optional_string(
        cls,
        parameters: dict[str, Any],
        key: str,
    ) -> str | None:
        return cls._required_string(parameters, key)

    @staticmethod
    def _needs_input(field: str) -> ProjectIdeasAgentOutput:
        return ProjectIdeasAgentOutput(
            status="needs_input",
            message=f"The following input is required: {field}.",
            required_input=field,
        )
