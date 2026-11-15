
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from agent_hub.agents.git_agent.tools.git_pull.impl.git_pull import (
    GitPullInput,
    GitPullTool,
    RepositoryResult,
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

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Instruction cannot be empty.")

        return value


class GitAgentInput(BaseModel):
    root_path: Path


class GitAgentOutput(BaseModel):
    status: Literal["completed", "needs_input", "unsupported"]
    message: str
    total_repositories: int = 0
    successful_pulls: int = 0
    skipped_repositories: list[RepositoryResult] = Field(default_factory=list)
    failed_repositories: list[RepositoryResult] = Field(default_factory=list)
    required_input: str | None = None


class GitAgent(Agent):
    name = "git-agent"
    description = "Manage Git operations across multiple repositories."

    input_schema = GitAgentRequest
    output_schema = GitAgentOutput

    def __init__(
        self,
        tool: GitPullTool | None = None,
        interpreter: Interpreter | None = None,
    ) -> None:
        self._git_pull_tool = tool or GitPullTool()
        self._interpreter = interpreter

        skills_dir = Path(__file__).parent / "skills"
        self._skills = SkillLoader(skills_dir).load_all()

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills)

    async def run(self, input: Any) -> GitAgentOutput:
        request = GitAgentRequest.model_validate(input)

        root_path = request.root_path

        if self._interpreter is not None:
            interpretation = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=request.instruction,
                    skills=list(self._skills),
                )
            )

            if interpretation.skill_name != "git-pull":
                return GitAgentOutput(
                    status="unsupported",
                    message=(
                        interpretation.message
                        or "No available skill matches the request."
                    ),
                )

            if root_path is None:
                root_path = interpretation.parameters.get("root_path")

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

        if root_path is None:
            return GitAgentOutput(
                status="needs_input",
                message="A root directory is required to execute Git pull.",
                required_input="root_path",
            )

        try:
            execution_input = GitAgentInput(root_path=root_path)
        except ValidationError as error:
            return GitAgentOutput(
                status="needs_input",
                message=f"Invalid root directory: {error}",
                required_input="root_path",
            )

        results = await self._git_pull_tool.execute(
            GitPullInput(root_path=execution_input.root_path)
        )

        successful = [
            result for result in results if result.status == "success"
        ]
        skipped = [
            result for result in results if result.status == "skipped"
        ]
        failed = [
            result for result in results if result.status == "failed"
        ]

        return GitAgentOutput(
            status="completed",
            message=(
                f"Git pull completed. "
                f"{len(successful)} successful, "
                f"{len(skipped)} skipped, "
                f"{len(failed)} failed."
            ),
            total_repositories=len(results),
            successful_pulls=len(successful),
            skipped_repositories=skipped,
            failed_repositories=failed,
        )
