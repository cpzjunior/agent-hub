
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ValidationError, field_validator

from agent_hub.agents.git_agent.tools.git_cli import (
    GitCliInput,
    GitCliOutput,
    GitCliTool,
)
from agent_hub.core import (
    Agent,
    InterpretationRequest,
    Interpreter,
    Skill,
    SkillLoader,
)


class GitAgentRequest(BaseModel):
    instruction: str
    root_path: Path | None = None
    confirmed: bool = False

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Instruction cannot be empty.")

        return value


class GitAgentOutput(BaseModel):
    status: Literal[
        "completed",
        "needs_input",
        "unsupported",
        "failed",
    ]
    message: str
    result: GitCliOutput | None = None
    required_input: str | None = None


class GitAgent(Agent):
    name = "git-agent"
    description = "Execute Git operations in a repository."
    input_schema = GitAgentRequest
    output_schema = GitAgentOutput

    def __init__(
        self,
        tool: GitCliTool | None = None,
        interpreter: Interpreter | None = None,
    ) -> None:
        self._git_cli_tool = tool or GitCliTool()
        self._interpreter = interpreter

        skills_dir = Path(__file__).parent / "skills"
        self._skills = SkillLoader(skills_dir).load_all()

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills)

    async def run(self, input: Any) -> GitAgentOutput:
        request = GitAgentRequest.model_validate(input)

        if self._interpreter is None:
            return GitAgentOutput(
                status="needs_input",
                message="An interpreter is required to process instructions.",
                required_input="interpreter",
            )

        interpretation = await self._interpreter.interpret(
            InterpretationRequest(
                instruction=request.instruction,
                skills=list(self._skills),
            )
        )

        if interpretation.skill_name != "git-operations":
            return GitAgentOutput(
                status="unsupported",
                message=(
                    interpretation.message
                    or "No available skill matches the request."
                ),
            )

        parameters = dict(interpretation.parameters)

        root_path = request.root_path or parameters.get("root_path")

        if root_path is None:
            return GitAgentOutput(
                status="needs_input",
                message="A repository directory is required.",
                required_input="root_path",
            )

        missing_inputs = [
            item
            for item in interpretation.missing_inputs
            if item != "root_path" or root_path is None
        ]

        if missing_inputs:
            return GitAgentOutput(
                status="needs_input",
                message=(
                    interpretation.message
                    or "Additional information is required."
                ),
                required_input=missing_inputs[0],
            )

        parameters.pop("root_path", None)
        parameters.pop("confirmed", None)

        try:
            execution_input = GitCliInput.model_validate(
                {
                    **parameters,
                    "root_path": root_path,
                    "confirmed": request.confirmed,
                }
            )
        except ValidationError as error:
            return GitAgentOutput(
                status="needs_input",
                message=f"Invalid Git operation parameters: {error}",
                required_input="operation_parameters",
            )

        try:
            result = await self._git_cli_tool.execute(execution_input)
        except ValueError as error:
            return GitAgentOutput(
                status="needs_input",
                message=str(error),
            )

        if not result.success:
            return GitAgentOutput(
                status="failed",
                message=result.stderr or "Git operation failed.",
                result=result,
            )

        return GitAgentOutput(
            status="completed",
            message=result.stdout or "Git operation completed successfully.",
            result=result,
        )
