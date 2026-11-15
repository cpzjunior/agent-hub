
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from agent_hub.core import (
    Agent,
    InterpretationRequest,
    Interpreter,
    Skill,
    SkillLoader,
)


class AgentBuilderRequest(BaseModel):
    instruction: str
    project_context: str | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Instruction cannot be empty.")

        return value

    @field_validator("project_context")
    @classmethod
    def validate_project_context(
        cls,
        value: str | None,
    ) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                return None

        return value


class GeneratedArtifact(BaseModel):
    path: str
    content: str
    action: Literal["create", "update"]

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Artifact path cannot be empty.")

        posix_path = PurePosixPath(value)
        windows_path = PureWindowsPath(value)

        if (
            posix_path.is_absolute()
            or windows_path.is_absolute()
            or ".." in posix_path.parts
            or ".." in windows_path.parts
            or windows_path.drive
        ):
            raise ValueError("Artifact path must be relative.")

        return value.replace("\\", "/")


class AgentBuilderOutput(BaseModel):
    status: Literal[
        "proposed",
        "needs_input",
        "unsupported",
        "failed",
    ]
    message: str
    skill_name: str | None = None
    artifacts: list[GeneratedArtifact] = Field(
        default_factory=list,
    )
    tests_relevant: bool | None = None
    tests_rationale: str | None = None
    validation_notes: list[str] = Field(default_factory=list)
    required_input: str | None = None


class AgentBuilder(Agent):
    name = "agent-builder"
    description = (
        "Create and improve agents, skills and tools "
        "within the Agent Hub project."
    )
    input_schema = AgentBuilderRequest
    output_schema = AgentBuilderOutput

    _SUPPORTED_SKILLS = {
        "agent-manage",
        "skill-manage",
        "tool-manage",
    }

    def __init__(
        self,
        interpreter: Interpreter | None = None,
    ) -> None:
        self._interpreter = interpreter

        skills_dir = Path(__file__).parent / "skills"

        self._skills = SkillLoader(
            skills_dir,
        ).load_all()

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills)

    async def run(self, input: Any) -> AgentBuilderOutput:
        request = AgentBuilderRequest.model_validate(input)

        if self._interpreter is None:
            return AgentBuilderOutput(
                status="needs_input",
                message="An interpreter is required.",
                required_input="interpreter",
            )

        instruction = request.instruction

        if request.project_context:
            instruction += (
                "\n\nProject context provided by the user:\n"
                f"{request.project_context}"
            )

        try:
            interpretation = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=instruction,
                    skills=list(self._skills),
                )
            )
        except Exception as error:
            return AgentBuilderOutput(
                status="failed",
                message=f"Interpreter execution failed: {error}",
            )

        skill_name = interpretation.skill_name

        if skill_name not in self._SUPPORTED_SKILLS:
            return AgentBuilderOutput(
                status="unsupported",
                message=(
                    interpretation.message
                    or "No available skill matches the request."
                ),
            )

        if interpretation.missing_inputs:
            return AgentBuilderOutput(
                status="needs_input",
                message=(
                    interpretation.message
                    or "Additional information is required."
                ),
                skill_name=skill_name,
                required_input=interpretation.missing_inputs[0],
            )

        parameters = interpretation.parameters

        try:
            artifacts = [
                GeneratedArtifact.model_validate(item)
                for item in parameters.get("artifacts", [])
            ]

            paths = [artifact.path for artifact in artifacts]

            if len(paths) != len(set(paths)):
                raise ValueError(
                    "Generated artifacts contain duplicate paths."
                )

            return AgentBuilderOutput(
                status="proposed",
                message=(
                    interpretation.message
                    or "Artifacts generated successfully."
                ),
                skill_name=skill_name,
                artifacts=artifacts,
                tests_relevant=parameters.get("tests_relevant"),
                tests_rationale=parameters.get("tests_rationale"),
                validation_notes=parameters.get(
                    "validation_notes",
                    [],
                ),
            )

        except (ValidationError, ValueError, TypeError) as error:
            return AgentBuilderOutput(
                status="failed",
                message=f"Invalid generated artifacts: {error}",
                skill_name=skill_name,
            )
