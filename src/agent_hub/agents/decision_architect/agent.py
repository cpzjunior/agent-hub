from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from agent_hub.agents.decision_architect.models import (
    Decision,
    DecisionEvent,
    DecisionSession,
    EventType,
)
from agent_hub.core import (
    Agent,
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
    Skill,
    SkillLoader,
)


class DecisionArchitectRequest(BaseModel):
    instruction: str
    session: DecisionSession | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Instruction cannot be empty.")
        return value


class DecisionArchitectOutput(BaseModel):
    status: Literal["completed", "needs_input", "unsupported", "failed"]
    message: str
    session: DecisionSession
    skill_name: str | None = None
    interpretation: InterpretationResult | None = None
    required_input: list[str] = Field(default_factory=list)


class DecisionArchitect(Agent):
    """Analyzes and supports decisions through an iterative process."""

    name = "decision-architect"
    description = (
        "Supports decision analysis through an iterative process based "
        "on domain, context, objectives, uncertainties, consequences, "
        "and evolution."
    )

    def __init__(
        self,
        interpreter: Interpreter | None = None,
        agent_path: Path | str | None = None,
    ) -> None:
        self._interpreter = interpreter

        self._agent_path = (
            Path(agent_path).expanduser().resolve()
            if agent_path is not None
            else Path(__file__).parent
        )

        self._skills = {
            skill.name: skill
            for skill in SkillLoader(
                self._agent_path / "skills"
            ).load_all()
        }

        workflow_path = (
            self._agent_path
            / "workflows"
            / "decision-architecture"
            / "WORKFLOW.md"
        )

        if not workflow_path.is_file():
            raise FileNotFoundError(
                f"Decision workflow not found: {workflow_path}"
            )

        self._workflow = workflow_path.read_text(encoding="utf-8")

    @property
    def input_schema(self) -> type[BaseModel]:
        return DecisionArchitectRequest

    @property
    def output_schema(self) -> type[BaseModel]:
        return DecisionArchitectOutput

    @property
    def skills(self) -> tuple[Skill, ...]:
        return tuple(self._skills.values())

    async def run(
        self,
        input: BaseModel | dict[str, Any],
    ) -> DecisionArchitectOutput:
        session = DecisionSession()

        try:
            request = DecisionArchitectRequest.model_validate(input)
            session = request.session or DecisionSession()

            if self._interpreter is None:
                return self._result(
                    "needs_input",
                    "An interpreter is required to execute the agent.",
                    session,
                    required_input=["interpreter"],
                )

            if not self._skills:
                return self._result(
                    "failed",
                    "No decision skills were loaded.",
                    session,
                )

            selection = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_selection_instruction(
                        request,
                        session,
                    ),
                    skills=list(self._skills.values()),
                )
            )

            if selection.missing_inputs:
                return self._result(
                    "needs_input",
                    selection.message or "Additional information is required.",
                    session,
                    required_input=selection.missing_inputs,
                    interpretation=selection,
                )

            skill_name = selection.skill_name

            if skill_name not in self._skills:
                return self._result(
                    "unsupported",
                    selection.message
                    or "No suitable decision skill was selected.",
                    session,
                    interpretation=selection,
                )

            skill = self._skills[skill_name]

            execution = await self._interpreter.interpret(
                InterpretationRequest(
                    instruction=self._build_execution_instruction(
                        request,
                        session,
                        skill,
                    ),
                    skills=[skill],
                )
            )

            if execution.missing_inputs:
                return self._result(
                    "needs_input",
                    execution.message or "Additional information is required.",
                    session,
                    skill_name=skill_name,
                    required_input=execution.missing_inputs,
                    interpretation=execution,
                )

            if execution.skill_name != skill_name:
                return self._result(
                    "unsupported",
                    "The interpreter did not execute the selected skill.",
                    session,
                    skill_name=skill_name,
                    interpretation=execution,
                )

            self._apply_updates(session, execution)

            return self._result(
                "completed",
                execution.message or "Decision analysis updated.",
                session,
                skill_name=skill_name,
                interpretation=execution,
            )

        except (OSError, ValueError) as error:
            return self._result(
                "failed",
                f"Decision analysis failed: {error}",
                session,
            )
        except Exception as error:
            return self._result(
                "failed",
                f"Unexpected decision analysis error: {error}",
                session,
            )

    def _build_selection_instruction(
        self,
        request: DecisionArchitectRequest,
        session: DecisionSession,
    ) -> str:
        return (
            "Select the most relevant decision skill for the user's "
            "current interaction. Follow the workflow instructions. "
            "Select exactly one skill. Do not execute the skill yet. "
            "Consider the existing Decision Model and the conversation "
            "context provided below. If essential user information is "
            "missing, report it instead of inventing information.\n\n"
            f"WORKFLOW:\n{self._workflow}\n\n"
            f"USER INSTRUCTION:\n{request.instruction}\n\n"
            f"CURRENT DECISION MODEL:\n"
            f"{session.decision.model_dump_json(indent=2)}"
        )

    @staticmethod
    def _build_execution_instruction(
        request: DecisionArchitectRequest,
        session: DecisionSession,
        skill: Skill,
    ) -> str:
        return (
            "Execute the selected decision skill according to its "
            "instructions and the Decision Architecture workflow.\n\n"
            "Analyze the user's instruction in the context of the "
            "current Decision Model.\n\n"
            "Return structured parameters using the following contract:\n"
            "- decision_updates: dictionary containing only the "
            "Decision Model fields that must be updated.\n"
            "- event_description: description of the relevant change.\n"
            "- event_type: one of created, updated, information_added, "
            "alternative_added, alternative_selected, status_changed, "
            "reviewed.\n"
            "- event_target: affected Decision Model field.\n"
            "- event_rationale: reason for the change.\n"
            "- event_source: user, external_evidence, or agent_inference.\n\n"
            "Do not include unchanged fields in decision_updates. "
            "Do not invent missing information. Preserve existing "
            "information unless there is a justified update. "
            "If no relevant model change is necessary, return an empty "
            "decision_updates dictionary and explain the result.\n\n"
            f"SELECTED SKILL: {skill.name}\n\n"
            f"USER INSTRUCTION:\n{request.instruction}\n\n"
            f"CURRENT DECISION MODEL:\n"
            f"{session.decision.model_dump_json(indent=2)}"
        )

    @staticmethod
    def _apply_updates(
        session: DecisionSession,
        interpretation: InterpretationResult,
    ) -> None:
        parameters = interpretation.parameters

        updates = parameters.get("decision_updates", {})

        if not isinstance(updates, dict):
            raise ValueError("decision_updates must be a dictionary.")

        if updates:
            current_data = session.decision.model_dump()
            updated_data = {**current_data, **updates}

            session.decision = Decision.model_validate(updated_data)

        event_description = parameters.get("event_description")

        if not isinstance(event_description, str) or not event_description.strip():
            return

        event_type_value = parameters.get(
            "event_type",
            EventType.UPDATED.value,
        )

        event = DecisionEvent(
            event_type=EventType(event_type_value),
            target=parameters.get("event_target"),
            description=event_description,
            rationale=parameters.get("event_rationale"),
            source=parameters.get("event_source", "user"),
        )

        session.record_event(event)

    @staticmethod
    def _result(
        status: Literal["completed", "needs_input", "unsupported", "failed"],
        message: str,
        session: DecisionSession,
        skill_name: str | None = None,
        required_input: list[str] | None = None,
        interpretation: InterpretationResult | None = None,
    ) -> DecisionArchitectOutput:
        return DecisionArchitectOutput(
            status=status,
            message=message,
            session=session,
            skill_name=skill_name,
            required_input=required_input or [],
            interpretation=interpretation,
        )
